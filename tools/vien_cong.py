# -*- coding: utf-8 -*-
"""Chấm cổng 1 đợt Viện từ sổ cái (nguồn chân lý, không phụ thuộc Kanzo).

Đọc phân công + sổ NCKH-*.md, suy trạng thái mỗi agent (làm xong / chờ
xét / xong / cần sửa / chưa mở), rồi kết luận cổng đợt ĐẠT hay CHƯA.
Tái dùng bộ phân tích của tools/vien_dashboard.py nên logic 2 nơi khớp nhau.

Chạy:  python tools/vien_cong.py --dot 2
Mã thoát: 0 cổng ĐẠT · 1 còn việc dở (liệt kê) · 2 sai cách dùng.
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import vien_dashboard as vd  # noqa: E402


def cham_cong(dot):
    """Trả về (dat_bool, ds_agent_dot, ds_vuong)."""
    # Chấm cổng KHÔNG đụng mạng: sổ cái là nguồn chân lý (QD-003).
    du_lieu = vd.xay_du_lieu(thu_mang_kanzo=False)
    ds = sorted([h for h in du_lieu["agents"].values() if h["dot"] == dot],
                key=lambda h: h["ma"])
    vuong = [h for h in ds if h["status"] != "done"]
    return (not vuong and bool(ds)), ds, vuong


def mo_ta_vuong(h):
    """1 dòng vì sao agent này chặn cổng."""
    if not h["ledger"]:
        return "chua co so (chua mo hoac chua nhan viec)"
    if h["status"] == "doing":
        return "dang lam, chua bao cao"
    if h["status"] == "review":
        return "da bao cao, chua co verdict kiem cheo"
    if h["status"] == "sua":
        return f"bi KHONG DAT (xet boi {[x['ma'] for x in h['reviewed_by']]})"
    return h["status"]


def main(argv=None):
    p = argparse.ArgumentParser(description="Chấm cổng 1 đợt Viện.")
    p.add_argument("--dot", type=int, default=None, help="số đợt (1-4)")
    p.add_argument("--self-test", action="store_true", help="tự kiểm offline")
    args = p.parse_args(argv)
    if args.self_test:
        return tu_kiem()
    if args.dot is None:
        print("thiếu --dot N (1-4)", file=sys.stderr)
        return 2
    dat, ds, vuong = cham_cong(args.dot)
    print(f"đợt {args.dot}: {len(ds) - len(vuong)}/{len(ds)} agent done")
    for h in ds:
        dau = "x" if h["status"] == "done" else " "
        print(f"  [{dau}] {h['ma']} {h['ten']} ({h['nhom']}): {h['status']}")
    if dat:
        print(f"CỔNG ĐỢT {args.dot}: ĐẠT")
        return 0
    print(f"CỔNG ĐỢT {args.dot}: CHƯA ĐẠT — còn {len(vuong)} việc:")
    for h in vuong:
        print(f"  - {h['ma']} {h['ten']}: {mo_ta_vuong(h)}")
    return 1


def tu_kiem():
    """Self-test offline trên dữ liệu thật (chỉ đọc)."""
    dat1, ds1, _ = cham_cong(1)
    assert dat1 and len(ds1) == 12, f"đợt 1 phải 12/12 done"
    dat2, ds2, vuong2 = cham_cong(2)
    assert len(ds2) == 44, f"đợt 2 phải 44 agent, thấy {len(ds2)}"
    # Đợt 2 đã chốt cổng ĐẠT (QD-004/005) — nếu self-test hỏng ở đây thì
    # sổ sách và quyết định lệch nhau, phải điều tra.
    assert dat2, f"đợt 2 còn vướng: {[h['ma'] for h in vuong2]}"
    print("self-test ok: đợt 1 (12/12) và đợt 2 (44/44) đều ĐẠT.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
