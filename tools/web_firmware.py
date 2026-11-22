#!/usr/bin/env python3
"""Quét web/firmware và sinh manifest firmware.json cho siêu web nạp.

Chạy từ thư mục gốc repo:
    python tools/web_firmware.py
"""
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FW_DIR = ROOT / "web" / "firmware"

# Mô tả tiếng Việt cho từng gói firmware có sẵn trong web.
PACKAGES = {
    "hwtest-otg": {
        "name": "hwtest — bản USB-OTG (khuyên dùng)",
        "desc": "Kiểm tra USB CDC, nút BOOT, LED RGB và HID echo 64 byte. Dùng cổng USB native sau khi nạp.",
        "files": [{"path": "hwtest-otg/hwtest.ino.merged.bin", "address": "0x0"}],
    },
    "hwtest-hwcdc": {
        "name": "hwtest — bản HWCDC (dự phòng)",
        "desc": "Giống bản OTG nhưng không có HID echo. Dùng khi board/cáp không chịu OTG.",
        "files": [{"path": "hwtest-hwcdc/hwtest.ino.merged.bin", "address": "0x0"}],
    },
}


def sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def verify_manifest() -> int:
    """Đối chiếu file trên đĩa với firmware.json (tồn tại + cỡ + SHA-256)."""
    try:
        manifest = json.loads((FW_DIR / "firmware.json").read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        print(f"Manifest lỗi: {exc}")
        return 1
    fail = 0
    for pkg in manifest.get("packages", []):
        for entry in pkg.get("files", []):
            full = FW_DIR / entry["path"]
            tag = f"{pkg.get('id')}:{entry.get('path')}"
            if not full.exists():
                print(f"HỎNG {tag}: thiếu file")
                fail = 1
                continue
            size = full.stat().st_size
            if size != entry.get("size"):
                print(f"HỎNG {tag}: cỡ {size} != {entry.get('size')}")
                fail = 1
                continue
            if sha256_of(full) != entry.get("sha256"):
                print(f"HỎNG {tag}: sai SHA-256")
                fail = 1
                continue
            print(f"ok {tag} ({size} byte, SHA-256 khớp)")
    if fail:
        print("Manifest KHÔNG khớp: build lại firmware rồi chạy tools/web_firmware.py.")
    else:
        print("Manifest khớp: mọi file firmware nguyên vẹn.")
    return fail


def main(argv: list[str] | None = None) -> None:
    if argv is None:
        argv = sys.argv[1:]
    if "--check" in argv:
        raise SystemExit(verify_manifest())
    manifest = {"packages": []}
    for pkg_id, pkg in PACKAGES.items():
        files = []
        for entry in pkg["files"]:
            full = FW_DIR / entry["path"]
            if not full.exists():
                raise SystemExit(f"Thiếu file {full}. Build trước đã (xem scripts/build_hwtest.ps1).")
            files.append(
                {
                    "path": entry["path"],
                    "address": entry["address"],
                    "size": full.stat().st_size,
                    "sha256": sha256_of(full),
                }
            )
        manifest["packages"].append(
            {"id": pkg_id, "name": pkg["name"], "desc": pkg["desc"], "files": files}
        )
    out = FW_DIR / "firmware.json"
    out.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Đã ghi {out} với {len(manifest['packages'])} gói.")


if __name__ == "__main__":
    main()
