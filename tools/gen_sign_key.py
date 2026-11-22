#!/usr/bin/env python3
"""Sinh khóa ký Secure Boot ngoại tuyến (U053, chạy 1 lần duy nhất).

Tạo keys/secure-boot-signing.key (RSA-3072, PEM, PKCS#8) để ký bản firmware
phát hành. ESP32-S3 dùng Secure Boot V2 RSA (xem bootloader/Kconfig.projbuild
của ESP-IDF: scheme ECDSA V2 chỉ dành cho ESP32-C2). Từ chối ghi đè khóa đã
có. Đọc keys/README.md trước khi chạy: backup khóa ngay bằng vault + Shamir
sau khi tạo.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / ".tooling" / "pylibs"))
sys.path.insert(0, str(ROOT / "tools"))
import secureio  # noqa: E402

KEY_PATH = ROOT / "keys" / "secure-boot-signing.key"


def main() -> int:
    if KEY_PATH.exists():
        print(f"Đã có {KEY_PATH}, không ghi đè. Xóa tay nếu chắc chắn muốn tạo mới.")
        return 1
    try:
        from cryptography.hazmat.primitives import serialization
        from cryptography.hazmat.primitives.asymmetric import rsa
    except ImportError:
        print("Thiếu cryptography. Chạy: pip install --target .tooling/pylibs -r tools/requirements-vault.txt")
        return 2
    key = rsa.generate_private_key(public_exponent=65537, key_size=3072)
    pem = key.private_bytes(serialization.Encoding.PEM,
                              serialization.PrivateFormat.PKCS8,
                              serialization.NoEncryption())
    try:
        secureio.write_secret_file(KEY_PATH, pem)
    except OSError as exc:
        print(f"Không ghi được khóa: {exc}")
        return 1
    pub = key.public_key().public_bytes(serialization.Encoding.DER,
                                        serialization.PublicFormat.SubjectPublicKeyInfo)
    import hashlib
    print(f"Đã tạo {KEY_PATH} (RSA-3072).")
    print(f"Vân tay khóa công khai (SHA-256): {hashlib.sha256(pub).hexdigest()}")
    print("BACKUP NGAY bằng vault + Shamir theo keys/README.md rồi mới build bản ký.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
