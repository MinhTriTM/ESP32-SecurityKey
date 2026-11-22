#!/usr/bin/env python3
"""Hàm dùng chung để ghi/đọc file an toàn (hiện thực một phần U029/U034).

Mọi tool ghi file bí mật (share Shamir, entropy, két, khóa PQC) PHẢI qua
module này thay vì gọi Path.write_* trực tiếp:
- tự tạo thư mục cha (không còn OSError vì thiếu thư mục),
- ghi nguyên tử (file tạm cùng thư mục + thay thế),
- chmod 0600 trên POSIX cho file bí mật,
- chặn tên file lách thư mục (../, phân cách, ổ đĩa),
- đọc có giới hạn cỡ để file lạ không nuốt RAM.

Không cần cài thêm thư viện. Cần Python 3.10 trở lên.
"""
from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path

SECRET_MODE = 0o600
READ_CAP = 64 * 1024 * 1024  # 64 MB: quá cỡ này thì từ chối đọc


def ensure_parent(path: str | Path) -> Path:
    """Tạo thư mục cha nếu thiếu. Trả về Path đã chuẩn hóa."""
    p = Path(path)
    parent = p.parent
    if str(parent) not in ("", "."):
        parent.mkdir(parents=True, exist_ok=True)
    return p


def check_safe_name(name: str) -> str:
    """Tên file đơn (tiền tố...): cấm lách thư mục. Trả về tên nếu đạt."""
    if not name or "\x00" in name:
        raise ValueError("tên file rỗng hoặc chứa byte NUL")
    if "/" in name or "\\" in name or ":" in name:
        raise ValueError(f"tên file chứa ký tự phân cách: {name!r}")
    if name in (".", "..") or ".." in name:
        raise ValueError(f"tên file lách thư mục: {name!r}")
    if Path(name).is_absolute():
        raise ValueError(f"tên file tuyệt đối: {name!r}")
    return name


def _atomic_replace(tmp_path: str, dest: Path) -> None:
    os.replace(tmp_path, dest)


def write_file(path: str | Path, data: bytes | str, secret: bool = False) -> Path:
    """Ghi file nguyên tử, tự tạo thư mục cha. secret=True thì chmod 0600."""
    dest = ensure_parent(path)
    raw = data.encode("utf-8") if isinstance(data, str) else bytes(data)
    fd, tmp = tempfile.mkstemp(dir=str(dest.parent), prefix=".tmp-")
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(raw)
            f.flush()
            os.fsync(f.fileno())
        if secret and os.name == "posix":
            os.chmod(tmp, SECRET_MODE)
        _atomic_replace(tmp, dest)
    except BaseException:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise
    return dest


def write_secret_file(path: str | Path, data: bytes | str) -> Path:
    """Ghi file bí mật: nguyên tử + thư mục cha + 0600 trên POSIX."""
    return write_file(path, data, secret=True)


def read_capped(path: str | Path, cap: int = READ_CAP) -> bytes:
    """Đọc file, từ chối nếu quá cap byte (chống nuốt RAM)."""
    p = Path(path)
    size = p.stat().st_size
    if size > cap:
        raise ValueError(f"file {p} dài {size} byte, vượt giới hạn {cap}")
    return p.read_bytes()


def self_test() -> int:
    import tempfile

    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        # 1. Tên nguy hiểm bị chặn, tên thường lọt.
        for bad in ["../x", "a/b", "a\\b", "C:x", "..", ".", "", "a..b", "x\x00y"]:
            try:
                check_safe_name(bad)
            except ValueError:
                pass
            else:
                raise AssertionError(f"đáng lẽ phải chặn tên: {bad!r}")
        assert check_safe_name("mlkem768") == "mlkem768"
        assert check_safe_name("share-1-of-3.txt") == "share-1-of-3.txt"
        # 2. Tự tạo thư mục cha nhiều tầng + ghi nguyên tử đúng nội dung.
        deep = root / "a" / "b" / "c.txt"
        write_file(deep, "nội dung")
        assert deep.read_text(encoding="utf-8") == "nội dung"
        assert not list((root / "a" / "b").glob(".tmp-*")), "còn file tạm sau ghi"
        # 3. File bí mật 0600 trên POSIX (Windows bỏ qua vì chmod khác nghĩa).
        sec = root / "s.bin"
        write_secret_file(sec, "bí mật")
        assert sec.read_bytes() == "bí mật".encode("utf-8")
        if os.name == "posix":
            assert sec.stat().st_mode & 0o777 == SECRET_MODE, "quyền file bí mật sai"
        # 4. Đọc có giới hạn cỡ.
        big = root / "big.bin"
        big.write_bytes(b"0" * 100)
        try:
            read_capped(big, cap=64)
        except ValueError:
            pass
        else:
            raise AssertionError("đáng lẽ phải từ chối file quá cap")
        assert read_capped(big, cap=100) == b"0" * 100
    print("self-test ok: chặn tên lách thư mục, ghi nguyên tử + 0600, đọc giới hạn cỡ.")
    return 0


if __name__ == "__main__":
    if "--self-test" in sys.argv or "-t" in sys.argv:
        sys.exit(self_test())
    print("Module dùng chung, không có lệnh CLI. Chạy với --self-test để kiểm tra.")
    sys.exit(2)
