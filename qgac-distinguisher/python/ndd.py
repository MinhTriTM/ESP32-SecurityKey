# -*- coding: utf-8 -*-
"""Doc/ghi file dataset .ndd bang numpy (dung cho doi chieu va huan luyen).

Dinh dang .ndd (xem docs/THIET-KE.md):
- Header 20 byte: magic b"NDD1", version u16 LE, rounds u16 LE,
  n_samples u32 LE, seed u64 LE.
- Moi mau 9 byte: 4 tu u16 LE + 1 byte nhan (0/1).
"""

from __future__ import annotations

import struct

import numpy as np

MAGIC = b"NDD1"
VERSION = 1
DINH_DANG_HEADER = "<4sHHIQ"  # magic, version, rounds, n, seed
DO_DAI_HEADER = struct.calcsize(DINH_DANG_HEADER)  # 20
DO_DAI_MAU = 9  # 4*u16 + 1 byte


def ghi_ndd(duong_dan: str, rounds: int, seed: int,
            tu: np.ndarray, nhan: np.ndarray) -> None:
    """Ghi dataset ra file .ndd.

    - tu: mang (N, 4) uint16 — cap ban ma (c0.x, c0.y, c1.x, c1.y).
    - nhan: mang (N,) uint8 — 0 hoac 1.
    """
    tu = np.ascontiguousarray(tu, dtype=np.uint16)
    nhan = np.ascontiguousarray(nhan, dtype=np.uint8)
    assert tu.ndim == 2 and tu.shape[1] == 4, "tu phai co dang (N, 4)"
    assert nhan.ndim == 1 and nhan.shape[0] == tu.shape[0], "nhan phai co dang (N,)"
    assert set(np.unique(nhan)).issubset({0, 1}), "nhan chi duoc 0/1"
    with open(duong_dan, "wb") as f:
        f.write(struct.pack(DINH_DANG_HEADER, MAGIC, VERSION, rounds,
                            tu.shape[0], seed))
        for w, y in zip(tu, nhan):
            f.write(struct.pack("<HHHHB", int(w[0]), int(w[1]),
                                int(w[2]), int(w[3]), int(y)))


def doc_ndd(duong_dan: str) -> dict:
    """Doc file .ndd, tra ve dict(version, rounds, n, seed, tu, nhan)."""
    with open(duong_dan, "rb") as f:
        du_lieu = f.read()
    if len(du_lieu) < DO_DAI_HEADER:
        raise ValueError("file .ndd qua ngan (thieu header)")
    magic, version, rounds, n, seed = struct.unpack(
        DINH_DANG_HEADER, du_lieu[:DO_DAI_HEADER])
    if magic != MAGIC:
        raise ValueError(f"sai magic .ndd: {magic!r}")
    if version != VERSION:
        raise ValueError(f"phien ban .ndd khong ho tro: {version}")
    muon = DO_DAI_HEADER + n * DO_DAI_MAU
    if len(du_lieu) != muon:
        raise ValueError(f"do dai file {len(du_lieu)} khong khop header ({muon})")
    tu = np.zeros((n, 4), dtype=np.uint16)
    nhan = np.zeros(n, dtype=np.uint8)
    vi_tri = DO_DAI_HEADER
    for i in range(n):
        w0, w1, w2, w3, y = struct.unpack("<HHHHB", du_lieu[vi_tri:vi_tri + 9])
        tu[i] = (w0, w1, w2, w3)
        nhan[i] = y
        vi_tri += 9
    if not set(np.unique(nhan)).issubset({0, 1}):
        raise ValueError("nhan trong file khong hop le (chi duoc 0/1)")
    return {"version": version, "rounds": rounds, "n": n, "seed": seed,
            "tu": tu, "nhan": nhan}


def tu_thanh_bit(tu: np.ndarray) -> np.ndarray:
    """Doi mang (N, 4) uint16 thanh (N, 64) float32, MSB truoc.

    Port cua `words_to_bits` trong tools/ml_distinguisher.py cua repo me.
    """
    tu = np.ascontiguousarray(tu, dtype=np.uint16)
    n = tu.shape[0]
    bit = np.zeros((n, 64), dtype=np.float32)
    for j in range(4):
        w = tu[:, j].astype(np.uint16)
        for b in range(16):
            bit[:, j * 16 + b] = ((w >> (15 - b)) & 1).astype(np.float32)
    return bit
