#!/usr/bin/env python3
"""Trao đổi khóa hậu lượng tử ML-KEM-768 qua liboqs-python.

Chức năng: sinh cặp khóa, đóng gói (encapsulate) và mở gói (decapsulate)
để hai bên cùng suy ra một shared secret 32 byte mà không gửi nó trên kênh.

Cài đặt (không cài system-wide, chỉ vào .tooling/pylibs của repo):
    pip install --target .tooling/pylibs -r tools/requirements-pqc.txt

Chạy (luôn kèm PYTHONPATH để thấy .tooling/pylibs):
    set PYTHONPATH=.tooling/pylibs && python tools/pqc.py --self-test
    set PYTHONPATH=.tooling/pylibs && python tools/pqc.py keygen --out-dir out
    set PYTHONPATH=.tooling/pylibs && python tools/pqc.py encapsulate --public-key out/mlkem768.pk --out-ct out/ct.bin --out-ss out/ss.a
    set PYTHONPATH=.tooling/pylibs && python tools/pqc.py decapsulate --secret-key out/mlkem768.sk --ciphertext out/ct.bin --out-ss out/ss.b

Ghi chú về thư viện native liboqs (Windows):
    liboqs-python chỉ là wrapper ctypes, nó cần DLL liboqs native. Lần đầu
    `import oqs` sẽ tự clone + build liboqs vào thư mục _oqs trong home của
    bạn, việc này cần CMake và trình biên dịch C (Visual Studio). Nếu đã
    build tay vào chỗ khác, trỏ biến môi trường OQS_INSTALL_PATH tới thư mục
    cài đó trước khi chạy (oqs tìm oqs.dll/liboqs.dll trong thư mục bin
    bên dưới OQS_INSTALL_PATH).

Định dạng file: byte thô (raw), không header. Kích thước ML-KEM-768 chuẩn:
    public key 1184 byte, secret key 2400 byte, ciphertext 1088 byte,
    shared secret 32 byte. Tool không hardcode mà đọc từ kem.details.

Cần Python 3.10 trở lên.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

try:
    import secureio
except ImportError:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import secureio

# Tên thuật toán đúng như liboqs đăng ký (kiểm tra bằng
# oqs.get_enabled_kem_mechanisms(), xem --self-test).
ALG = "ML-KEM-768"

# Mã thoát thiếu thư viện/sai dùng (bảng chuẩn NCKH-052: 0 ok, 1 lỗi chạy, 2 thiếu lib/sai dùng).
EXIT_MISSING_LIB = 2


class OqsMissingError(RuntimeError):
    """Thiếu liboqs-python hoặc DLL liboqs native."""


def load_oqs():
    """Import oqs, gom mọi kiểu hỏng thành OqsMissingError dễ đọc.

    oqs có 3 kiểu hỏng khi thiếu lib: ImportError (chưa pip install),
    RuntimeError (không thấy shared library), SystemExit (tự build
    liboqs thất bại, ví dụ thiếu cmake/trình biên dịch C).
    """
    try:
        import oqs  # type: ignore[import-not-found]

        return oqs
    except SystemExit as exc:
        raise OqsMissingError(
            f"Không tải được liboqs native ({exc}). Cần build liboqs: cài CMake "
            "và Visual Studio (workload Desktop C++), rồi import oqs một lần để "
            "nó tự build vào thư mục _oqs trong home của bạn; hoặc build tay "
            "rồi trỏ OQS_INSTALL_PATH tới thư mục cài."
        ) from exc
    except (ImportError, RuntimeError, OSError) as exc:
        raise OqsMissingError(
            f"Thiếu thư viện PQC ({exc}). Chạy: "
            "pip install --target .tooling/pylibs -r tools/requirements-pqc.txt "
            "rồi chạy lại với PYTHONPATH=.tooling/pylibs"
            + (
                "; nếu vẫn báo thiếu shared library thì build liboqs native "
                "(cần CMake + Visual Studio) hoặc trỏ OQS_INSTALL_PATH."
                if not isinstance(exc, ImportError)
                else ""
            )
        ) from exc


def check_alg(oqs) -> None:
    """Bảo đảm ML-KEM-768 có mặt và được bật trong liboqs đang tải."""
    enabled = oqs.get_enabled_kem_mechanisms()
    if ALG in enabled:
        return
    supported = oqs.get_supported_kem_mechanisms()
    if ALG in supported:
        raise OqsMissingError(
            f"{ALG} có trong liboqs nhưng chưa được bật (enabled={len(enabled)} "
            "thuật toán). Hãy build lại liboqs với KEM mặc định."
        )
    raise OqsMissingError(
        f"{ALG} không có trong liboqs này (hỗ trợ {len(supported)} thuật toán). "
        "Hãy nâng cấp liboqs/liboqs-python."
    )


def alg_details(oqs) -> dict:
    """Đọc kích thước khóa/bản mã từ chính liboqs (không hardcode)."""
    with oqs.KeyEncapsulation(ALG) as kem:
        return dict(kem.details)


def generate_keypair(oqs) -> tuple[bytes, bytes]:
    """Sinh cặp khóa mới, trả về (public_key, secret_key)."""
    with oqs.KeyEncapsulation(ALG) as kem:
        public_key = kem.generate_keypair()
        secret_key = kem.export_secret_key()
    return public_key, secret_key


def encapsulate(oqs, public_key: bytes) -> tuple[bytes, bytes]:
    """Đóng gói với khóa công khai, trả về (ciphertext, shared_secret)."""
    with oqs.KeyEncapsulation(ALG) as kem:
        return kem.encap_secret(public_key)


def decapsulate(oqs, secret_key: bytes, ciphertext: bytes) -> bytes:
    """Mở gói bằng khóa bí mật, trả về shared_secret."""
    with oqs.KeyEncapsulation(ALG, secret_key=secret_key) as kem:
        return kem.decap_secret(ciphertext)


def _read_exact(path: Path, expect_len: int | None, label: str) -> bytes:
    try:
        data = path.read_bytes()
    except OSError as exc:
        raise SystemExit(f"Lỗi: không đọc được {label} {path}: {exc}") from exc
    if expect_len is not None and len(data) != expect_len:
        raise SystemExit(
            f"Lỗi: {label} {path} dài {len(data)} byte, đáng lẽ {expect_len} byte."
        )
    return data


def cmd_keygen(oqs, args: argparse.Namespace) -> int:
    try:
        secureio.check_safe_name(args.prefix)
    except ValueError as exc:
        print(f"Tiền tố không an toàn: {exc}")
        return 2
    chi_tiet = alg_details(oqs)
    public_key, secret_key = generate_keypair(oqs)
    out_dir = Path(args.out_dir)
    pk_path = out_dir / f"{args.prefix}.pk"
    sk_path = out_dir / f"{args.prefix}.sk"
    try:
        secureio.write_file(pk_path, public_key)
        secureio.write_secret_file(sk_path, secret_key)
    except OSError as exc:
        print(f"Không ghi được khóa: {exc}")
        return 1
    print(f"Đã ghi {pk_path} ({len(public_key)} byte, đáng lẽ {chi_tiet['length_public_key']}).")
    print(f"Đã ghi {sk_path} ({len(secret_key)} byte, đáng lẽ {chi_tiet['length_secret_key']}).")
    return 0


def cmd_encapsulate(oqs, args: argparse.Namespace) -> int:
    chi_tiet = alg_details(oqs)
    public_key = _read_exact(
        Path(args.public_key), chi_tiet["length_public_key"], "khóa công khai"
    )
    try:
        ciphertext, shared_secret = encapsulate(oqs, public_key)
    except (ValueError, RuntimeError) as exc:
        print(f"Đóng gói thất bại: {exc}")
        return 1
    try:
        secureio.write_file(args.out_ct, ciphertext)
        secureio.write_secret_file(args.out_ss, shared_secret)
    except OSError as exc:
        print(f"Không ghi được kết quả: {exc}")
        return 1
    print(f"Đã ghi {args.out_ct} ({len(ciphertext)} byte).")
    print(f"Đã ghi {args.out_ss} ({len(shared_secret)} byte, giữ bí mật).")
    return 0


def cmd_decapsulate(oqs, args: argparse.Namespace) -> int:
    chi_tiet = alg_details(oqs)
    secret_key = _read_exact(
        Path(args.secret_key), chi_tiet["length_secret_key"], "khóa bí mật"
    )
    ciphertext = _read_exact(
        Path(args.ciphertext), chi_tiet["length_ciphertext"], "bản mã"
    )
    try:
        shared_secret = decapsulate(oqs, secret_key, ciphertext)
    except (ValueError, RuntimeError) as exc:
        print(f"Mở gói thất bại: {exc}")
        return 1
    try:
        secureio.write_secret_file(args.out_ss, shared_secret)
    except OSError as exc:
        print(f"Không ghi được kết quả: {exc}")
        return 1
    print(f"Đã ghi {args.out_ss} ({len(shared_secret)} byte, giữ bí mật).")
    return 0


def self_test() -> int:
    """Kiểm thử vòng tròn thật trên liboqs: khớp đúng, hỏng sạch khi sai."""
    try:
        oqs = load_oqs()
    except OqsMissingError as exc:
        print(exc)
        return EXIT_MISSING_LIB
    try:
        check_alg(oqs)
    except OqsMissingError as exc:
        print(exc)
        return EXIT_MISSING_LIB
    print(f"liboqs {oqs.oqs_version()}, liboqs-python {oqs.oqs_python_version()}.")

    # 1. Sinh khóa + đọc kích thước từ liboqs.
    chi_tiet = alg_details(oqs)
    print(
        "Kích thước: pk={length_public_key}, sk={length_secret_key}, "
        "ct={length_ciphertext}, ss={length_shared_secret}.".format(**chi_tiet)
    )
    public_key, secret_key = generate_keypair(oqs)
    assert len(public_key) == chi_tiet["length_public_key"], "khóa công khai sai cỡ"
    assert len(secret_key) == chi_tiet["length_secret_key"], "khóa bí mật sai cỡ"
    print("1. keygen ok: cặp khóa đúng kích thước.")

    # 2. Vòng tròn đóng gói -> mở gói phải cho cùng shared secret.
    ciphertext, ss_gui = encapsulate(oqs, public_key)
    assert len(ciphertext) == chi_tiet["length_ciphertext"], "bản mã sai cỡ"
    assert len(ss_gui) == chi_tiet["length_shared_secret"], "shared secret sai cỡ"
    ss_nhan = decapsulate(oqs, secret_key, ciphertext)
    assert ss_gui == ss_nhan, "round-trip lệch: hai shared secret khác nhau"
    print("2. round-trip ok: shared secret hai đầu khớp từng byte.")

    # 3. Mở gói bằng SAI khóa: ML-KEM từ chối ngầm (implicit rejection) nên
    # vẫn trả 32 byte nhưng phải KHÁC secret gốc, tuyệt đối không khớp lén.
    _, secret_key_lac = generate_keypair(oqs)
    ss_sai_khoa = decapsulate(oqs, secret_key_lac, ciphertext)
    assert ss_sai_khoa != ss_gui, "SAI KHÓA mà vẫn ra đúng secret!"
    print("3. sai khóa ok: secret trả về khác hẳn (từ chối ngầm), không khớp lén.")

    # 4. Bản mã sửa 1 bit: secret mở ra phải khác, không được khớp lén.
    ban_ma_sua = bytearray(ciphertext)
    ban_ma_sua[0] ^= 0x01
    ss_sua_ct = decapsulate(oqs, secret_key, bytes(ban_ma_sua))
    assert ss_sua_ct != ss_gui, "SỬA 1 BIT bản mã mà vẫn ra đúng secret!"
    print("4. sửa 1 bit ok: secret trả về khác hẳn, không khớp lén.")

    # 5. Bản mã cắt ngắn: wrapper phải báo lỗi sạch (ValueError), không crash.
    try:
        decapsulate(oqs, secret_key, ciphertext[:-1])
    except ValueError:
        print("5. cắt ngắn bản mã ok: báo ValueError sạch.")
    else:
        raise AssertionError("bản mã thiếu byte mà không báo lỗi!")

    # 6. Vòng tròn qua CLI thật trong thư mục tạm.
    import tempfile

    with tempfile.TemporaryDirectory() as tmp:
        d = Path(tmp)
        rc = cmd_keygen(oqs, argparse.Namespace(out_dir=str(d / "k"), prefix="t"))
        assert rc == 0, "CLI keygen hỏng"
        rc = cmd_encapsulate(oqs, argparse.Namespace(
            public_key=str(d / "k" / "t.pk"), out_ct=str(d / "x" / "ct.bin"),
            out_ss=str(d / "x" / "ss.a")))
        assert rc == 0, "CLI encap hỏng"
        rc = cmd_decapsulate(oqs, argparse.Namespace(
            secret_key=str(d / "k" / "t.sk"), ciphertext=str(d / "x" / "ct.bin"),
            out_ss=str(d / "x" / "ss.b")))
        assert rc == 0, "CLI decap hỏng"
        a, b = (d / "x" / "ss.a").read_bytes(), (d / "x" / "ss.b").read_bytes()
        assert a == b and len(a) == chi_tiet["length_shared_secret"]
        print("6. CLI ok: keygen -> encap -> decap trong thư mục tạm, secret khớp.")

    # 7. Tiền tố lách thư mục bị từ chối trước khi ghi bất cứ gì.
    rc = cmd_keygen(oqs, argparse.Namespace(out_dir=".", prefix="../lac"))
    assert rc == 2, "đáng lẽ phải chặn tiền tố ../"
    print("7. chặn lách thư mục ok: tiền tố ../ bị từ chối.")

    print("self-test ok: ML-KEM-768 keygen/encap/decap đúng.")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="ML-KEM-768 keygen/đóng gói/mở gói qua liboqs-python."
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="chạy vòng tròn keygen/encap/decap thật trên liboqs",
    )
    sub = parser.add_subparsers(dest="lenh")

    p_keygen = sub.add_parser("keygen", help="sinh cặp khóa ML-KEM-768")
    p_keygen.add_argument("--out-dir", default=".", help="thư mục ghi khóa")
    p_keygen.add_argument("--prefix", default="mlkem768", help="tiền tố tên file")

    p_enc = sub.add_parser(
        "encapsulate", aliases=["encap"], help="đóng gói với khóa công khai"
    )
    p_enc.add_argument("--public-key", required=True, help="file khóa công khai (.pk)")
    p_enc.add_argument("--out-ct", required=True, help="file ghi bản mã")
    p_enc.add_argument("--out-ss", required=True, help="file ghi shared secret")

    p_dec = sub.add_parser(
        "decapsulate", aliases=["decap"], help="mở gói bằng khóa bí mật"
    )
    p_dec.add_argument("--secret-key", required=True, help="file khóa bí mật (.sk)")
    p_dec.add_argument("--ciphertext", required=True, help="file bản mã")
    p_dec.add_argument("--out-ss", required=True, help="file ghi shared secret")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.self_test or args.lenh is None:
        if args.lenh is not None:
            print("Sai dùng: không dùng --self-test chung với lệnh khác.")
            return 2
        return self_test()
    try:
        oqs = load_oqs()
        check_alg(oqs)
    except OqsMissingError as exc:
        print(exc)
        return EXIT_MISSING_LIB
    if args.lenh == "keygen":
        return cmd_keygen(oqs, args)
    if args.lenh in ("encapsulate", "encap"):
        return cmd_encapsulate(oqs, args)
    if args.lenh in ("decapsulate", "decap"):
        return cmd_decapsulate(oqs, args)
    raise AssertionError(f"lệnh lạ: {args.lenh}")


if __name__ == "__main__":
    sys.exit(main())
