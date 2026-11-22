# -*- coding: utf-8 -*-
"""Sinh dashboard HTML một file cho Viện Nghiên cứu từ sổ sách thật.

Đọc: vien-nghien-cuu/phan-cong.json, vien-nghien-cuu/so-cai/NCKH-*.md,
vien-nghien-cuu/QUYET-DINH.md, vien-nghien-cuu/so-cai/NHIP-TIM.log,
bảng Kanzo (kèm cache khi Kanzo sập).
Ghi: dashboard/vien.html (tự chứa, mở offline được) + dashboard/board_snapshot.json.

Chạy:  python tools/vien_dashboard.py   (từ thư mục gốc repo)
"""
import json
import re
import sys
import urllib.request
from datetime import datetime
from pathlib import Path

# Thư mục gốc repo suy từ vị trí script, không hardcode.
ROOT = Path(__file__).resolve().parent.parent
VIEN = ROOT / "vien-nghien-cuu"
SO_CAI = VIEN / "so-cai"
DASH = ROOT / "dashboard"
KANZO_BOARD = "http://100.101.100.100:4242/api/board?project=esp32-securitykey"

# Màu mỗi nhóm (mã nhóm -> mã màu hex), dùng xuyên suốt dashboard.
MAU_NHOM = {
    "firmware": "#f5b301",   # vàng hổ phách
    "tooling": "#4aa8ff",    # xanh dương
    "tailieu": "#3ddc84",    # xanh lá
    "kiemdinh": "#ff6b6b",   # đỏ
    "PQC": "#2dd4bf",        # xanh ngọc
    "ML": "#fb923c",         # cam
}

# Thư mục gốc hợp lệ trong repo (để nhận diện đường dẫn file).
TOP_DIR = ("tools/", "docs/", "firmware/", "scripts/", "hardware/", "config/",
           "vien-nghien-cuu/", ".tooling/", "dashboard/", "QGAC/")
KET_LUAN = re.compile(r"KIEM-DINH|kết luận", re.IGNORECASE)
TU_DAT = re.compile(r"KHÔNG ĐẠT|KHONG[ -]?DAT|ĐẠT|DAT\b", re.IGNORECASE)


def verdict_cua_doan(tieu_de, than_bai):
    """Verdict của một lượt xét: từ khóa kết luận CUỐI cùng quyết định."""
    ung_vien = []
    for m in KET_LUAN.finditer(than_bai):
        v = TU_DAT.search(than_bai, m.end(), min(m.end() + 60, len(than_bai)))
        if v:
            ung_vien.append(v.group(0))
    if ung_vien:
        cuoi = ung_vien[-1].upper()
        return "KHONG" if "KHÔNG" in cuoi or "KHONG" in cuoi else "DAT"
    # Dự phòng: verdict nằm ngay trong tiêu đề mục.
    t = tieu_de.upper()
    if "KHÔNG ĐẠT" in t or "KHONG DAT" in t or "KHONG-DAT" in t:
        return "KHONG"
    if "KIEM-DINH" in t and "DAT" in t:
        return "DAT"
    if re.search(r":\s*\*{0,2}ĐẠT\*{0,2}\s*$", tieu_de, re.IGNORECASE):
        return "DAT"
    return None
MA_AGENT = re.compile(r"NCKH-(\d{3})")
MOC_THOI_GIAN = re.compile(r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2})")
BACKTICK = re.compile(r"`([^`\n]{1,160})`")
# Động từ "viết" trên cùng dòng với đường dẫn -> coi là file agent tạo/sửa.
DONG_TU_VIET = re.compile(r"(tạo mới|viết mới|tạo file|thêm file|deliverable|file mới|"
                           r"xuất ra|lưu (vào|ra)|ghi ra|tạo ra)\w*", re.IGNORECASE)


def doc_bang_kanzo(thu_mang=True):
    """Đọc bảng Kanzo, hỏng thì dùng cache. Trả về (tasks, lay_moi_duoc)."""
    DASH.mkdir(exist_ok=True)
    cache = DASH / "board_snapshot.json"
    if not thu_mang:
        if cache.exists():
            return json.loads(cache.read_text(encoding="utf-8"))["tasks"], False
        return [], False
    for lan_thu in (1, 2):
        try:
            req = urllib.request.Request(KANZO_BOARD, headers={"Accept": "application/json"})
            with urllib.request.urlopen(req, timeout=30) as resp:
                du_lieu = json.loads(resp.read().decode("utf-8"))
            tasks = du_lieu.get("tasks", du_lieu if isinstance(du_lieu, list) else [])
            cache.write_text(json.dumps({"lay_luc": datetime.now().isoformat(timespec="minutes"),
                                         "tasks": tasks}, ensure_ascii=False), encoding="utf-8")
            return tasks, True
        except Exception as loi:  # noqa: BLE001 - Kanzo sập là chuyện thường
            print(f"  Kanzo lần {lan_thu} hỏng: {loi}")
            if lan_thu == 1:
                import time
                time.sleep(5)
    if cache.exists():
        print("  Dùng cache bảng Kanzo.")
        return json.loads(cache.read_text(encoding="utf-8"))["tasks"], False
    print("  Không có cache bảng.")
    return [], False


def chuan_hoa_duong_dan(tho, chi_muc_file=None):
    """Biến chuỗi thô thành đường dẫn tương đối trong repo, hoặc None."""
    s = tho.strip().strip("'\"").replace("\\", "/")
    # Đường dẫn TEMP (probe ngoài repo): giữ lại tên file để nhóm riêng.
    if "$" in s or "/Temp/" in s or "/TEMP/" in s or s.startswith("Temp/"):
        ten = s.rsplit("/", 1)[-1]
        return f"$TEMP/{ten}" if "." in ten else None
    # Cắt số dòng kiểu file.py:28 và dấu câu bám đuôi.
    s = re.sub(r":\d+(-\d+)?$", "", s).rstrip(".,;:!?)]}\"")
    if not s or len(s) > 180 or " " in s or "http" in s or "$" in s:
        return None
    # Cắt tiền tố tuyệt đối tới gốc repo nếu có.
    for mach in ("D:/Download/ESP32-SecurityKey/", "ESP32-SecurityKey/"):
        if mach in s:
            s = s.split(mach, 1)[1]
    s = s.lstrip("./")
    if "/" not in s and "." not in s:
        return None
    if s.startswith(TOP_DIR):
        return s
    # Tên file đơn lẻ: đối chiếu cây repo thật để gộp với đường dẫn đủ.
    m = re.fullmatch(r"[\w\-.+]+\.(py|md|ino|sh|ps1|txt|rules|json|png|jpg|dll|so|bin|hex|csv)", s)
    if m and chi_muc_file and s in chi_muc_file:
        return chi_muc_file[s]
    if m:
        return s
    return None


def lap_chi_muc_file():
    """Lập chỉ mục tên file -> đường dẫn cho tên KHÔNG trùng trong repo."""
    dem, duong = {}, {}
    bo_qua = {".git", "__pycache__", "node_modules", ".venv"}
    for p in ROOT.rglob("*"):
        if not p.is_file() or any(b in p.parts for b in bo_qua):
            continue
        try:
            rel = p.relative_to(ROOT).as_posix()
        except ValueError:
            continue
        dem[p.name] = dem.get(p.name, 0) + 1
        duong[p.name] = rel
    return {ten: duong[ten] for ten, n in dem.items() if n == 1}


def tach_muc_so(noi_dung):
    """Cắt sổ cái thành các mục theo dòng '## '. Trả về [(tieu_de, than_bai)]."""
    dong = noi_dung.split("\n")
    cac_muc, tieu_de, dem = [], None, []
    for d in dong:
        if d.startswith("## "):
            if tieu_de is not None:
                cac_muc.append((tieu_de, "\n".join(dem)))
            tieu_de, dem = d[3:].strip(), []
        elif tieu_de is not None:
            dem.append(d)
    if tieu_de is not None:
        cac_muc.append((tieu_de, "\n".join(dem)))
    return cac_muc


def phan_loai_muc(tieu_de):
    """Nhận diện loại mục sổ: nhanviec / baocao / kiemcheo / kanzo / unresolved / khac."""
    t = tieu_de.lower()
    if "nhận việc" in t:
        return "nhanviec"
    # "Unresolved (lượt kiểm chéo...)" là mục tồn đọng, KHÔNG phải lượt xét.
    if "unresolved" in t or "tồn đọng" in t:
        return "unresolved"
    # Mục đồng bộ Kanzo nhắc tới kiểm chéo (vd "Kanzo kiểm chéo thẻ 144").
    if "kanzo" in t or "đồng bộ" in t:
        return "kanzo"
    # "sửa ... theo kết luận kiểm chéo" là báo cáo sửa bài, không phải lượt xét cho.
    if "theo" in t and "kiểm chéo" in t:
        return "baocao"
    if "kiểm chéo" in t or "kiem-cheo" in t or "duyệt lại" in t:
        return "kiemcheo"
    if "báo cáo" in t:
        return "baocao"
    return "khac"


def trich_file_trong_muc(tieu_de, than_bai, chi_muc_file=None):
    """Trích mọi đường dẫn file trong mục, đoán quan hệ đọc/viết theo từng dòng."""
    tim_thay = {}
    for dong in (tieu_de + "\n" + than_bai).split("\n"):
        co_dong_tu_viet = bool(DONG_TU_VIET.search(dong))
        for m in BACKTICK.finditer(dong):
            p = chuan_hoa_duong_dan(m.group(1), chi_muc_file)
            if p:
                cu = tim_thay.get(p)
                moi = "wrote" if co_dong_tu_viet else "read"
                # "wrote" thắng "read" khi cùng file xuất hiện nhiều dòng.
                if cu != "wrote":
                    tim_thay[p] = moi
    return tim_thay


def the_cua_chinh_minh(noi_dung):
    """Đoán số thẻ Kanzo của chính chủ sổ (CHỈ từ mục nhận việc)."""
    thay = []
    for tieu_de, than_bai in tach_muc_so(noi_dung):
        # Chỉ tin mục nhận việc: mục xét/đồng bộ hay nhắc thẻ người khác
        # (vd người xét đồng bộ giúp thẻ của tác giả).
        if phan_loai_muc(tieu_de) != "nhanviec":
            continue
        thay += re.findall(r"thẻ (?:id )?#?(\d{2,4})", tieu_de + "\n" + than_bai)
        thay += re.findall(r"[Kk]anzo id (\d{2,4})", tieu_de + "\n" + than_bai)
    return thay


def doc_mot_so(ma, duong_dan, chi_muc_file=None, the_sang_ma=None):
    """Đọc một sổ cái, trả về dict timeline / lượt xét / verdict / file / unresolved."""
    noi_dung = duong_dan.read_text(encoding="utf-8-sig")
    timeline, da_xet, files = [], [], {}
    bao_cao_xong = nhan_viec = False
    unresolved = []
    for thu_tu, (tieu_de, than_bai) in enumerate(tach_muc_so(noi_dung)):
        loai = phan_loai_muc(tieu_de)
        moc = MOC_THOI_GIAN.search(tieu_de)
        timeline.append({"t": moc.group(1) if moc else "",
                         "kind": loai,
                         "title": tieu_de[:140]})
        if loai == "nhanviec":
            nhan_viec = True
        elif loai == "baocao":
            bao_cao_xong = True
        elif loai == "kiemcheo":
            # Mục tiêu là mã NCKH đầu tiên khác chính mình trong tiêu đề.
            # (KHÔNG đoán từ thân bài: dễ bắt nhầm mã nhắc chơi như NCKH-012.)
            ma_dich = [f"NCKH-{m}" for m in MA_AGENT.findall(tieu_de)
                       if f"NCKH-{m}" != ma]
            if not ma_dich and the_sang_ma:
                # Một số sổ cũ chỉ ghi số thẻ ("kiểm chéo thẻ 145").
                for so_the in re.findall(r"thẻ #?(\d{2,4})", tieu_de):
                    if int(so_the) in the_sang_ma:
                        ma_dich = [the_sang_ma[int(so_the)]]
                        break
            verdict = verdict_cua_doan(tieu_de, than_bai)
            if ma_dich:
                da_xet.append({"to": ma_dich[0], "verdict": verdict,
                               "ord": thu_tu})
            else:
                print(f"  CẢNH BÁO {ma}: lượt xét không rõ mục tiêu: {tieu_de[:80]}")
        elif loai == "unresolved":
            for dong in than_bai.split("\n"):
                d = dong.strip("- ").strip()
                if len(d) > 12:
                    unresolved.append(d[:160])
                if len(unresolved) >= 8:
                    break
        for p, qh in trich_file_trong_muc(tieu_de, than_bai, chi_muc_file).items():
            if files.get(p) != "wrote":
                files[p] = qh
    # Chính sổ cái của agent cũng là file nó viết.
    files[f"vien-nghien-cuu/so-cai/{ma}.md"] = "wrote"
    return {"timeline": timeline, "da_xet": da_xet, "files": files,
            "bao_cao_xong": bao_cao_xong, "nhan_viec": nhan_viec,
            "unresolved": unresolved[:8]}


def doc_cong_quyet_dinh():
    """Trích các quyết định QD-xxx từ QUYET-DINH.md."""
    cac_qd = []
    p = VIEN / "QUYET-DINH.md"
    if not p.exists():
        return cac_qd
    for m in re.finditer(r"^## (QD-\d+[^\n]*)\n((?:(?!^## ).*\n?)*)",
                         p.read_text(encoding="utf-8-sig"), re.MULTILINE):
        than = m.group(2)
        qd = re.search(r"Quyết định:\s*(.+?)(?:\n- |\n\n|\Z)", than, re.DOTALL)
        cac_qd.append({"id": m.group(1).strip(),
                       "text": re.sub(r"\s+", " ", qd.group(1)).strip()[:220]
                       if qd else ""})
    return cac_qd


def xay_du_lieu(thu_mang_kanzo=True):
    """Gom toàn bộ dữ liệu Viện thành một dict cho template."""
    phan_cong = json.loads((VIEN / "phan-cong.json").read_text(encoding="utf-8-sig"))
    tasks_bang, bang_tuoi = doc_bang_kanzo(thu_mang_kanzo)
    print(f"  Bảng Kanzo: {len(tasks_bang)} thẻ (tươi: {bang_tuoi}).")

    # Ánh xạ mã agent -> các thẻ Kanzo nhắc tới mã đó trong tiêu đề,
    # và ngược lại số thẻ -> mã (để giải mã lượt xét ghi theo số thẻ).
    the_theo_ma, the_sang_ma = {}, {}
    for t in tasks_bang:
        codes = MA_AGENT.findall(t.get("title", "") or "")
        if codes and t.get("id") not in the_sang_ma:
            the_sang_ma[t["id"]] = f"NCKH-{codes[0]}"
        for m in codes:
            the_theo_ma.setdefault(f"NCKH-{m}", []).append(
                {"id": t.get("id"), "status": t.get("status"),
                 "comments": t.get("comments", 0),
                 "title": (t.get("title", "") or "")[:90]})

    chi_muc_file = lap_chi_muc_file()
    # Lấp chỗ trống bản đồ thẻ->mã bằng lời khai trong chính các sổ
    # (đề phòng endpoint liệt kê bảng thiếu thẻ như đã từng xảy ra).
    nhan_the = {}
    for a in phan_cong:
        so = SO_CAI / f"{a['ma']}.md"
        if so.exists():
            for so_the in the_cua_chinh_minh(so.read_text(encoding="utf-8-sig")):
                nhan_the.setdefault(int(so_the), set()).add(a["ma"])
    for so_the, cac_ma in nhan_the.items():
        if so_the not in the_sang_ma and len(cac_ma) == 1:
            the_sang_ma[so_the] = next(iter(cac_ma))
    agents, reviews = {}, []
    for a in phan_cong:
        ma = a["ma"]
        ho_so = {"ma": ma, "ten": a.get("ten", ""), "nhom": a.get("nhom", ""),
                 "vai_tro": a.get("vai_tro", ""), "dot": a.get("dot", 0),
                 "nhiem_vu": a.get("nhiem_vu", {}), "status": "chuamo",
                 "ledger": False, "card": None, "cards": [],
                 "timeline": [], "files": [], "reviewed_by": [], "reviewed": [],
                 "unresolved": []}
        so = SO_CAI / f"{ma}.md"
        if so.exists():
            ho_so["ledger"] = True
            parsed = doc_mot_so(ma, so, chi_muc_file, the_sang_ma)
            ho_so["timeline"] = parsed["timeline"]
            ho_so["unresolved"] = parsed["unresolved"]
            ho_so["files"] = [{"path": p, "rel": qh}
                              for p, qh in sorted(parsed["files"].items())]
            ho_so["reviewed"] = parsed["da_xet"]
            for x in parsed["da_xet"]:
                reviews.append({"from": ma, "to": x["to"],
                                "verdict": x["verdict"], "ord": x["ord"]})
            ho_so["status"] = ("review" if parsed["bao_cao_xong"]
                               else "doing" if parsed["nhan_viec"] else "doing")
        agents[ma] = ho_so

    # Đảo chiều lượt xét: ai bị ai xét, verdict nhận được.
    # Cùng cặp xét nhiều lần (nhận xét rồi báo cáo xét): lượt SAU thắng.
    for r in reviews:
        if r["to"] in agents:
            agents[r["to"]]["reviewed_by"].append(
                {"ma": r["from"], "verdict": r["verdict"], "ord": r["ord"]})
    # Chốt trạng thái done/sửa theo verdict MỚI NHẤT đã nhận.
    for ma, h in agents.items():
        if not h["ledger"]:
            continue
        theo_nguoi = {}
        for x in sorted(h["reviewed_by"], key=lambda e: e["ord"]):
            if x["verdict"]:
                theo_nguoi[x["ma"]] = x["verdict"]
        vd = list(theo_nguoi.values())
        if "KHONG" in vd:
            h["status"] = "sua"
        elif "DAT" in vd and h["status"] == "review":
            h["status"] = "done"

    # Gắn thẻ Kanzo (thẻ chính = thẻ done đầu tiên, nếu không thì thẻ đầu).
    for ma, ds in the_theo_ma.items():
        if ma in agents:
            agents[ma]["cards"] = sorted(ds, key=lambda c: c["id"])
            dones = [c for c in ds if c["status"] == "done"]
            agents[ma]["card"] = (dones or ds)[0]

    # Bảng file: gom ngược từ agent -> file.
    files = {}
    for ma, h in agents.items():
        for f in h["files"]:
            e = files.setdefault(f["path"], {"readers": [], "writers": []})
            e["readers" if f["rel"] == "read" else "writers"].append(ma)
    ds_files = [{"path": p, "folder": (p.rsplit("/", 1)[0] if "/" in p else "(gốc)"),
                 "readers": sorted(set(v["readers"])),
                 "writers": sorted(set(v["writers"]))}
                for p, v in sorted(files.items())]

    # Hội đồng: Viện trưởng + nhóm trưởng các nhóm.
    truong_nhom = {}
    for a in phan_cong:
        if a.get("vai_tro") == "nhóm trưởng":
            truong_nhom.setdefault(a.get("nhom"), {"ma": a["ma"], "ten": a.get("ten", "")})

    log_file = SO_CAI / "NHIP-TIM.log"
    nhip_tim = (log_file.read_text(encoding="utf-8-sig").strip().split("\n")[-12:]
                if log_file.exists() else [])
    return {
        "meta": {"tao_luc": datetime.now().strftime("%Y-%m-%d %H:%M"),
                 "bang_tuoi": bang_tuoi, "so_the": len(tasks_bang)},
        "mau_nhom": MAU_NHOM,
        "agents": agents,
        "files": ds_files,
        "reviews": reviews,
        "gates": doc_cong_quyet_dinh(),
        "truong_nhom": truong_nhom,
        "nhip_tim": nhip_tim,
    }


def main():
    if not (VIEN / "phan-cong.json").exists():
        print("Thiếu vien-nghien-cuu/phan-cong.json (dữ liệu nội bộ, không public).")
        return 1
    du_lieu = xay_du_lieu()
    so_agent = len(du_lieu["agents"])
    so_so = sum(1 for h in du_lieu["agents"].values() if h["ledger"])
    print(f"  Agent: {so_agent}, có sổ: {so_so}, lượt xét: {len(du_lieu['reviews'])}, "
          f"file: {len(du_lieu['files'])}.")
    if so_agent != 200:
        raise ValueError(f"phân công phải đủ 200 agent, thấy {so_agent}")
    # Mọi lượt xét phải trỏ tới agent có thật.
    for r in du_lieu["reviews"]:
        if r["to"] not in du_lieu["agents"]:
            raise ValueError(f"lượt xét trỏ mã lạ: {r}")
    mau = (DASH / "template.html").read_text(encoding="utf-8")
    if "/*__VIEN_DATA__*/null" not in mau:
        raise ValueError("template thiếu điểm nhúng dữ liệu")
    payload = json.dumps(du_lieu, ensure_ascii=False)
    payload = payload.replace("<", "\\u003c").replace(">", "\\u003e")
    html = mau.replace("/*__VIEN_DATA__*/null", payload)
    ra = DASH / "vien.html"
    ra.write_text(html, encoding="utf-8")
    print(f"  Đã ghi {ra} ({ra.stat().st_size // 1024} KB).")


if __name__ == "__main__":
    sys.exit(main())

