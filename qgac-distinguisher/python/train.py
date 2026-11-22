#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Huan luyen bo phan biet no-ron kieu Gohr bang PyTorch tu file .ndd.

Mo hinh: MLP 64 -> 128 -> 64 -> 1, ReLU + sigmoid (BCEWithLogits),
Adam lr=0.002 — port sang PyTorch cua lop MLP trong
tools/ml_distinguisher.py cua repo me.

Vi du:
    python python/train.py --data train-R5.ndd --epochs 5
    python python/train.py --data train-R5.ndd --test-data test-R5.ndd
    python python/train.py --self-test
"""

from __future__ import annotations

import argparse
import os
import sys
import tempfile
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np

try:
    import torch
    import torch.nn as nn
except ImportError:
    print("Thieu thu vien torch. Chay: pip install -r python/requirements.txt")
    raise SystemExit(2)

from ndd import doc_ndd, ghi_ndd, tu_thanh_bit


class MLP(nn.Module):
    """Mang perceptron nhieu lop nho: 64 -> 128 -> 64 -> 1."""

    def __init__(self) -> None:
        super().__init__()
        self.lop1 = nn.Linear(64, 128)
        self.lop2 = nn.Linear(128, 64)
        self.lop3 = nn.Linear(64, 1)
        # Khoi tao He cho cac lop ReLU, Xavier cho lop ra (nhu ban numpy).
        nn.init.kaiming_normal_(self.lop1.weight, nonlinearity="relu")
        nn.init.zeros_(self.lop1.bias)
        nn.init.kaiming_normal_(self.lop2.weight, nonlinearity="relu")
        nn.init.zeros_(self.lop2.bias)
        nn.init.xavier_normal_(self.lop3.weight)
        nn.init.zeros_(self.lop3.bias)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Lan truyen thang, tra ve logit (chua sigmoid)."""
        x = torch.relu(self.lop1(x))
        x = torch.relu(self.lop2(x))
        return self.lop3(x)


def do_chinh_xac(mo_hinh: MLP, x: torch.Tensor, y: torch.Tensor) -> float:
    """Do chinh xac nhi phan (nguong 0.5)."""
    mo_hinh.eval()
    with torch.no_grad():
        du_doan = (torch.sigmoid(mo_hinh(x)).ravel() >= 0.5).float()
        return float((du_doan == y).float().mean())


def nap_du_lieu(duong_dan: str) -> tuple[torch.Tensor, torch.Tensor]:
    """Nap file .ndd thanh (dac trung bit 64 chieu, nhan)."""
    goi = doc_ndd(duong_dan)
    x = torch.from_numpy(tu_thanh_bit(goi["tu"]))
    y = torch.from_numpy(goi["nhan"].astype(np.float32))
    return x, y


def huan_luyen(x_tr: torch.Tensor, y_tr: torch.Tensor,
               x_te: torch.Tensor, y_te: torch.Tensor,
               epochs: int, batch: int, seed: int) -> tuple[MLP, float]:
    """Huan luyen MLP, tra ve (mo hinh, do chinh xac tren tap test)."""
    dat_seed(seed)
    mo_hinh = MLP()
    mat_mat = nn.BCEWithLogitsLoss()
    toi_uu = torch.optim.Adam(mo_hinh.parameters(), lr=0.002)
    n = x_tr.shape[0]
    rng = np.random.default_rng(seed)
    for _ in range(epochs):
        hoan_vi = rng.permutation(n)  # tron lai moi epoch
        mo_hinh.train()
        for s in range(0, n, batch):
            idx = torch.from_numpy(hoan_vi[s:s + batch].astype(np.int64))
            toi_uu.zero_grad()
            logit = mo_hinh(x_tr[idx]).ravel()
            ton_that = mat_mat(logit, y_tr[idx])
            ton_that.backward()
            toi_uu.step()
    return mo_hinh, do_chinh_xac(mo_hinh, x_te, y_te)


def dat_seed(seed: int) -> None:
    """Dat seed xac dinh cho numpy va torch (CPU)."""
    np.random.seed(seed % (2 ** 32))
    torch.manual_seed(seed)


def tu_kiem() -> int:
    """Tu kiem nhanh: round-trip .ndd + micro-train tren du lieu tong hop."""
    print("== self-test: ndd.py + train.py (PyTorch) ==")
    rng = np.random.default_rng(0)
    tu = rng.integers(0, 65536, size=(64, 4)).astype(np.uint16)
    nhan = rng.integers(0, 2, size=64).astype(np.uint8)
    with tempfile.TemporaryDirectory() as tmp:
        duong_dan = os.path.join(tmp, "kiem.ndd")
        ghi_ndd(duong_dan, 5, 0, tu, nhan)
        goi = doc_ndd(duong_dan)
    ok_doc = (goi["rounds"] == 5 and np.array_equal(goi["tu"], tu)
              and np.array_equal(goi["nhan"], nhan))
    print(f"[ndd round-trip] {'PASS' if ok_doc else 'FAIL'}")
    x = torch.from_numpy(tu_thanh_bit(tu))
    y = torch.from_numpy(nhan.astype(np.float32))
    t0 = time.time()
    _, acc = huan_luyen(x[:48], y[:48], x[48:], y[48:],
                        epochs=1, batch=16, seed=3)
    print(f"[micro-train] 48 mau tong hop, 1 epoch -> acc={acc:.3f} "
          f"({time.time() - t0:.1f}s)")
    ok = ok_doc and 0.0 <= acc <= 1.0
    print("self-test ok." if ok else "self-test LOI.")
    return 0 if ok else 1


def main() -> int:
    """CLI chinh."""
    ap = argparse.ArgumentParser(
        description="Huan luyen MLP distinguisher kieu Gohr tu file .ndd.")
    ap.add_argument("--data", default=None,
                    help="file .ndd train (bat buoc neu khong --self-test)")
    ap.add_argument("--test-data", default=None,
                    help="file .ndd test (mac dinh: tach 20%% tu --data)")
    ap.add_argument("--rounds", type=int, default=5,
                    help="chi dung de in thong tin (R that nam trong file)")
    ap.add_argument("--samples", type=int, default=0,
                    help="gioi han so mau train lay tu file (0 = lay het)")
    ap.add_argument("--epochs", type=int, default=5, help="so epoch")
    ap.add_argument("--batch", type=int, default=256, help="kich thuoc batch")
    ap.add_argument("--seed", type=int, default=1337, help="seed")
    ap.add_argument("--self-test", action="store_true",
                    help="chi chay tu kiem nhanh")
    args = ap.parse_args()

    if args.self_test:
        return tu_kiem()
    if not args.data:
        print("Sai dung: thieu --data (hoac dung --self-test).")
        return 2

    t0 = time.time()
    x_tr, y_tr = nap_du_lieu(args.data)
    if args.samples > 0:
        x_tr, y_tr = x_tr[:args.samples], y_tr[:args.samples]
    if args.test_data:
        x_te, y_te = nap_du_lieu(args.test_data)
    else:  # tach 20% cuoi lam test
        cat = int(len(x_tr) * 0.8)
        x_tr, y_tr, x_te, y_te = x_tr[:cat], y_tr[:cat], x_tr[cat:], y_tr[cat:]
    _, acc = huan_luyen(x_tr, y_tr, x_te, y_te, args.epochs,
                        args.batch, args.seed)
    dt = time.time() - t0
    print(f"R~{args.rounds}: train={len(x_tr)} test={len(x_te)} "
          f"epochs={args.epochs} -> accuracy={acc:.4f} ({dt:.1f}s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
