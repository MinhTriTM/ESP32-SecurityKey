#!/usr/bin/env python3
"""Kiểm tra echo HID của sketch hwtest (vendor page 0xFF00, report ID 1).

Gửi 60 byte ngẫu nhiên, đối chiếu từng byte trả về. Chạy sau khi nạp hwtest
ở chế độ USB-OTG và cắm cổng USB native.

Cách dùng:
    pip install -r requirements.txt
    python hid_echo.py
    python hid_echo.py --self-test   # chỉ kiểm tra đóng gói report

Cần Python 3.10 trở lên.
"""
import argparse
import os
import sys

ECHO_USAGE_PAGE = 0xFF00
REPORT_ID = 0  # Descriptor không đánh số report (giống CTAP HID)
REPORT_LEN = 64
PAYLOAD_LEN = 60


def build_report(payload: bytes) -> bytes:
    """Report gửi đi: byte đầu là report ID (0 = không đánh số) + 64 byte dữ liệu."""
    if len(payload) > REPORT_LEN:
        raise ValueError(f"payload tối đa {REPORT_LEN} byte, nhận {len(payload)}")
    return bytes([REPORT_ID]) + payload.ljust(REPORT_LEN, b"\x00")


def self_test() -> int:
    report = build_report(b"abc")
    assert len(report) == REPORT_LEN + 1 and report[0] == REPORT_ID
    assert report[1:4] == b"abc" and report[4:] == b"\x00" * 61
    try:
        build_report(bytes(REPORT_LEN + 1))
    except ValueError:
        pass
    else:
        raise AssertionError("đáng lẽ phải từ chối payload quá dài")
    devs = [{"usage_page": 0xFF00, "vendor_id": 1, "product_id": 2},
            {"usage_page": 0xFF00, "vendor_id": 3, "product_id": 4},
            {"usage_page": 0xF1D0, "vendor_id": 1, "product_id": 2}]
    assert select_device(devs, None, None, 0)["vendor_id"] == 1
    assert select_device(devs, None, None, 1)["vendor_id"] == 3
    assert select_device(devs, 3, None, 0)["product_id"] == 4
    for bad in [([], None, None, 0), (devs, None, None, 2), (devs, None, None, -1)]:
        try:
            select_device(*bad)
        except LookupError:
            pass
        else:
            raise AssertionError("đáng lẽ phải từ chối chọn thiết bị sai")
    print("self-test ok: đóng gói report HID echo đúng.")
    return 0


def select_device(devices: list, vid: int | None, pid: int | None, index: int) -> dict:
    """Chọn thiết bị echo: lọc usage_page 0xFF00 (+ VID/PID nếu cho), rồi --index."""
    cands = [d for d in (devices or [])
             if d.get("usage_page") == ECHO_USAGE_PAGE
             and (vid is None or d.get("vendor_id") == vid)
             and (pid is None or d.get("product_id") == pid)]
    if not cands:
        raise LookupError("không thấy HID echo (usage page 0xFF00)")
    if index < 0 or index >= len(cands):
        raise LookupError(f"chỉ thấy {len(cands)} thiết bị echo, không có số {index}")
    return cands[index]


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Kiểm tra echo HID của sketch hwtest.")
    ap.add_argument("--index", type=int, default=None,
                        help="chọn thiết bị echo số mấy (mặc định: tự chọn khi chỉ có đúng 1)")
    ap.add_argument("--vid", default=None, help="lọc vendor ID, ví dụ 0x303A")
    ap.add_argument("--pid", default=None, help="lọc product ID")
    ap.add_argument("-t", "--self-test", action="store_true", help="chỉ kiểm tra đóng gói")
    args = ap.parse_args(argv)
    if args.self_test:
        return self_test()
    try:
        vid = int(args.vid, 16) if args.vid else None
        pid = int(args.pid, 16) if args.pid else None
    except ValueError:
        print("--vid/--pid phải là hex, ví dụ 0x303A.")
        return 2
    try:
        import hid
    except ImportError:
        print("Thiếu thư viện hid. Chạy: pip install -r requirements.txt")
        return 2
    found = [d for d in hid.enumerate() if d.get("usage_page") == ECHO_USAGE_PAGE]
    explicit = args.index is not None or args.vid or args.pid
    if not explicit and len(found) != 1:
        for i, dev in enumerate(found):
            print(f"   [{i}] vid=0x{dev.get('vendor_id', 0):04x} "
                  f"pid=0x{dev.get('product_id', 0):04x} "
                  f"{dev.get('manufacturer_string')} {dev.get('product_string')}")
        if found:
            print(f"Thấy {len(found)} thiết bị echo, không dám đoán mò.")
            print("Chọn đúng board bằng --index (ESP32 là vid 0x303a).")
        else:
            print("Không thấy HID echo (usage page 0xFF00).")
        print("Kiểm tra: đã nạp hwtest ở USB Mode = USB-OTG, cắm cổng USB native.")
        return 1
    index = args.index if args.index is not None else 0
    try:
        target = select_device(found, vid, pid, index)
    except LookupError as exc:
        print(f"{exc}.")
        print("Kiểm tra: đã nạp hwtest ở USB Mode = USB-OTG, cắm cổng USB native.")
        return 1
    for i, dev in enumerate(found):
        mark = ">>" if dev == target else "  "
        print(f"{mark} [{i}] vid=0x{dev.get('vendor_id', 0):04x} "
              f"pid=0x{dev.get('product_id', 0):04x} "
              f"{dev.get('manufacturer_string')} {dev.get('product_string')}")
    device = hid.device()
    try:
        device.open_path(target["path"])
    except OSError as exc:
        print(f"Không mở được thiết bị: {exc}")
        return 1
    device.set_nonblocking(False)
    try:
        payload = os.urandom(PAYLOAD_LEN)
        device.write(build_report(payload))
        echo = bytes(device.read(REPORT_LEN + 1, timeout_ms=2000))
        if not echo:
            print("Thiết bị không trả lời.")
            return 1
        if len(echo) == REPORT_LEN + 1:
            if echo[0] != REPORT_ID:
                print(f"Echo sai report ID: muốn {REPORT_ID}, thấy {echo[0]}.")
                return 1
            body = echo[1:]
        elif len(echo) == REPORT_LEN:
            body = echo
        else:
            print(f"Echo dài lạ: {len(echo)} byte.")
            return 1
        if body[:PAYLOAD_LEN] != payload:
            print(f"Echo sai: nhận {body[:PAYLOAD_LEN].hex()}")
            return 1
        print("HID echo ok: 60 byte đi về khớp từng byte. Đường USB HID sống.")
    except OSError as exc:
        print(f"Lỗi HID: {exc}")
        return 1
    finally:
        device.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
