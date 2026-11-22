#!/usr/bin/env python3
"""Kiểm tra key FIDO qua USB HID: INIT, PING (ngắn + dài) và CTAP2 GetInfo.

Cách dùng:
    pip install -r requirements.txt
    python fido_check.py                 # cần cắm key thật
    python fido_check.py --index 1       # dùng key thứ 2 nếu có nhiều key
    python fido_check.py --self-test     # kiểm tra bằng key giả, không cần phần cứng

Trên Linux cần cài udev rules ở config/70-u2f.rules trước.
Cần Python 3.10 trở lên (dùng cú pháp dict | None).
"""
import os
import sys
from pathlib import Path

try:
    from cborx import cbor_decode
except ImportError:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from cborx import cbor_decode

FIDO_USAGE_PAGE = 0xF1D0
PACKET_SIZE = 64
CID_BROADCAST = 0xFFFFFFFF

CTAPHID_PING = 0x01
CTAPHID_MSG = 0x03
CTAPHID_INIT = 0x06
CTAPHID_CBOR = 0x10
CTAPHID_ERROR = 0x3F

CTAP2_GET_INFO = 0x04

HID_ERRORS = {
    0x01: "lệnh sai",
    0x02: "tham số sai",
    0x03: "độ dài sai",
    0x04: "thứ tự gói sai",
    0x05: "key hết giờ",
    0x06: "kênh bận",
    0x0A: "kênh đang khóa",
    0x0B: "CID sai",
}

CTAP2_STATUS = {
    0x00: "ok",
    0x01: "lệnh CTAP2 sai",
    0x02: "tham số CBOR sai",
    0x03: "độ dài sai",
    0x04: "thứ tự sai",
    0x05: "hết giờ",
    0x06: "kênh bận",
    0x0A: "cần mở khóa",
    0x27: "lệnh chưa hỗ trợ",
}

GETINFO_NAMES = {
    0x01: "versions",
    0x02: "extensions",
    0x03: "aaguid",
    0x04: "options",
    0x05: "maxMsgSize",
    0x06: "pinUvAuthProtocols",
    0x07: "maxCredentialCountInList",
    0x08: "maxCredentialIdLength",
    0x09: "transports",
    0x0A: "algorithms",
    0x0D: "minPINLength",
    0x0E: "firmwareVersion",
}


class CtapHidError(Exception):
    def __init__(self, code: int):
        self.code = code
        super().__init__(f"lỗi CTAPHID 0x{code:02x}: {HID_ERRORS.get(code, 'không rõ')}")


class Ctap2Error(Exception):
    def __init__(self, code: int):
        self.code = code
        super().__init__(f"lỗi CTAP2 0x{code:02x}: {CTAP2_STATUS.get(code, 'không rõ')}")


# CTAPHID: 1 gói đầu 57 byte + tối đa 128 gói nối 59 byte = 7609 byte.
# Mọi kiểm tra biên dùng ValueError (assert mất tác dụng dưới python -O).
MAX_MSG = 7609


def build_init_packet(nonce: bytes) -> bytes:
    """Gói INIT: CID broadcast + CMD + độ dài 8 + nonce 8 byte."""
    if len(nonce) != 8:
        raise ValueError(f"nonce INIT phải đúng 8 byte, nhận {len(nonce)}")
    header = CID_BROADCAST.to_bytes(4, "big") + bytes([CTAPHID_INIT | 0x80]) + (8).to_bytes(2, "big")
    return (header + nonce).ljust(PACKET_SIZE, b"\x00")


def build_ping_packet(cid: int, payload: bytes) -> bytes:
    """Gói PING đơn (payload tối đa 57 byte). Dài hơn thì dùng send_msg."""
    if len(payload) > 57:
        raise ValueError(f"PING đơn chỉ chứa 57 byte, nhận {len(payload)}")
    header = cid.to_bytes(4, "big") + bytes([CTAPHID_PING | 0x80]) + len(payload).to_bytes(2, "big")
    return (header + payload).ljust(PACKET_SIZE, b"\x00")


def fragment(cid: int, cmd: int, data: bytes) -> list[bytes]:
    """Cắt message thành gói mở đầu + gói nối tiếp (chưa có report ID)."""
    if len(data) > MAX_MSG:
        raise ValueError(f"message {len(data)} byte vượt {MAX_MSG} byte chuẩn CTAPHID")
    first = cid.to_bytes(4, "big") + bytes([cmd | 0x80]) + len(data).to_bytes(2, "big") + data[:57]
    packets = [first.ljust(PACKET_SIZE, b"\x00")]
    rest, seq = data[57:], 0
    while rest:
        packets.append((cid.to_bytes(4, "big") + bytes([seq]) + rest[:59]).ljust(PACKET_SIZE, b"\x00"))
        rest, seq = rest[59:], seq + 1
    return packets


def send_msg(dev, cid: int, cmd: int, data: bytes) -> None:
    """Gửi message, tự cắt gói. Mỗi gói ghi kèm report ID 0 ở đầu."""
    for packet in fragment(cid, cmd, data):
        dev.write(b"\x00" + packet)


def _strip_report_id(buf: bytes) -> bytes:
    # hidapi có nền tảng trả kèm report ID (65 byte), có nền tảng không (64 byte).
    if len(buf) == PACKET_SIZE + 1:
        return bytes(buf[1:])
    if len(buf) == PACKET_SIZE:
        return bytes(buf)
    raise ValueError(f"gói HID dài lạ: {len(buf)} byte")


def recv_msg(dev, expected_cid: int | None = None,
             timeout_ms: int = 2000) -> tuple[int, int, bytes]:
    """Đọc message, tự ghép gói nối tiếp. Trả về (cid, cmd, data).

    expected_cid: CID đang chờ (batch INIT là CID broadcast). Gói đầu sai CID
    hoặc đòi message vượt chuẩn đều bị từ chối để chống nhầm kênh/DoS.
    """
    raw = bytes(dev.read(PACKET_SIZE + 1, timeout_ms=timeout_ms))
    if not raw:
        raise TimeoutError("thiết bị không trả lời (hết giờ đọc)")
    pkt = _strip_report_id(raw)
    cid, cmd = int.from_bytes(pkt[0:4], "big"), pkt[4]
    if expected_cid is not None and cid != expected_cid:
        raise ValueError(f"gói đầu sai CID (muốn 0x{expected_cid:08x}, thấy 0x{cid:08x})")
    if (cmd & 0x80) == 0:
        raise ValueError("gói đầu thiếu bit lệnh")
    cmd &= 0x7F
    bcnt = int.from_bytes(pkt[5:7], "big")
    if bcnt > MAX_MSG:
        raise ValueError(f"thiết bị đòi message {bcnt} byte, vượt {MAX_MSG} chuẩn CTAPHID")
    data = bytearray(pkt[7:7 + min(bcnt, PACKET_SIZE - 7)])
    if cmd == CTAPHID_ERROR:
        raise CtapHidError(data[0] if data else 0x00)
    seq = 0
    while len(data) < bcnt:
        raw = bytes(dev.read(PACKET_SIZE + 1, timeout_ms=timeout_ms))
        if not raw:
            raise TimeoutError("gói nối không tới (hết giờ đọc)")
        cont = _strip_report_id(raw)
        if int.from_bytes(cont[0:4], "big") != cid:
            raise ValueError("gói nối sai CID")
        if cont[4] != seq:
            raise ValueError(f"gói nối sai thứ tự (muốn {seq}, thấy {cont[4]})")
        take = min(bcnt - len(data), PACKET_SIZE - 5)
        data += cont[5:5 + take]
        seq += 1
    return cid, cmd, bytes(data)


def parse_init_response(data: bytes) -> dict:
    """Bóc 17 byte trả về của INIT: nonce + CID mới + version + khả năng."""
    if len(data) < 17:
        raise ValueError(f"INIT trả về quá ngắn: {len(data)} byte")
    return {
        "nonce": data[0:8],
        "new_cid": int.from_bytes(data[8:12], "big"),
        "version": data[12],
        "capabilities": data[16],
    }


# Giải/mã CBOR dùng chung từ cborx (có fuzz 3000 ca trong self-test của nó).


def ctap2_get_info(dev, cid: int) -> dict:
    """Gửi authenticatorGetInfo, trả về map đã đặt tên trường."""
    send_msg(dev, cid, CTAPHID_CBOR, bytes([CTAP2_GET_INFO]))
    _, cmd, data = recv_msg(dev, cid)
    if cmd != CTAPHID_CBOR:
        raise ValueError(f"muốn CBOR mà nhận lệnh 0x{cmd:02x}")
    if not data:
        raise ValueError("CBOR trả về rỗng")
    if data[0] != 0:
        raise Ctap2Error(data[0])
    info, rest = cbor_decode(data[1:])
    if rest:
        raise ValueError(f"GetInfo thừa {len(rest)} byte rác đuôi")
    if not isinstance(info, dict):
        raise ValueError("GetInfo không trả về map")
    named = {}
    for key, value in info.items():
        name = GETINFO_NAMES.get(key, f"0x{key:02x}" if isinstance(key, int) else key)
        named[name] = value.hex() if isinstance(value, bytes) and key == 0x03 else value
    return named


def find_fido_devices(hid) -> list:
    return [dev for dev in hid.enumerate() if dev.get("usage_page") == FIDO_USAGE_PAGE]


# --- Key giả trong RAM để tự kiểm tra không cần phần cứng ---

# GetInfo mẫu: versions [U2F_V2, FIDO_2_0], options {rk: true}, maxMsgSize 1024.
CANNED_GETINFO = bytes.fromhex(
    "A30182665532465F5632684649444F5F325F30"
    "04A162726BF5"
    "05190400"
)

NEW_CID = 0xAABBCCDD


class FakeDevice:
    """Giả lập key FIDO: INIT cấp CID mới, PING echo, CBOR trả GetInfo mẫu."""

    def __init__(self, with_report_id: bool = True):
        self.with_report_id = with_report_id
        self.queue: list[bytes] = []
        self.pending = bytearray()
        self.pending_cmd = 0
        self.pending_cid = 0
        self.pending_len = 0

    def write(self, packet: bytes) -> int:
        body = bytes(packet[1:])
        cid = int.from_bytes(body[0:4], "big")
        if body[4] & 0x80:
            self.pending_cid = cid
            self.pending_cmd = body[4] & 0x7F
            self.pending_len = int.from_bytes(body[5:7], "big")
            self.pending = bytearray(body[7:7 + min(self.pending_len, 57)])
        else:
            take = min(max(self.pending_len - len(self.pending), 0), 59)
            self.pending += body[5:5 + take]
        if len(self.pending) >= self.pending_len:
            self._answer(bytes(self.pending))
        return len(packet)

    def _emit(self, cid: int, cmd: int, data: bytes) -> None:
        for packet in fragment(cid, cmd, data):
            self.queue.append((b"\x00" if self.with_report_id else b"") + packet)

    def _answer(self, data: bytes) -> None:
        cmd = self.pending_cmd
        if cmd == CTAPHID_INIT:
            resp = data[:8] + NEW_CID.to_bytes(4, "big") + bytes([2, 0, 0, 0, 0x05])
            self._emit(CID_BROADCAST, CTAPHID_INIT, resp)
        elif cmd == CTAPHID_PING:
            self._emit(self.pending_cid, CTAPHID_PING, data)
        elif cmd == CTAPHID_CBOR and data[:1] == bytes([CTAP2_GET_INFO]):
            self._emit(self.pending_cid, CTAPHID_CBOR, b"\x00" + CANNED_GETINFO)
        else:
            self._emit(self.pending_cid, CTAPHID_ERROR, b"\x01")

    def read(self, max_length: int, timeout_ms: int = 0) -> bytes:
        if not self.queue:
            return b""
        return self.queue.pop(0)[:max_length]


def self_test() -> int:
    # 1. Framing gói đơn.
    nonce = bytes(range(8))
    init = build_init_packet(nonce)
    assert len(init) == PACKET_SIZE
    assert init[0:4] == b"\xff\xff\xff\xff" and init[4] == CTAPHID_INIT | 0x80
    assert init[5:7] == b"\x00\x08" and init[7:15] == nonce
    assert init[15:] == b"\x00" * (PACKET_SIZE - 15)
    ping = build_ping_packet(0x12345678, b"esp32-s3-ping-test")
    assert len(ping) == PACKET_SIZE and ping[4] == CTAPHID_PING | 0x80
    try:
        build_ping_packet(1, bytes(58))
    except ValueError:
        pass
    else:
        raise AssertionError("đáng lẽ phải từ chối PING đơn quá 57 byte")

    # 2. Cắt gói nối: 100 byte thành 1 gói đầu + 1 gói nối, ghép lại đúng.
    parts = fragment(0x01020304, CTAPHID_PING, bytes(range(100)))
    assert len(parts) == 2 and all(len(p) == PACKET_SIZE for p in parts)
    assert parts[0][4] == CTAPHID_PING | 0x80 and parts[0][5:7] == (100).to_bytes(2, "big")
    assert parts[1][0:4] == (0x01020304).to_bytes(4, "big") and parts[1][4] == 0
    assert parts[0][7:] + parts[1][5:5 + 43] == bytes(range(100))

    # 3. Bóc INIT mẫu.
    sample = bytes(range(8)) + (0xDEADBEEF).to_bytes(4, "big") + bytes([2, 1, 0, 3, 0x05])
    parsed = parse_init_response(sample)
    assert parsed["nonce"] == bytes(range(8)) and parsed["new_cid"] == 0xDEADBEEF
    assert parsed["version"] == 2 and parsed["capabilities"] == 0x05

    # 4. CBOR: GetInfo mẫu, kiểu lồng nhau, bool/null và gói cụt.
    info, rest = cbor_decode(CANNED_GETINFO)
    assert rest == b"" and info[1] == ["U2F_V2", "FIDO_2_0"]
    assert info[4] == {"rk": True} and info[5] == 1024
    nested, _ = cbor_decode(bytes.fromhex("A2018202210243626974"))
    assert nested == {1: [2, -2], 2: b"bit"}
    assert cbor_decode(bytes.fromhex("F5"))[0] is True
    assert cbor_decode(bytes.fromhex("F4"))[0] is False
    assert cbor_decode(bytes.fromhex("F6"))[0] is None
    try:
        cbor_decode(bytes.fromhex("1904"))
    except ValueError:
        pass
    else:
        raise AssertionError("đáng lẽ phải từ chối CBOR cụt")

    # 5. Hội thoại đầu-cuối với key giả, cả hai kiểu report ID.
    for with_rid in (True, False):
        dev = FakeDevice(with_report_id=with_rid)
        send_msg(dev, CID_BROADCAST, CTAPHID_INIT, nonce)
        _, cmd, data = recv_msg(dev)
        assert cmd == CTAPHID_INIT
        got = parse_init_response(data)
        assert got["nonce"] == nonce and got["new_cid"] == NEW_CID
        cid = got["new_cid"]
        payload = b"esp32-s3-ping-test"
        send_msg(dev, cid, CTAPHID_PING, payload)
        _, cmd, echo = recv_msg(dev)
        assert cmd == CTAPHID_PING and echo == payload
        long_payload = bytes(range(100))
        send_msg(dev, cid, CTAPHID_PING, long_payload)
        _, cmd, long_echo = recv_msg(dev)
        assert cmd == CTAPHID_PING and long_echo == long_payload
        info = ctap2_get_info(dev, cid)
        assert info["versions"] == ["U2F_V2", "FIDO_2_0"]
        assert info["options"] == {"rk": True} and info["maxMsgSize"] == 1024
        send_msg(dev, cid, 0x3E, b"")
        try:
            recv_msg(dev)
        except CtapHidError as exc:
            assert exc.code == 0x01
        else:
            raise AssertionError("đáng lẽ lệnh lạ phải báo lỗi")
        try:
            recv_msg(FakeDevice())
        except TimeoutError:
            pass
        else:
            raise AssertionError("đáng lẽ đọc rỗng phải hết giờ")

    # 6. CBOR độc hại, CID sai, message vượt chuẩn, nonce sai, rác đuôi.
    for bad in [bytes.fromhex("A1810101"),  # key là mảng
                bytes.fromhex("A1A101410101"),  # key là map
                b"\x81" * 100,  # lồng sâu
                bytes.fromhex("4200"),  # bytes cụt
                bytes.fromhex("62A1"),  # text cụt
                bytes.fromhex("62FFFF")]:  # text sai UTF-8
        try:
            cbor_decode(bad)
        except ValueError:
            pass
        else:
            raise AssertionError(f"đáng lẽ phải từ chối CBOR: {bad.hex()[:40]}")
    for fn, exc_tag in [(lambda: fragment(1, CTAPHID_PING, bytes(MAX_MSG + 1)),
                         "message vượt chuẩn"),
                        (lambda: build_init_packet(bytes(7)), "nonce sai 8 byte")]:
        try:
            fn()
        except ValueError:
            pass
        else:
            raise AssertionError(f"đáng lẽ phải từ chối {exc_tag}")
    dev = FakeDevice()
    send_msg(dev, CID_BROADCAST, CTAPHID_INIT, nonce)
    try:
        recv_msg(dev, 0x12345678)
    except ValueError as exc:
        assert "sai CID" in str(exc)
    else:
        raise AssertionError("đáng lẽ phải từ chối CID sai")

    class TrailingFake(FakeDevice):
        def _answer(self, data: bytes) -> None:
            if self.pending_cmd == CTAPHID_CBOR:
                self._emit(self.pending_cid, CTAPHID_CBOR, b"\x00" + CANNED_GETINFO + b"\x00")
            else:
                super()._answer(data)

    dev2 = TrailingFake()
    send_msg(dev2, CID_BROADCAST, CTAPHID_INIT, nonce)
    recv_msg(dev2, CID_BROADCAST)
    try:
        ctap2_get_info(dev2, NEW_CID)
    except ValueError as exc:
        assert "rác đuôi" in str(exc)
    else:
        raise AssertionError("đáng lẽ phải từ chối rác đuôi CBOR")
    assert main(["--index", "-1"]) == 2, "--index âm phải báo sai dùng"

    print("self-test ok: framing, gói nối, CBOR, GetInfo và hội thoại đầu-cuối đều đúng.")
    return 0


def main(argv: list[str]) -> int:
    index = 0
    if "--index" in argv:
        try:
            index = int(argv[argv.index("--index") + 1])
            if index < 0:
                raise ValueError("số thứ tự key không được âm")
        except (IndexError, ValueError):
            print("--index cần kèm số thứ tự key (0, 1, ...).")
            return 2
    try:
        import hid
    except ImportError:
        print("Thiếu thư viện hid. Chạy: pip install -r requirements.txt")
        return 2

    found = find_fido_devices(hid)
    if not found:
        print("Không thấy thiết bị HID usage page 0xF1D0.")
        print("Kiểm tra: cắm đúng cổng USB OTG native, cáp dữ liệu, udev rules trên Linux.")
        return 1
    if index >= len(found):
        print(f"Chỉ thấy {len(found)} key, không có key số {index}.")
        return 2
    for i, dev in enumerate(found):
        mark = ">>" if i == index else "  "
        print(f"{mark} [{i}] {dev.get('manufacturer_string')} {dev.get('product_string')}")
    dev_info = found[index]

    device = hid.device()
    try:
        device.open_path(dev_info["path"])
    except OSError as exc:
        print(f"Không mở được key: {exc}")
        return 1
    device.set_nonblocking(False)

    try:
        nonce = os.urandom(8)
        send_msg(device, CID_BROADCAST, CTAPHID_INIT, nonce)
        _, cmd, data = recv_msg(device, CID_BROADCAST)
        if cmd != CTAPHID_INIT:
            print(f"INIT trả về lệnh lạ 0x{cmd:02x}.")
            return 1
        ans = parse_init_response(data)
        if ans["nonce"] != nonce:
            print("INIT sai nonce, key hoặc đường truyền có vấn đề.")
            return 1
        cid = ans["new_cid"]
        print(f"INIT ok. CID mới: 0x{cid:08x}, giao thức HID v{ans['version']}.")

        payload = b"esp32-s3-ping-test"
        send_msg(device, cid, CTAPHID_PING, payload)
        _, cmd, echo = recv_msg(device, cid)
        if cmd != CTAPHID_PING or echo != payload:
            print(f"PING ngắn không echo đúng: {echo.hex()}")
            return 1
        print("PING ngắn ok.")

        long_payload = os.urandom(100)
        send_msg(device, cid, CTAPHID_PING, long_payload)
        _, cmd, long_echo = recv_msg(device, cid)
        if cmd != CTAPHID_PING or long_echo != long_payload:
            print("PING dài 100 byte (gói nối) không echo đúng.")
            return 1
        print("PING dài ok. Đường gói nối tiếp hoạt động.")

        info = ctap2_get_info(device, cid)
        print(f"CTAP2 GetInfo ok: versions={info.get('versions')}, "
              f"options={info.get('options')}, maxMsgSize={info.get('maxMsgSize')}.")
        print("Key trả lời đúng cả ba tầng: HID, PING nối gói và CTAP2.")
    except (CtapHidError, Ctap2Error, ValueError, TimeoutError) as exc:
        print(f"Kiểm tra hỏng: {exc}")
        if sys.platform.startswith("linux"):
            print("Trên Linux hãy kiểm tra udev rules và rút cắm lại key.")
        return 1
    except OSError as exc:
        print(f"Lỗi HID: {exc}")
        return 1
    finally:
        device.close()
    return 0


if __name__ == "__main__":
    if "--self-test" in sys.argv or "-t" in sys.argv:
        sys.exit(self_test())
    sys.exit(main(sys.argv[1:]))
