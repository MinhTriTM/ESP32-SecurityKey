#!/usr/bin/env python3
"""Tool quản lý key hợp nhất (hiện thực U036).

Gộp các thao tác rời rạc trên key thật thành một cửa duy nhất:
    list      liệt kê key FIDO đang cắm (không chạm vào key)
    status    INIT + CTAP2 GetInfo, in tóm tắt tình trạng key
    attest    thông tin định danh phục vụ provisioning attestation (U009)
    provision danh mục khởi tạo key mới + ghi sổ theo dõi
    reset     authenticatorReset CÓ KIỂM SOÁT (xóa trắng key, cần 2 lớp xác nhận)
    doctor    kiểm tra môi trường PC (lib, udev, manifest firmware web)

Mọi lệnh gắn phần cứng đều chỉ đọc, trừ reset (ghi chú cảnh báo riêng).
Cần Python 3.10 trở lên. Lệnh list/status/attest/reset cần thư viện hid.
"""
from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import secureio  # noqa: E402
import web_firmware  # noqa: E402
from fido_check import (  # noqa: E402
    CID_BROADCAST,
    CTAPHID_CBOR,
    CTAPHID_INIT,
    Ctap2Error,
    CtapHidError,
    FakeDevice,
    ctap2_get_info,
    find_fido_devices,
    parse_init_response,
    recv_msg,
    send_msg,
)

CTAP2_RESET = 0x07
MAC_RE = re.compile(r"^([0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}$")
KEYS_MD = Path(__file__).resolve().parent.parent / "hardware" / "keys.md"


def _load_hid():
    try:
        import hid  # type: ignore[import-not-found]
    except ImportError:
        print("Thiếu thư viện hid. Chạy: pip install -r requirements.txt")
        raise SystemExit(2)
    return hid


def _pick_device(hid, index: int):
    found = find_fido_devices(hid)
    if not found:
        print("Không thấy key FIDO nào (usage page 0xF1D0).")
        raise SystemExit(1)
    if index < 0 or index >= len(found):
        print(f"Chỉ thấy {len(found)} key, không có key số {index}.")
        raise SystemExit(2)
    return found[index]


def _open_path(hid, dev_info):
    device = hid.device()
    try:
        device.open_path(dev_info["path"])
    except OSError as exc:
        print(f"Không mở được key: {exc}")
        raise SystemExit(1)
    device.set_nonblocking(False)
    return device


def cmd_list(_args: argparse.Namespace) -> int:
    hid = _load_hid()
    found = find_fido_devices(hid)
    if not found:
        print("Không thấy key FIDO nào.")
        return 1
    for i, dev in enumerate(found):
        print(f"[{i}] vid=0x{dev.get('vendor_id', 0):04x} "
              f"pid=0x{dev.get('product_id', 0):04x} "
              f"serial={dev.get('serial_number') or '-'} "
              f"{dev.get('manufacturer_string')} {dev.get('product_string')}")
    return 0


def _init_and_info(device) -> tuple[int, dict]:
    """INIT lấy CID mới rồi GetInfo. Ném CtapHidError/Ctap2Error/ValueError."""
    nonce = os.urandom(8)
    send_msg(device, CID_BROADCAST, CTAPHID_INIT, nonce)
    _, cmd, data = recv_msg(device, CID_BROADCAST)
    if cmd != CTAPHID_INIT:
        raise ValueError(f"INIT trả về lệnh lạ 0x{cmd:02x}")
    ans = parse_init_response(data)
    if ans["nonce"] != nonce:
        raise ValueError("INIT sai nonce")
    cid = ans["new_cid"]
    return cid, ctap2_get_info(device, cid)


def cmd_status(args: argparse.Namespace) -> int:
    hid = _load_hid()
    dev_info = _pick_device(hid, args.index)
    device = _open_path(hid, dev_info)
    try:
        cid, info = _init_and_info(device)
    except (CtapHidError, Ctap2Error, ValueError, TimeoutError, OSError) as exc:
        print(f"Đọc key hỏng: {exc}")
        return 1
    finally:
        device.close()
    opts = info.get("options", {})
    print(f"CID: 0x{cid:08x}")
    print(f"versions: {info.get('versions')}")
    print(f"extensions: {info.get('extensions')}")
    print(f"aaguid: {info.get('aaguid')}")
    print(f"options: {opts}")
    print(f"PIN đã đặt: {'có' if opts.get('clientPin') else 'chưa/không rõ'}")
    print(f"maxMsgSize: {info.get('maxMsgSize')}")
    print(f"firmware: {info.get('firmwareVersion')}")
    return 0


def cmd_attest(args: argparse.Namespace) -> int:
    """In định danh phục vụ provisioning attestation riêng (U009)."""
    hid = _load_hid()
    dev_info = _pick_device(hid, args.index)
    device = _open_path(hid, dev_info)
    try:
        _, info = _init_and_info(device)
    except (CtapHidError, Ctap2Error, ValueError, TimeoutError, OSError) as exc:
        print(f"Đọc key hỏng: {exc}")
        return 1
    finally:
        device.close()
    print(f"aaguid: {info.get('aaguid')}")
    print(f"versions: {info.get('versions')}")
    print("Ghi chú U009: CTAP không cho đọc chứng chỉ attestation qua GetInfo.")
    print("Muốn key riêng không lẫn với bản mẫu pico-fido thì làm provisioning")
    print("offline (AAGUID + cert batch của bạn) lúc build firmware, rồi đối")
    print("chiếu AAGUID trên đây với batch đã ký.")
    return 0


def _ghi_so(path: Path, name: str, mac: str, date: str, commit: str) -> str:
    """Điền MAC/ngày/commit vào hàng `name` của sổ keys.md. Trả về mô tả.

    Chỉ điền ô trống; MAC đã ghi khác thì từ chối (không ghi đè lén).
    Chưa có hàng thì thêm hàng mới trước mục ## đầu tiên.
    """
    if not MAC_RE.match(mac):
        raise ValueError(f"MAC sai định dạng (cần XX:XX:XX:XX:XX:XX): {mac}")
    lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
    for i, line in enumerate(lines):
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) >= 6 and cells[0] == name:
            if cells[1] and cells[1] != mac:
                raise ValueError(f"{name} đã ghi MAC {cells[1]}, không ghi đè")
            cells[1] = mac
            cells[2] = cells[2] or date
            cells[3] = cells[3] or commit
            lines[i] = "| " + " | ".join(cells) + " |\n"
            secureio.write_file(path, "".join(lines))
            return f"đã điền {name} trong sổ"
    row = f"| {name} | {mac} | {date} | {commit} | | |\n"
    at = next((i for i, line in enumerate(lines) if line.startswith("## ")), len(lines))
    lines.insert(at, row)
    secureio.write_file(path, "".join(lines))
    return f"đã thêm hàng {name} vào sổ"


def cmd_provision(args: argparse.Namespace) -> int:
    from datetime import date as _date

    date = args.date or _date.today().isoformat()
    if args.check:
        try:
            import hid  # type: ignore[import-not-found]
        except ImportError:
            print("CẢNH BÁO: thiếu thư viện hid, bỏ qua kiểm tra phần cứng.")
        else:
            found = find_fido_devices(hid)
            if not found:
                print("CẢNH BÁO: không thấy key nào cắm, vẫn ghi sổ theo MAC bạn đưa.")
            else:
                print(f"Thấy {len(found)} key đang cắm, kiểm tra GetInfo key đầu...")
                device = _open_path(hid, found[0])
                try:
                    _, info = _init_and_info(device)
                    print(f"GetInfo ok: {info.get('versions')}")
                except (CtapHidError, Ctap2Error, ValueError, TimeoutError, OSError) as exc:
                    print(f"CẢNH BÁO: key không trả lời ({exc}), vẫn ghi sổ.")
                finally:
                    device.close()
    try:
        note = _ghi_so(KEYS_MD, args.name, args.mac, date, args.commit or "")
    except (OSError, ValueError) as exc:
        print(f"Không ghi được sổ: {exc}")
        return 1
    print(f"{note}: {KEYS_MD}")
    print("Nhớ: MAC chỉ để định danh, PIN nhớ trong đầu, mã khôi phục in giấy.")
    return 0


def _do_reset(device, timeout_ms: int = 30000) -> None:
    """Gửi authenticatorReset (0x07, không tham số). Key phải vừa cắm lại."""
    nonce = os.urandom(8)
    send_msg(device, CID_BROADCAST, CTAPHID_INIT, nonce)
    _, cmd, data = recv_msg(device, CID_BROADCAST)
    if cmd != CTAPHID_INIT:
        raise ValueError(f"INIT trả về lệnh lạ 0x{cmd:02x}")
    cid = parse_init_response(data)["new_cid"]
    send_msg(device, cid, CTAPHID_CBOR, bytes([CTAP2_RESET]))
    _, cmd2, resp = recv_msg(device, cid, timeout_ms)
    if cmd2 != CTAPHID_CBOR:
        raise ValueError(f"reset trả về lệnh lạ 0x{cmd2:02x}")
    if not resp:
        raise ValueError("reset trả về rỗng")
    if resp[0] != 0:
        raise Ctap2Error(resp[0])


def cmd_reset(args: argparse.Namespace) -> int:
    if not args.yes or args.confirm != "RESET":
        print("reset cần ĐỦ 2 điều kiện: --yes và --confirm RESET (gõ chữ RESET hoa).")
        print("Lệnh này XÓA TRẮNG mọi credential trên key, không hoàn tác được.")
        return 2
    print("BƯỚC 1: rút key ra, CẮM LẠI, rồi nhấn Enter NGAY (vài giây sau khi cắm).")
    print("BƯỚC 2: khi LED báo thì CHẠM nút xác nhận trên key.")
    try:
        input("Nhấn Enter khi đã cắm lại key (Ctrl+C để hủy): ")
    except (KeyboardInterrupt, EOFError):
        print("\nĐã hủy.")
        return 1
    hid = _load_hid()
    dev_info = _pick_device(hid, args.index)
    device = _open_path(hid, dev_info)
    try:
        _do_reset(device)
    except Ctap2Error as exc:
        print(f"Key từ chối reset: {exc}")
        print("Thường do quá thời gian sau khi cắm lại — rút cắm lại rồi chạy ngay.")
        return 1
    except (CtapHidError, ValueError, TimeoutError, OSError) as exc:
        print(f"Reset hỏng: {exc}")
        return 1
    finally:
        device.close()
    print("Đã reset trắng key. Đăng ký lại key này trên mọi dịch vụ.")
    return 0


def cmd_doctor(_args: argparse.Namespace) -> int:
    ok = True
    py_ok = sys.version_info >= (3, 10)
    print(f"Python {sys.version.split()[0]}: {'ok' if py_ok else 'CẦN >= 3.10'}")
    ok = ok and py_ok
    try:
        import hid  # noqa: F401  # type: ignore[import-not-found]
        print("thư viện hid: ok")
    except ImportError:
        print("thư viện hid: THIẾU (pip install -r requirements.txt)")
        ok = False
    if sys.platform.startswith("linux"):
        print("Linux: kiểm tra tay udev rules config/70-u2f.rules đã cài vào /etc/udev.")
    ok = ok and web_firmware.verify_manifest() == 0
    print("doctor: " + ("ĐẠT" if ok else "CÓ MỤC HỎNG (xem trên)"))
    return 0 if ok else 1


CTAP2_CLIENT_PIN = 0x06
PIN_SUB_GET_RETRIES = 0x01


def _get_pin_retries(device, cid: int, proto: int) -> dict:
    """Hỏi số lần thử PIN còn lại (clientPIN getRetries, không cần xác thực)."""
    from cborx import cbor_decode, cbor_encode

    send_msg(device, cid, CTAPHID_CBOR,
             bytes([CTAP2_CLIENT_PIN]) + cbor_encode({1: proto, 2: PIN_SUB_GET_RETRIES}))
    _, cmd, resp = recv_msg(device, cid)
    if cmd != CTAPHID_CBOR:
        raise ValueError(f"muốn CBOR mà nhận lệnh 0x{cmd:02x}")
    if not resp:
        raise ValueError("clientPIN trả về rỗng")
    if resp[0] != 0:
        raise Ctap2Error(resp[0])
    info, rest = cbor_decode(resp[1:])
    if rest:
        raise ValueError(f"clientPIN thừa {len(rest)} byte rác đuôi")
    if not isinstance(info, dict):
        raise ValueError("clientPIN không trả về map")
    return info


def cmd_pin_retries(args: argparse.Namespace) -> int:
    hid = _load_hid()
    dev_info = _pick_device(hid, args.index)
    device = _open_path(hid, dev_info)
    try:
        cid, info = _init_and_info(device)
        opts = info.get("options", {})
        if not opts.get("clientPin"):
            print("Key không báo hỗ trợ PIN (options.clientPin vắng).")
            return 1
        protos = info.get("pinUvAuthProtocols") or [1]
        data = _get_pin_retries(device, cid, protos[0])
    except (CtapHidError, Ctap2Error, ValueError, TimeoutError, OSError) as exc:
        print(f"Đọc key hỏng: {exc}")
        return 1
    finally:
        device.close()
    print(f"protocol: {protos[0]}")
    print(f"số lần thử PIN còn lại: {data.get(3, '?')}")
    if 4 in data:
        print(f"powerCycleState: {data[4]}")
    return 0


def cmd_backup_check(args: argparse.Namespace) -> int:
    """Kiểm tra bộ sao lưu: share đồng bộ, két đúng định dạng, cụm checksum ok."""
    from mnemonic import load_wordlist, mnemonic_to_entropy
    from split_secret import parse_share
    from vault import MAGIC as VAULT_MAGIC
    from vault import NONCE_LEN, SALT_LEN

    if not (args.shares or args.vault or args.mnemonic_file):
        print("backup-check cần ít nhất một trong: --shares, --vault, --mnemonic-file.")
        return 2
    fail = 0
    if args.shares:
        try:
            parsed = [parse_share(Path(s).read_text(encoding="utf-8")) for s in args.shares]
        except (OSError, ValueError, UnicodeDecodeError) as exc:
            print(f"share HỎNG: {exc}")
            fail = 1
        else:
            heads = {(n, k, len(y)) for n, k, _, y in parsed}
            xs = [x for _, _, x, _ in parsed]
            if len(heads) != 1 or len(set(xs)) != len(xs):
                print("share HỎNG: lẫn lộn nhiều lần chia hoặc trùng chỉ số.")
                fail = 1
            else:
                n, k, _ = heads.pop()
                if len(parsed) < k:
                    print(f"share THIẾU: có {len(parsed)}, cần ít nhất {k} trong {n}.")
                    fail = 1
                else:
                    print(f"share ok: {len(parsed)}/{n} file, cần {k}, cùng một lần chia.")
    if args.vault:
        try:
            blob = secureio.read_capped(args.vault)
        except (OSError, ValueError) as exc:
            print(f"két HỎNG: {exc}")
            fail = 1
        else:
            head = len(VAULT_MAGIC) + SALT_LEN + NONCE_LEN
            if blob[:len(VAULT_MAGIC)] != VAULT_MAGIC or len(blob) <= head:
                print("két HỎNG: sai magic hoặc cụt (chưa mở, không cần mật khẩu).")
                fail = 1
            else:
                print(f"két ok: đúng định dạng, {len(blob)} byte (chưa mở).")
    if args.mnemonic_file:
        try:
            words = load_wordlist()
            ent = mnemonic_to_entropy(Path(args.mnemonic_file).read_text(encoding="utf-8"), words)
        except (OSError, ValueError, UnicodeDecodeError) as exc:
            print(f"cụm từ HỎNG: {exc}")
            fail = 1
        else:
            print(f"cụm từ ok: checksum đúng, entropy {len(ent)} byte.")
    print("backup-check: " + ("ĐẠT" if not fail else "CÓ MỤC HỎNG"))
    return 1 if fail else 0


def self_test() -> int:
    # 1. Định dạng MAC.
    assert MAC_RE.match("AA:BB:CC:DD:EE:FF")
    assert MAC_RE.match("aa:bb:cc:dd:ee:00")
    for bad in ["", "AA:BB:CC", "GG:BB:CC:DD:EE:FF", "AA-BB-CC-DD-EE-FF",
                "aa:bb:cc:dd:ee:ff:00", "AA:BB:CC:DD:EE:FF "]:
        assert not MAC_RE.match(bad), f"đáng lẽ từ chối MAC: {bad}"
    # 2. Ghi sổ vào file tạm: điền hàng có sẵn, thêm hàng mới, không ghi đè.
    import tempfile

    with tempfile.TemporaryDirectory() as tmp:
        p = Path(tmp) / "keys.md"
        p.write_text("| Tên key | MAC | Ngày | Commit | Dịch vụ | Ghi chú |\n"
                     "|---|---|---|---|---|---|\n"
                     "| key-01 | | | | | chính |\n\n## Quy tắc\n",
                     encoding="utf-8")
        assert "điền" in _ghi_so(p, "key-01", "AA:BB:CC:DD:EE:01", "2026-11-22", "abc")
        text = p.read_text(encoding="utf-8")
        assert "AA:BB:CC:DD:EE:01" in text and "2026-11-22" in text
        try:
            _ghi_so(p, "key-01", "AA:BB:CC:DD:EE:02", "2026-11-22", "")
        except ValueError:
            pass
        else:
            raise AssertionError("đáng lẽ không ghi đè MAC khác")
        assert "thêm" in _ghi_so(p, "key-09", "AA:BB:CC:DD:EE:09", "2026-11-22", "")
        text2 = p.read_text(encoding="utf-8")
        assert text2.index("key-09") < text2.index("## Quy tắc")
    # 3. reset thiếu xác nhận bị chặn trước khi chạm phần cứng.
    assert cmd_reset(argparse.Namespace(yes=False, confirm="", index=0)) == 2
    assert cmd_reset(argparse.Namespace(yes=True, confirm="reset", index=0)) == 2
    # 4. Giao thức reset trên key giả: thành công và thất bại.
    class ResetFake(FakeDevice):
        def _answer(self, data: bytes) -> None:
            if self.pending_cmd == CTAPHID_CBOR and data[:1] == bytes([CTAP2_RESET]):
                self._emit(self.pending_cid, CTAPHID_CBOR, b"\x00")
            else:
                super()._answer(data)

    _do_reset(ResetFake())
    try:
        _do_reset(FakeDevice())
    except CtapHidError:
        pass
    else:
        raise AssertionError("đáng lẽ reset trên key lạ phải hỏng")
    # 5. INIT + GetInfo trên key giả.
    from fido_check import NEW_CID

    cid, info = _init_and_info(FakeDevice())
    assert cid == NEW_CID and info["versions"] == ["U2F_V2", "FIDO_2_0"]
    # 6. getRetries trên key giả.
    from cborx import cbor_encode

    class PinFake(FakeDevice):
        def _answer(self, data: bytes) -> None:
            if self.pending_cmd == CTAPHID_CBOR and data[:1] == bytes([CTAP2_CLIENT_PIN]):
                self._emit(self.pending_cid, CTAPHID_CBOR, b"\x00" + cbor_encode({3: 8}))
            else:
                super()._answer(data)

    dev = PinFake()
    send_msg(dev, CID_BROADCAST, CTAPHID_INIT, b"12345678")
    _, _, init_data = recv_msg(dev, CID_BROADCAST)
    cid2 = parse_init_response(init_data)["new_cid"]
    assert _get_pin_retries(dev, cid2, 1) == {3: 8}
    # 7. backup-check trên bộ sao lưu giả trong thư mục tạm.
    from mnemonic import entropy_to_mnemonic, load_wordlist
    from split_secret import format_share, split
    from vault import encrypt_bytes

    words = load_wordlist()
    with tempfile.TemporaryDirectory() as tmp:
        d = Path(tmp)
        shares = split(b"bi-mat-16-byte!!", 3, 2)
        paths = []
        for x, y in shares:
            p = d / f"s{x}.txt"
            p.write_text(format_share(3, 2, x, y), encoding="utf-8")
            paths.append(str(p))
        (d / "ket.bin").write_bytes(encrypt_bytes(b"du-lieu", b"mat-khau"))
        (d / "cum.txt").write_text(entropy_to_mnemonic(bytes(16), words), encoding="utf-8")
        full = argparse.Namespace(shares=paths, vault=str(d / "ket.bin"),
                                  mnemonic_file=str(d / "cum.txt"))
        assert cmd_backup_check(full) == 0
        thieu = argparse.Namespace(shares=paths[:1], vault=None, mnemonic_file=None)
        assert cmd_backup_check(thieu) == 1
        (d / "ket-hong.bin").write_bytes(b"RAC")
        hong = argparse.Namespace(shares=[], vault=str(d / "ket-hong.bin"), mnemonic_file=None)
        assert cmd_backup_check(hong) == 1
        trong = argparse.Namespace(shares=[], vault=None, mnemonic_file=None)
        assert cmd_backup_check(trong) == 2
    print("self-test ok: MAC, ghi sổ, chặn reset thiếu xác nhận, giao thức key giả.")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Quản lý key FIDO hợp nhất.")
    ap.add_argument("-t", "--self-test", action="store_true", help="tự kiểm tra offline")
    sub = ap.add_subparsers(dest="cmd")
    sub.add_parser("list", help="liệt kê key đang cắm")
    p_status = sub.add_parser("status", help="INIT + GetInfo tóm tắt tình trạng key")
    p_status.add_argument("--index", type=int, default=0)
    p_attest = sub.add_parser("attest", help="định danh phục vụ provisioning attestation")
    p_attest.add_argument("--index", type=int, default=0)
    p_prov = sub.add_parser("provision", help="ghi sổ key mới (+ kiểm tra phần cứng)")
    p_prov.add_argument("--name", required=True, help="tên key, ví dụ key-01")
    p_prov.add_argument("--mac", required=True, help="MAC từ log hwtest, XX:XX:XX:XX:XX:XX")
    p_prov.add_argument("--date", default="", help="ngày flash (mặc định hôm nay)")
    p_prov.add_argument("--commit", default="", help="commit pico-fido đã flash")
    p_prov.add_argument("--check", action=argparse.BooleanOptionalAction, default=True,
                        help="kiểm tra key đang cắm (tắt bằng --no-check)")
    p_reset = sub.add_parser("reset", help="XÓA TRẮNG key (2 lớp xác nhận)")
    p_reset.add_argument("--index", type=int, default=0)
    p_reset.add_argument("--yes", action="store_true")
    p_reset.add_argument("--confirm", default="")
    p_pin = sub.add_parser("pin-retries", help="xem số lần thử PIN còn lại")
    p_pin.add_argument("--index", type=int, default=0)
    p_bak = sub.add_parser("backup-check", help="kiểm tra bộ sao lưu (share/két/cụm từ)")
    p_bak.add_argument("--shares", nargs="*", default=[], help="file share Shamir")
    p_bak.add_argument("--vault", default=None, help="file két .bin (chỉ kiểm định dạng)")
    p_bak.add_argument("--mnemonic-file", default=None, help="file chứa cụm từ")
    sub.add_parser("doctor", help="kiểm tra môi trường PC")
    args = ap.parse_args(argv)
    if args.self_test:
        return self_test()
    if args.cmd == "list":
        return cmd_list(args)
    if args.cmd == "status":
        return cmd_status(args)
    if args.cmd == "attest":
        return cmd_attest(args)
    if args.cmd == "provision":
        return cmd_provision(args)
    if args.cmd == "reset":
        return cmd_reset(args)
    if args.cmd == "pin-retries":
        return cmd_pin_retries(args)
    if args.cmd == "backup-check":
        return cmd_backup_check(args)
    if args.cmd == "doctor":
        return cmd_doctor(args)
    ap.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main())
