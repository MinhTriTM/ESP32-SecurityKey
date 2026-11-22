#!/usr/bin/env python3
"""Két mã hóa file: AES-256-GCM, khóa suy từ mật khẩu bằng PBKDF2.

Thay cho age/VeraCrypt ngoài trong quy trình sao lưu. Mật khẩu két chính là
dạng hex của bí mật gốc S (lấy từ mnemonic hoặc ghép share Shamir).

Cách dùng:
    pip install -r requirements-vault.txt
    python vault.py encrypt --in recovery.txt --out ket.bin
    python vault.py decrypt --in ket.bin --out recovery.txt
    python vault.py --self-test

Mật khẩu nhập qua getpass, hoặc --password-file để đọc từ file.
Cần Python 3.10 trở lên.
"""
import argparse
import getpass
import os
import sys
from pathlib import Path

try:
    import secureio
except ImportError:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import secureio

MAGIC = b"ESKVAULT1"
SALT_LEN = 16
NONCE_LEN = 12
PBKDF2_ROUNDS = 600_000


def _crypto():
    try:
        from cryptography.hazmat.primitives.ciphers.aead import AESGCM
        from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
        from cryptography.hazmat.primitives import hashes
        from cryptography.exceptions import InvalidTag
    except ImportError:
        print("Thiếu thư viện cryptography. Chạy: pip install -r requirements-vault.txt")
        sys.exit(2)
    return AESGCM, PBKDF2HMAC, hashes, InvalidTag


def derive_key(password: bytes, salt: bytes) -> bytes:
    """Suy khóa AES-256 từ mật khẩu. Salt phải ngẫu nhiên mỗi lần mã hóa."""
    _, PBKDF2HMAC, hashes, _ = _crypto()
    return PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt,
                      iterations=PBKDF2_ROUNDS).derive(password)


def encrypt_bytes(plain: bytes, password: bytes) -> bytes:
    AESGCM, _, _, _ = _crypto()
    salt, nonce = os.urandom(SALT_LEN), os.urandom(NONCE_LEN)
    cipher = AESGCM(derive_key(password, salt)).encrypt(nonce, plain, None)
    return MAGIC + salt + nonce + cipher


def decrypt_bytes(blob: bytes, password: bytes) -> bytes:
    AESGCM, _, _, InvalidTag = _crypto()
    if not blob:
        raise ValueError("két rỗng, không có gì để mở")
    if blob[:len(MAGIC)] != MAGIC:
        raise ValueError("file không phải két của tool này (sai magic)")
    head = len(MAGIC) + SALT_LEN + NONCE_LEN
    if len(blob) <= head:
        raise ValueError("két cụt: thiếu salt/nonce/dữ liệu mã hóa")
    salt = blob[len(MAGIC):len(MAGIC) + SALT_LEN]
    nonce = blob[len(MAGIC) + SALT_LEN:head]
    cipher = blob[head:]
    try:
        return AESGCM(derive_key(password, salt)).decrypt(nonce, cipher, None)
    except InvalidTag:
        raise ValueError("sai mật khẩu hoặc file bị sửa đổi")


def _read_pw(source: str | None, confirm: bool, prompt: str) -> bytes:
    if source:
        # Đọc NGUYÊN byte (kể cả ký tự xuống dòng cuối nếu có): file mật khẩu
        # phải chứa đúng mật khẩu, không thừa không thiếu.
        try:
            return Path(source).read_bytes()
        except OSError as exc:
            print(f"Không đọc được file mật khẩu: {exc}")
            sys.exit(1)
    first = getpass.getpass(prompt).encode("utf-8")
    if confirm:
        second = getpass.getpass("Nhập lại để xác nhận: ").encode("utf-8")
        if first != second or not first:
            print("Hai lần nhập không khớp hoặc rỗng.")
            sys.exit(1)
    return first


def read_password(args: argparse.Namespace, confirm: bool) -> bytes:
    return _read_pw(args.password_file, confirm, "Mật khẩu két: ")


def rekey_bytes(blob: bytes, old: bytes, new: bytes) -> bytes:
    """Đổi mật khẩu két: mở bằng mật khẩu cũ rồi mã hóa lại bằng mật khẩu mới."""
    return encrypt_bytes(decrypt_bytes(blob, old), new)


def cmd_rekey(args: argparse.Namespace) -> int:
    old = _read_pw(args.password_file, confirm=False, prompt="Mật khẩu két hiện tại: ")
    new = _read_pw(args.new_password_file, confirm=True, prompt="Mật khẩu két mới: ")
    try:
        blob = secureio.read_capped(args.in_file)
    except (OSError, ValueError) as exc:
        print(f"Không đọc được két: {exc}")
        return 1
    try:
        out = rekey_bytes(blob, old, new)
    except ValueError as exc:
        print(f"Không mở được két: {exc}")
        return 1
    try:
        secureio.write_file(args.out, out)
    except OSError as exc:
        print(f"Không ghi được {args.out}: {exc}")
        return 1
    print(f"Đã đổi mật khẩu két ra {args.out}. Xóa két cũ sau khi kiểm tra két mới!")
    return 0


def cmd_encrypt(args: argparse.Namespace) -> int:
    password = read_password(args, confirm=True)
    try:
        plain = secureio.read_capped(args.in_file)
    except (OSError, ValueError) as exc:
        print(f"Không đọc được file vào: {exc}")
        return 1
    try:
        secureio.write_file(args.out, encrypt_bytes(plain, password))
    except OSError as exc:
        print(f"Không ghi được {args.out}: {exc}")
        return 1
    print(f"Đã mã hóa ra {args.out}. Két này để ở đâu cũng được, kể cả cloud.")
    return 0


def cmd_decrypt(args: argparse.Namespace) -> int:
    password = read_password(args, confirm=False)
    try:
        blob = secureio.read_capped(args.in_file)
    except (OSError, ValueError) as exc:
        print(f"Không đọc được két: {exc}")
        return 1
    try:
        plain = decrypt_bytes(blob, password)
    except ValueError as exc:
        print(f"Không mở được két: {exc}")
        return 1
    try:
        secureio.write_secret_file(args.out, plain)
    except OSError as exc:
        print(f"Không ghi được {args.out}: {exc}")
        return 1
    print(f"Đã giải mã ra {args.out}. Xóa file này sau khi dùng xong!")
    return 0


def self_test() -> int:
    secret, password = os.urandom(200), os.urandom(32)
    blob = encrypt_bytes(secret, password)
    assert blob[:len(MAGIC)] == MAGIC
    assert decrypt_bytes(blob, password) == secret
    # Hai lần mã hóa cùng đầu vào phải ra khác nhau (salt/nonce ngẫu nhiên).
    assert encrypt_bytes(secret, password) != blob
    # Sai mật khẩu, file sửa 1 bit, sai magic đều bị từ chối.
    for bad_blob, bad_pw in [(blob, b"sai"), (blob[:-1] + bytes([blob[-1] ^ 1]), password)]:
        try:
            decrypt_bytes(bad_blob, bad_pw)
        except ValueError:
            pass
        else:
            raise AssertionError("đáng lẽ phải từ chối két sai")
    try:
        decrypt_bytes(b"RAC" + blob[3:], password)
    except ValueError:
        pass
    else:
        raise AssertionError("đáng lẽ phải từ chối magic sai")
    # Đổi mật khẩu: két mới mở bằng mật khẩu mới, mật khẩu cũ hết tác dụng.
    blob2 = rekey_bytes(blob, password, b"mat-khau-moi")
    assert decrypt_bytes(blob2, b"mat-khau-moi") == secret
    try:
        decrypt_bytes(blob2, password)
    except ValueError:
        pass
    else:
        raise AssertionError("đáng lẽ mật khẩu cũ phải hết tác dụng")
    try:
        rekey_bytes(blob, b"sai", b"moi")
    except ValueError:
        pass
    else:
        raise AssertionError("đáng lẽ rekey sai mật khẩu cũ phải hỏng")
    # Két rỗng và két cụt có thông điệp riêng, không gộp vào "sai mật khẩu".
    for bad, tag in [(b"", "két rỗng"), (MAGIC + b"cut", "két cụt"),
                     (blob[:20], "két cụt")]:
        try:
            decrypt_bytes(bad, password)
        except ValueError as exc:
            assert tag in str(exc), f"thông điệp sai cho két hỏng: {exc}"
        else:
            raise AssertionError("đáng lẽ phải từ chối két hỏng")
    print("self-test ok: mã hóa/giải mã đúng, sai mật khẩu và file sửa bị từ chối.")
    return 0


def main(argv: list[str]) -> int:
    if "--self-test" in argv or "-t" in argv:
        return self_test()
    parser = argparse.ArgumentParser(description="Két mã hóa file AES-256-GCM.")
    pw = argparse.ArgumentParser(add_help=False)
    pw.add_argument("--password-file", help="đọc mật khẩu từ file thay vì gõ")
    sub = parser.add_subparsers(dest="cmd", required=True)
    p_enc = sub.add_parser("encrypt", parents=[pw], help="mã hóa file thành két")
    p_enc.add_argument("--in", dest="in_file", required=True)
    p_enc.add_argument("--out", required=True)
    p_dec = sub.add_parser("decrypt", parents=[pw], help="mở két ra file")
    p_dec.add_argument("--in", dest="in_file", required=True)
    p_dec.add_argument("--out", required=True)
    p_key = sub.add_parser("rekey", parents=[pw], help="đổi mật khẩu két")
    p_key.add_argument("--in", dest="in_file", required=True)
    p_key.add_argument("--out", required=True)
    p_key.add_argument("--new-password-file", help="đọc mật khẩu mới từ file")
    args = parser.parse_args(argv)
    if args.cmd == "encrypt":
        return cmd_encrypt(args)
    if args.cmd == "rekey":
        return cmd_rekey(args)
    return cmd_decrypt(args)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
