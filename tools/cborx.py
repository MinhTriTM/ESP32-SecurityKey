#!/usr/bin/env python3
"""Bộ giải/mã CBOR tối thiểu cho CTAP2 (tách từ fido_check để dùng chung).

Giải mã: số, bytes, text, mảng, map, bool/null — đủ cho GetInfo. Mọi đầu
vào hỏng ném ValueError sạch (không TypeError/RecursionError/UnicodeDecode).
Mã hóa: dùng khi cần gửi tham số CBOR (làm sẵn cho PIN/credential sau này).

Không cần cài thêm thư viện. Cần Python 3.10 trở lên.
"""
from __future__ import annotations

import random
import sys

CBOR_MAX_DEPTH = 32


def _cbor_arg(buf: bytes) -> tuple[int, int, int]:
    if not buf:
        raise ValueError("CBOR cụt")
    major, info = buf[0] >> 5, buf[0] & 31
    if info < 24:
        return major, info, 1
    need = {24: 1, 25: 2, 26: 4, 27: 8}.get(info)
    if need is None or len(buf) < 1 + need:
        raise ValueError("CBOR dùng kiểu không hỗ trợ hoặc bị cụt")
    return major, int.from_bytes(buf[1:1 + need], "big"), 1 + need


def cbor_decode(buf: bytes, _depth: int = 0):
    """Giải mã một giá trị CBOR. Trả về (giá trị, phần còn lại).

    Mọi đầu vào hỏng (cụt, lồng sâu, key không băm được, UTF-8 sai) đều ném
    ValueError sạch, không bao giờ TypeError/RecursionError/UnicodeDecodeError.
    """
    if _depth > CBOR_MAX_DEPTH:
        raise ValueError(f"CBOR lồng quá sâu (quá {CBOR_MAX_DEPTH} tầng)")
    major, arg, hlen = _cbor_arg(buf)
    rest = buf[hlen:]
    if major == 0:
        return arg, rest
    if major == 1:
        return -1 - arg, rest
    if major == 2:
        if len(rest) < arg:
            raise ValueError(f"CBOR bytes cụt: cần {arg}, còn {len(rest)}")
        return bytes(rest[:arg]), rest[arg:]
    if major == 3:
        if len(rest) < arg:
            raise ValueError(f"CBOR text cụt: cần {arg}, còn {len(rest)}")
        try:
            return bytes(rest[:arg]).decode("utf-8"), rest[arg:]
        except UnicodeDecodeError:
            raise ValueError("CBOR text không phải UTF-8 hợp lệ")
    if major == 4:
        items = []
        for _ in range(arg):
            value, rest = cbor_decode(rest, _depth + 1)
            items.append(value)
        return items, rest
    if major == 5:
        mapping = {}
        for _ in range(arg):
            key, rest = cbor_decode(rest, _depth + 1)
            value, rest = cbor_decode(rest, _depth + 1)
            if not isinstance(key, (int, str, bytes)):
                raise ValueError(f"key map CBOR không băm được: {type(key).__name__}")
            mapping[key] = value
        return mapping, rest
    if major == 7 and arg == 20:
        return False, rest
    if major == 7 and arg == 21:
        return True, rest
    if major == 7 and arg == 22:
        return None, rest
    raise ValueError("CBOR dùng kiểu simple/float không hỗ trợ")


def _cbor_head(major: int, arg: int) -> bytes:
    if arg < 24:
        return bytes([(major << 5) | arg])
    if arg < 256:
        return bytes([(major << 5) | 24, arg])
    if arg < 65536:
        return bytes([(major << 5) | 25]) + arg.to_bytes(2, "big")
    if arg < 4294967296:
        return bytes([(major << 5) | 26]) + arg.to_bytes(4, "big")
    if arg < 18446744073709551616:
        return bytes([(major << 5) | 27]) + arg.to_bytes(8, "big")
    raise ValueError(f"số CBOR quá lớn: {arg}")


def cbor_encode(obj, _depth: int = 0) -> bytes:
    """Mã hóa obj thành CBOR definite-length. Kiểu lạ ném TypeError."""
    if _depth > CBOR_MAX_DEPTH:
        raise ValueError(f"CBOR lồng quá sâu (quá {CBOR_MAX_DEPTH} tầng)")
    if obj is True:
        return b"\xf5"
    if obj is False:
        return b"\xf4"
    if obj is None:
        return b"\xf6"
    if isinstance(obj, int):
        if obj >= 0:
            return _cbor_head(0, obj)
        return _cbor_head(1, -1 - obj)
    if isinstance(obj, bytes):
        return _cbor_head(2, len(obj)) + obj
    if isinstance(obj, str):
        raw = obj.encode("utf-8")
        return _cbor_head(3, len(raw)) + raw
    if isinstance(obj, list):
        return _cbor_head(4, len(obj)) + b"".join(cbor_encode(v, _depth + 1) for v in obj)
    if isinstance(obj, dict):
        out = [_cbor_head(5, len(obj))]
        for key, value in obj.items():
            if not isinstance(key, (int, str, bytes)):
                raise TypeError(f"key map CBOR không hỗ trợ: {type(key).__name__}")
            out.append(cbor_encode(key, _depth + 1))
            out.append(cbor_encode(value, _depth + 1))
        return b"".join(out)
    raise TypeError(f"kiểu không mã hóa CBOR được: {type(obj).__name__}")


def self_test() -> int:
    # 1. Round-trip: mã rồi giải ra đúng giá trị.
    vectors = [0, 1, 23, 24, 255, 1000, 2 ** 32 - 1, -1, -100,
               b"", b"bit", "", "rk", "FIDO_2_0",
               [], [1, 2, -2], {}, {1: [2, -2], 2: b"bit"},
               True, False, None,
               {1: ["U2F_V2", "FIDO_2_0"], 4: {"rk": True}, 5: 1024}]
    for v in vectors:
        raw = cbor_encode(v)
        back, rest = cbor_decode(raw)
        assert rest == b"" and back == v, f"round-trip lệch: {v!r}"
    canned = bytes.fromhex("A30182665532465F5632684649444F5F325F30"
                           "04A162726BF5"
                           "05190400")
    info, rest = cbor_decode(canned)
    assert rest == b"" and info == {1: ["U2F_V2", "FIDO_2_0"], 4: {"rk": True}, 5: 1024}
    assert cbor_decode(cbor_encode(info))[0] == info
    # 2. Từ chối sạch: kiểu lạ khi mã, lồng sâu hai chiều.
    for bad_obj in [{1, 2}, 1.5, object()]:
        try:
            cbor_encode(bad_obj)
        except TypeError:
            pass
        else:
            raise AssertionError(f"đáng lẽ phải từ chối mã hóa: {bad_obj!r}")
    deep = []
    for _ in range(40):
        deep = [deep]
    try:
        cbor_encode(deep)
    except ValueError:
        pass
    else:
        raise AssertionError("đáng lẽ phải từ chối mã hóa lồng sâu")
    # 3. Fuzz gieo seed: 3000 ca ngẫu nhiên chỉ được ném ValueError.
    # Bất kỳ TypeError/RecursionError/UnicodeDecodeError nào lọt ra cũng làm
    # hỏng test (không bắt ở đây là cố ý).
    rng = random.Random(20261122)
    seeds = [canned, bytes.fromhex("A2018202210243626974"),
             b"\x81", b"\xa1", b"\x5f", b"\x9f", b""]
    for _ in range(3000):
        buf = bytearray(rng.choice(seeds) + bytes(rng.randrange(256)
                        for _ in range(rng.randrange(0, 25))))[:32]
        for _ in range(rng.randrange(0, 3)):
            if buf:
                buf[rng.randrange(len(buf))] = rng.randrange(256)
        try:
            cbor_decode(bytes(buf))
        except ValueError:
            pass
    print("self-test ok: CBOR mã/giải round-trip, từ chối sạch, fuzz 3000 ca seed.")
    return 0


if __name__ == "__main__":
    if "--self-test" in sys.argv or "-t" in sys.argv:
        sys.exit(self_test())
    print("Module dùng chung, không có lệnh CLI. Chạy với --self-test để kiểm tra.")
    sys.exit(2)
