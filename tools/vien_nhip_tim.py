# -*- coding: utf-8 -*-
"""Một nhịp tim Viện Nghiên cứu (thay cho prompt cron thủ công).

Mỗi nhịp: đọc bảng Kanzo -> tìm thẻ kẹt (doing quá 30 phút, review quá
20 phút) -> bình luận gọi tối đa 3 thẻ (cách nhau 5s) -> ghi 1 dòng log.
KHÔNG bao giờ tạo agent mới, KHÔNG xóa thẻ, KHÔNG sửa việc của ai.

Chạy:  python tools/vien_nhip_tim.py [--dry-run]
Mã thoát: 0 xong (kể cả khi Kanzo sập, đã ghi log) · 2 sai cách dùng.
"""
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import kanzo  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
VIEN = ROOT / "vien-nghien-cuu"
DU_LIEU = "esp32-securitykey"
NGUONG_DOING_PHUT = 30
NGUONG_REVIEW_PHUT = 20
TOI_DA_GOI = 3
GIAN_CACH = 5

MA_AGENT = re.compile(r"NCKH-(\d{3})")


def ten_agent_the(tieu_de, phan_cong):
    """Tra tên agent từ mã NCKH trong tiêu đề thẻ."""
    m = MA_AGENT.search(tieu_de or "")
    if not m:
        return None, None
    ma = f"NCKH-{m.group(1)}"
    for a in phan_cong:
        if a.get("ma") == ma:
            return ma, a.get("ten", "")
    return ma, ""


def the_ket(tasks, bay_gio=None):
    """Lọc thẻ kẹt: (id, status, số phút kẹt, title, updated_at)."""
    bay_gio = bay_gio or datetime.now(timezone.utc)
    ra = []
    for t in tasks:
        trang_thai = t.get("status")
        if trang_thai not in ("doing", "review"):
            continue
        try:
            cap_nhat = datetime.fromisoformat(
                str(t.get("updated_at")).replace("Z", "+00:00"))
            if cap_nhat.tzinfo is None:
                cap_nhat = cap_nhat.replace(tzinfo=timezone.utc)
        except (ValueError, TypeError):
            continue
        phut = (bay_gio - cap_nhat).total_seconds() / 60
        nguong = (NGUONG_DOING_PHUT if trang_thai == "doing"
                  else NGUONG_REVIEW_PHUT)
        if phut >= nguong:
            ra.append({"id": t.get("id"), "status": trang_thai,
                       "phut": int(phut), "title": t.get("title", ""),
                       "updated_at": t.get("updated_at")})
    return sorted(ra, key=lambda x: -x["phut"])


def dong_log(gio, dem, hanh_dong):
    """Dựng 1 dòng log nhịp tim (dạng thuần để self-test được)."""
    cac_trang_thai = " ".join(f"{k} {v}" for k, v in
                              sorted(dem.items()) if v)
    return (f"{gio} | bang: tong {sum(dem.values())} ({cac_trang_thai}) "
            f"| hanh dong: {hanh_dong}")


def nhip_tim(dry_run=False):
    """Chạy 1 nhịp đầy đủ. Trả về mã thoát."""
    gio = datetime.now().strftime("%Y-%m-%d %H:%M")
    log_file = VIEN / "so-cai" / "NHIP-TIM.log"
    try:
        tasks = kanzo.lay_bang(DU_LIEU)
    except kanzo.KanzoLoi as e:
        dong = (f"{gio} | KANZO SAP ({e}); so file la chan ly, "
                f"khong chan viec | hanh dong: khong")
        if not dry_run:
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(dong + "\n")
        print(dong)
        return 0
    dem = {}
    for t in tasks:
        dem[t.get("status", "?")] = dem.get(t.get("status", "?"), 0) + 1
    ket = the_ket(tasks)
    if not ket:
        dong = dong_log(gio, dem, "khong (khong the ket)")
        if not dry_run:
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(dong + "\n")
        print(dong)
        return 0
    phan_cong = json.loads(
        (VIEN / "phan-cong.json").read_text(encoding="utf-8-sig"))
    goi_duoc = []
    import time
    for i, the in enumerate(ket[:TOI_DA_GOI]):
        ma, ten = ten_agent_the(the["title"], phan_cong)
        goi = (f"[NHIP-TIM] The {the['status']} da {the['phut']} phut chua "
               f"cap nhat. {ma or ''} {ten or ''} vao viec hoac bao cao "
               f"tien do vao so cai.".strip())
        if dry_run:
            print(f"[DRY] comment the {the['id']}: {goi}")
            goi_duoc.append(str(the["id"]))
            continue
        try:
            kanzo.binh_luan(the["id"], goi)
            goi_duoc.append(str(the["id"]))
        except kanzo.KanzoLoi as e:
            print(f"goi the {the['id']} hong: {e}")
        if i < min(len(ket), TOI_DA_GOI) - 1:
            time.sleep(GIAN_CACH)
    dong = dong_log(gio, dem, f"goi {len(goi_duoc)}/{len(ket)} the ket "
                              f"({','.join(goi_duoc) or 'hong het'})")
    if not dry_run:
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(dong + "\n")
    print(dong)
    return 0


def tu_kiem():
    """Self-test offline: tìm thẻ kẹt + dựng dòng log (không mạng, không ghi)."""
    now = datetime(2026, 11, 21, 12, 0, tzinfo=timezone.utc)
    tasks = [
        {"id": 1, "status": "doing", "title": "viec A (NCKH-001)",
         "updated_at": "2026-11-21T11:20:00+00:00"},   # kẹt 40p
        {"id": 2, "status": "doing", "title": "viec B",
         "updated_at": "2026-11-21T11:50:00+00:00"},   # mới 10p
        {"id": 3, "status": "review", "title": "viec C (NCKH-002)",
         "updated_at": "2026-11-21T11:30:00+00:00"},   # kẹt 30p
        {"id": 4, "status": "todo", "title": "viec D",
         "updated_at": "2026-11-20T00:00:00+00:00"},   # todo bỏ qua
        {"id": 5, "status": "doing", "title": "viec E",
         "updated_at": "gio-hong"},                    # giờ hỏng bỏ qua
    ]
    ket = the_ket(tasks, now)
    assert [t["id"] for t in ket] == [1, 3], ket
    assert ket[0]["phut"] == 40 and ket[1]["phut"] == 30
    pc = [{"ma": "NCKH-001", "ten": "Nguyễn An"}]
    assert ten_agent_the("viec A (NCKH-001)", pc) == ("NCKH-001", "Nguyễn An")
    assert ten_agent_the("viec X", pc) == (None, None)
    dong = dong_log("2026-11-21 12:00", {"done": 50, "todo": 12}, "khong")
    assert "tong 62" in dong and "done 50" in dong and "todo 12" in dong
    print("self-test ok: tim the ket (doing>30p, review>20p), tra ten, dong log.")
    return 0


def main(argv=None):
    import argparse
    p = argparse.ArgumentParser(description="Chạy 1 nhịp tim Viện.")
    p.add_argument("--dry-run", action="store_true",
                   help="chỉ in hành động, không comment/không ghi log")
    p.add_argument("--self-test", action="store_true", help="tự kiểm offline")
    args = p.parse_args(argv)
    if args.self_test:
        return tu_kiem()
    return nhip_tim(args.dry_run)


if __name__ == "__main__":
    sys.exit(main())
