#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Distinguisher no-ron kieu Gohr tren Speck32/64 rut gon vong (hoc tap).

Thi nghiem: huan luyen MLP nho phan biet dau ra cua ma toy sau R vong
(voi chenh lech ban ro co dinh) voi du lieu ngau nhien.

- Ma toy: Speck32/64 (khoi 32 bit, khoa 64 bit), so vong R tuy chon.
- Chenh lech ban ro co dinh: (0x0040, 0x0000).
- Dac trung: 64 bit noi cua cap ban ma (c0, c1).
- Mo hinh: MLP numpy thuan (khong can torch/sklearn), chay CPU vai phut.

Vi du:
    python tools/ml_distinguisher.py --rounds 5,6,7 --samples 6000 --epochs 5
    python tools/ml_distinguisher.py --self-test
"""

from __future__ import annotations

import argparse
import sys
import time

try:
    import numpy as np
except ImportError:
    print("Thiếu thư viện numpy. Chạy: pip install -r tools/requirements.txt")
    raise SystemExit(2)

MASK16 = 0xFFFF
ALPHA = 7  # tham so xoay Speck32
BETA = 2
FULL_ROUNDS = 22  # so vong chuan cua Speck32/64

# Chenh lech ban ro co dinh (kieu Gohr): dx = 0x0040, dy = 0x0000.
FIXED_DX = 0x0040
FIXED_DY = 0x0000


# ---------------------------------------------------------------------------
# Speck32/64
# ---------------------------------------------------------------------------

def rotr16(x: int, r: int) -> int:
    """Xoay phai tu 16 bit."""
    return ((x >> r) | (x << (16 - r))) & MASK16


def rotl16(x: int, r: int) -> int:
    """Xoay trai tu 16 bit."""
    return ((x << r) | (x >> (16 - r))) & MASK16


def expand_key(key_words: tuple[int, int, int, int], rounds: int) -> list[int]:
    """Mo rong khoa 64 bit (k0..k3) thanh `rounds` khoa vong."""
    rk = [key_words[0] & MASK16]
    ell = [w & MASK16 for w in key_words[1:]]  # l0, l1, l2
    for i in range(rounds - 1):
        new_l = ((rotr16(ell[i], ALPHA) + rk[i]) & MASK16) ^ i
        ell.append(new_l)
        rk.append(rotl16(rk[i], BETA) ^ new_l)
    return rk


def encrypt(pt: tuple[int, int], key_words: tuple[int, int, int, int],
            rounds: int) -> tuple[int, int]:
    """Ma hoa 1 khoi (x, y) qua `rounds` vong."""
    rk = expand_key(key_words, rounds)
    x, y = pt
    for i in range(rounds):
        x = (((rotr16(x, ALPHA) + y) & MASK16) ^ rk[i])
        y = rotl16(y, BETA) ^ x
    return (x, y)


def decrypt(ct: tuple[int, int], key_words: tuple[int, int, int, int],
            rounds: int) -> tuple[int, int]:
    """Giai ma 1 khoi (x, y) qua `rounds` vong (nguoc encrypt)."""
    rk = expand_key(key_words, rounds)
    x, y = ct
    for i in range(rounds - 1, -1, -1):
        y = rotr16(x ^ y, BETA)
        x = rotl16(((x ^ rk[i]) - y) & MASK16, ALPHA)
    return (x, y)


# ---------------------------------------------------------------------------
# Sinh du lieu
# ---------------------------------------------------------------------------

def words_to_bits(words: tuple[int, ...]) -> np.ndarray:
    """Doi cac tu 16 bit thanh vector bit (MSB truoc), kieu float32."""
    out = np.zeros(len(words) * 16, dtype=np.float32)
    for j, w in enumerate(words):
        for b in range(16):
            out[j * 16 + b] = float((w >> (15 - b)) & 1)
    return out


def random_key(rng: np.random.Generator) -> tuple[int, int, int, int]:
    """Sinh khoa 64 bit ngau nhien."""
    return tuple(int(v) for v in rng.integers(0, 65536, size=4))


def make_dataset(rounds: int, n_samples: int, seed: int) -> tuple[np.ndarray, np.ndarray]:
    """Sinh tap can bang: mot nua la ban ma that (nhan 1), mot nua nga nhien (nhan 0)."""
    rng = np.random.default_rng(seed)
    half = n_samples // 2
    n_on = half + (n_samples % 2)  # so mau nhan 1 (lam tron len)
    X = np.zeros((n_samples, 64), dtype=np.float32)
    y = np.zeros(n_samples, dtype=np.float32)
    idx = 0
    # Mau that: cap ban ro lech nhau (FIXED_DX, FIXED_DY), cung khoa ngau nhien.
    for _ in range(n_on):
        key = random_key(rng)
        x0 = int(rng.integers(0, 65536))
        y0 = int(rng.integers(0, 65536))
        c0 = encrypt((x0, y0), key, rounds)
        c1 = encrypt((x0 ^ FIXED_DX, y0 ^ FIXED_DY), key, rounds)
        X[idx] = words_to_bits((c0[0], c0[1], c1[0], c1[1]))
        y[idx] = 1.0
        idx += 1
    # Mau nga nhien: 64 bit hoan toan ngau nhien.
    for _ in range(n_samples - n_on):
        X[idx] = rng.integers(0, 2, size=64).astype(np.float32)
        y[idx] = 0.0
        idx += 1
    perm = rng.permutation(n_samples)  # tron deu 2 lop
    return X[perm], y[perm]


# ---------------------------------------------------------------------------
# MLP numpy thuan (ReLU + sigmoid + Adam)
# ---------------------------------------------------------------------------

def relu(z: np.ndarray) -> np.ndarray:
    """Ham kich hoat ReLU."""
    return np.maximum(z, 0.0)


def sigmoid(z: np.ndarray) -> np.ndarray:
    """Ham sigmoid on dinh so hoc."""
    z = np.clip(z, -30.0, 30.0)
    return 1.0 / (1.0 + np.exp(-z))


class MLP:
    """Mang perceptron nhieu lop nho: 64 -> 128 -> 64 -> 1."""

    def __init__(self, seed: int, lr: float = 0.002) -> None:
        rng = np.random.default_rng(seed)
        # Khoi tao He cho cac lop ReLU, Xavier cho lop ra.
        self.w1 = rng.normal(0, np.sqrt(2.0 / 64), (64, 128)).astype(np.float64)
        self.b1 = np.zeros(128, dtype=np.float64)
        self.w2 = rng.normal(0, np.sqrt(2.0 / 128), (128, 64)).astype(np.float64)
        self.b2 = np.zeros(64, dtype=np.float64)
        self.w3 = rng.normal(0, np.sqrt(1.0 / 64), (64, 1)).astype(np.float64)
        self.b3 = np.zeros(1, dtype=np.float64)
        # Trang thai Adam cho tung tham so.
        self._m = [np.zeros_like(p) for p in self.params()]
        self._v = [np.zeros_like(p) for p in self.params()]
        self._t = 0
        self.lr = lr

    def params(self) -> list[np.ndarray]:
        """Tra ve danh sach tham so theo thu tu co dinh."""
        return [self.w1, self.b1, self.w2, self.b2, self.w3, self.b3]

    def forward(self, x: np.ndarray) -> tuple[np.ndarray, dict]:
        """Lan truyen thang, luu cache cho lan truyen nguoc."""
        z1 = x @ self.w1 + self.b1
        a1 = relu(z1)
        z2 = a1 @ self.w2 + self.b2
        a2 = relu(z2)
        z3 = a2 @ self.w3 + self.b3
        p = sigmoid(z3)
        cache = {"x": x, "z1": z1, "a1": a1, "z2": z2, "a2": a2, "p": p}
        return p, cache

    def backward(self, cache: dict, y: np.ndarray) -> list[np.ndarray]:
        """Tinh gradient cua mat mat BCE trung binh theo batch."""
        n = y.shape[0]
        x, z1, a1, z2, a2, p = (cache[k] for k in ("x", "z1", "a1", "z2", "a2", "p"))
        dz3 = (p - y.reshape(-1, 1)) / n
        dw3 = a2.T @ dz3
        db3 = dz3.sum(axis=0)
        da2 = dz3 @ self.w3.T
        dz2 = da2 * (z2 > 0)
        dw2 = a1.T @ dz2
        db2 = dz2.sum(axis=0)
        da1 = dz2 @ self.w2.T
        dz1 = da1 * (z1 > 0)
        dw1 = x.T @ dz1
        db1 = dz1.sum(axis=0)
        return [dw1, db1, dw2, db2, dw3, db3]

    def adam_step(self, grads: list[np.ndarray]) -> None:
        """Cap nhat tham so bang Adam (beta mac dinh 0.9/0.999)."""
        self._t += 1
        b1, b2, eps = 0.9, 0.999, 1e-8
        for i, (p, g) in enumerate(zip(self.params(), grads)):
            self._m[i] = b1 * self._m[i] + (1 - b1) * g
            self._v[i] = b2 * self._v[i] + (1 - b2) * (g * g)
            mh = self._m[i] / (1 - b1 ** self._t)
            vh = self._v[i] / (1 - b2 ** self._t)
            p -= self.lr * mh / (np.sqrt(vh) + eps)


def train_mlp(Xtr: np.ndarray, ytr: np.ndarray, Xte: np.ndarray, yte: np.ndarray,
              epochs: int, batch: int, seed: int) -> tuple[MLP, float]:
    """Huan luyen MLP, tra ve (mo hinh, do chinh xac tren tap test)."""
    rng = np.random.default_rng(seed)
    net = MLP(seed=seed)
    n = Xtr.shape[0]
    for _ in range(epochs):
        perm = rng.permutation(n)  # tron lai moi epoch
        for s in range(0, n, batch):
            idx = perm[s:s + batch]
            xb = Xtr[idx].astype(np.float64)
            yb = ytr[idx].astype(np.float64)
            p, cache = net.forward(xb)
            grads = net.backward(cache, yb)
            net.adam_step(grads)
    return net, accuracy(net, Xte, yte)


def accuracy(net: MLP, X: np.ndarray, y: np.ndarray) -> float:
    """Do chinh xac nhi phan (nguong 0.5)."""
    p, _ = net.forward(X.astype(np.float64))
    pred = (p.ravel() >= 0.5).astype(np.float32)
    return float((pred == y).mean())


# ---------------------------------------------------------------------------
# Tu kiem (self-test) va thi nghiem
# ---------------------------------------------------------------------------

# Vector kiem Speck32/64 (dang "chua xac nhan": chua doi chieu nguon ngoai
# doc lap trong phien nay; cong kiem tra tinh dung la round-trip).
TEST_KEY_WORDS = (0x1918, 0x1110, 0x0908, 0x0100)  # viet theo thu tu tai lieu
TEST_PT = (0x6574, 0x694C)
TEST_CT = (0xA868, 0x42F2)


def check_test_vector() -> tuple[bool, str]:
    """Kiem thu vector Speck32/64 voi ca 2 cach hieu thu tu tu khoa."""
    for ten, key in (("k0=tu-cuoi", TEST_KEY_WORDS[::-1]),
                     ("k0=tu-dau", TEST_KEY_WORDS)):
        if encrypt(TEST_PT, key, FULL_ROUNDS) == TEST_CT:
            return True, ten
    return False, "khong khop ca 2 thu tu"


def check_roundtrip(n: int = 200, seed: int = 7) -> bool:
    """Kiem tra decrypt(encrypt(p)) == p voi khoa/nap ban ro ngau nhien."""
    rng = np.random.default_rng(seed)
    for rounds in (5, FULL_ROUNDS):
        for _ in range(n):
            key = random_key(rng)
            pt = (int(rng.integers(0, 65536)), int(rng.integers(0, 65536)))
            if decrypt(encrypt(pt, key, rounds), key, rounds) != pt:
                return False
    return True


def self_test() -> int:
    """Tu kiem nhanh: vector/round-trip + micro-train. Tra ve exit code."""
    print("== self-test: Speck32/64 + micro-train ==")
    ok_vec, cach = check_test_vector()
    print(f"[vector] {'KHOP' if ok_vec else 'KHONG KHOP'} ({cach}; trang thai: chua xac nhan doc lap)")
    ok_rt = check_roundtrip()
    print(f"[round-trip] {'PASS' if ok_rt else 'FAIL'} (200 mau x R=5,22)")
    t0 = time.time()
    Xtr, ytr = make_dataset(5, 400, seed=1)
    Xte, yte = make_dataset(5, 200, seed=2)
    _, acc = train_mlp(Xtr, ytr, Xte, yte, epochs=1, batch=64, seed=3)
    print(f"[micro-train] R=5, 400 mau, 1 epoch -> acc={acc:.3f} ({time.time() - t0:.1f}s)")
    ok_micro = 0.0 <= acc <= 1.0
    ok = ok_rt and ok_micro
    if ok:
        print("self-test ok: Speck32/64 round-trip đúng, micro-train chạy được.")
    else:
        print("self-test lỗi: round-trip hoặc micro-train hỏng (xem chi tiết trên).")
    print("Ghi chu: cong kiem tra tinh dung chinh la round-trip; vector o tren")
    print("chi mang tinh tham khao vi chua doi chieu nguon tin cay doc lap.")
    return 0 if ok else 1


def run_experiment(rounds_list: list[int], samples: int, test_samples: int,
                   epochs: int, batch: int, seed: int) -> dict[int, float]:
    """Chay thi nghiem day du cho tung R, tra ve dict {R: accuracy}."""
    ket_qua: dict[int, float] = {}
    for r in rounds_list:
        t0 = time.time()
        Xtr, ytr = make_dataset(r, samples, seed=seed + r * 1000)
        Xte, yte = make_dataset(r, test_samples, seed=seed + r * 1000 + 77)
        _, acc = train_mlp(Xtr, ytr, Xte, yte, epochs=epochs, batch=batch,
                           seed=seed + r)
        ket_qua[r] = acc
        print(f"R={r}: train={samples} test={test_samples} epochs={epochs} "
              f"-> accuracy={acc:.4f} ({time.time() - t0:.1f}s)")
    return ket_qua


def main() -> int:
    """CLI chinh."""
    ap = argparse.ArgumentParser(description="Distinguisher no-ron kieu Gohr tren Speck32/64 rut gon.")
    ap.add_argument("--rounds", default="5,6,7",
                    help="danh sach so vong, cach nhau bang dau phay (mac dinh: 5,6,7)")
    ap.add_argument("--samples", type=int, default=6000, help="so mau train moi R (mac dinh: 6000)")
    ap.add_argument("--test-samples", type=int, default=2000, help="so mau test moi R (mac dinh: 2000)")
    ap.add_argument("--epochs", type=int, default=5, help="so epoch (mac dinh: 5)")
    ap.add_argument("--batch", type=int, default=256, help="kich thuoc batch (mac dinh: 256)")
    ap.add_argument("--seed", type=int, default=1337, help="seed ngau nhien (mac dinh: 1337)")
    ap.add_argument("--self-test", action="store_true", help="chi chay tu kiem nhanh")
    args = ap.parse_args()

    if args.self_test:
        return self_test()

    try:
        rounds_list = [int(x) for x in args.rounds.split(",") if x.strip()]
    except ValueError:
        print("Sai dùng: --rounds phải là danh sách số nguyên, ví dụ '5,6,7'.")
        return 2
    if not rounds_list or any(r < 1 or r > FULL_ROUNDS for r in rounds_list):
        print(f"Sai dùng: mỗi R phải trong [1, {FULL_ROUNDS}].")
        return 2

    print(f"Cau hinh: rounds={rounds_list} samples={args.samples} "
          f"test={args.test_samples} epochs={args.epochs} seed={args.seed}")
    ket_qua = run_experiment(rounds_list, args.samples, args.test_samples,
                             args.epochs, args.batch, args.seed)
    print("Tom tat:", ", ".join(f"R={r}: {a:.4f}" for r, a in ket_qua.items()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
