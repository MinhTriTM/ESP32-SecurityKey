#!/usr/bin/env python3
"""Sinh danh sách 200 agent Viện + phân công 4 tầng. Chạy một lần khi lập viện.

Tầng 1: việc tay chọn theo nhóm. Tầng 2: rà soát từng file repo. Tầng 3: câu hỏi
nghiên cứu. Tầng 4: kiểm định cặp file (tài liệu-code-test có khớp nhau không).
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = Path(__file__).with_name("phan-cong.json")

HO = ["Nguyễn", "Trần", "Lê", "Phạm", "Hoàng", "Phan", "Vũ", "Võ", "Đặng", "Bùi",
      "Đỗ", "Hồ", "Ngô", "Dương", "Lý", "Đinh", "Trịnh", "Trương", "Mai", "Đoàn",
      "Hứa", "Lâm", "Chu", "Tạ", "Hà"]
TEN = ["An", "Bình", "Cường", "Dung", "Em", "Phúc", "Giang", "Hạnh", "Hùng", "Lan"]
NHOM = ["PQC", "ML", "firmware", "tooling", "tailieu", "kiemdinh"]

TIER1 = [
    # (nhóm, tiêu đề, mô tả)
    ("PQC", "Rà soát tools/pqc.py", "Đọc toàn bộ, kiểm API oqs đúng bản, nhánh lỗi, self-test đủ chưa. Báo cáo [KIEM-DINH]."),
    ("PQC", "So sánh ML-KEM-512/768/1024", "Đo kích thước khóa/bản mã và tốc độ keygen/encap/decap trên máy này. Khuyến nghị một bản cho vault."),
    ("PQC", "Đặc tả két lai X25519+ML-KEM", "Viết đặc tả định dạng két lai (chưa code): layout byte, thứ tự bọc khóa, cách mở khi một vế gãy."),
    ("PQC", "Khảo sát PQC trên ESP32-S3", "Thư viện PQC nào chạy được trên S3, tốn bao nhiêu RAM/flash. Kết luận có nên đưa vào firmware không."),
    ("PQC", "Bọc bản sao S bằng ML-KEM", "Thiết kế quy trình: mã hóa S dưới khóa công khai ML-KEM để lưu cloud, khóa bí mật chia Shamir."),
    ("PQC", "Benchmark liboqs trên máy", "Đo mọi KEM có trong liboqs, lập bảng so sánh, lưu số liệu quan sát được."),
    ("PQC", "Tài liệu đe dọa lượng tử", "Viết: khi có máy lượng tử mạnh thì phần nào của dự án vỡ, phần nào còn, thứ tự ưu tiên sửa."),
    ("PQC", "Kiểm thử chéo pqc self-test", "Gọi oqs trực tiếp bằng script riêng, so kết quả với self-test của tool."),
    ("PQC", "Nghiên cứu ký số PQC", "ML-DSA/SLH-DSA cái nào hợp để ký bản tin firmware sau này. So sánh kích thước chữ ký."),
    ("PQC", "Cài liboqs trên môi trường sạch", "Thử cài theo requirements-pqc trên venv mới, ghi mọi lỗi gặp và cách sửa."),
    ("ML", "Tái hiện ml_distinguisher", "Chạy full, ghi accuracy theo từng R, đối chiếu với số trong tài liệu."),
    ("ML", "Tăng mẫu lên 50k ở R=7", "Xem accuracy có vượt 0.5 không. Báo cáo trung thực kể cả thất bại."),
    ("ML", "Thử CNN 1D thay MLP", "Cùng dữ liệu và ngân sách, so accuracy với baseline MLP."),
    ("ML", "Tóm tắt Gohr 2019", "Đọc bài Gohr về Speck, chỉ ra khác biệt với thí nghiệm của ta."),
    ("ML", "Tài liệu distinguisher cho người mới", "Giải thích từ đầu: distinguisher là gì, vì sao chống được nó không phải bằng chứng an toàn."),
    ("ML", "Kiểm thử chéo Speck", "Vector chuẩn + round-trip + đối chiếu implement độc lập tự viết."),
    ("ML", "Thử R=8 ngân sách gấp 10", "Ghi nhận kết quả trung thực, ước tính chi phí nếu muốn lên R=9."),
    ("ML", "Rà soát pipeline dữ liệu", "Kiểm cân bằng lớp, rò rỉ tập test, seed ngẫu nhiên có cố định không."),
    ("ML", "Benchmark CPU vs GPU", "Cùng cấu hình train, so thời gian CPU và CUDA (nếu có)."),
    ("ML", "Đề xuất thí nghiệm tiếp theo", "Simon hay Skinny? Viết đề xuất kèm chi phí ước tính."),
    ("firmware", "Rà soát hwtest.ino", "Đọc toàn bộ: logic nút/LED/HID, race condition echoPending, tràn bộ đệm."),
    ("firmware", "Kiểm descriptor HID độc lập", "Tự viết script parse từng byte descriptor, đối chiếu report ID/độ dài với code."),
    ("firmware", "Runbook nạp hwtest Windows", "Từng bước có mô tả ảnh chụp, từ cắm cáp đến thấy log."),
    ("firmware", "Runbook nạp hwtest Ubuntu", "Tương tự bản Windows, gồm phân quyền serial và udev."),
    ("firmware", "Chốt mã module N16R8", "Đối chiếu chữ in shield với tài liệu Espressif, cập nhật BOM."),
    ("firmware", "Secure boot từ Arduino?", "Nghiên cứu xem Arduino-ESP32 có bật được secure boot/flash encryption không."),
    ("firmware", "So sánh USBMode OTG/HWCDC", "Bảng ảnh hưởng tới upload/log/HID, khuyến nghị khi nào dùng bản nào."),
    ("firmware", "Rà soát RAM/flash hai bản build", "Đề xuất cắt giảm nếu vượt ngưỡng, đo lại sau khi cắt."),
    ("firmware", "Checklist bring-up board mới", "Từ mở hộp đến echo ok, dạng checklist đánh dấu."),
    ("firmware", "Đọc trạng thái bảo mật bằng espefuse", "Viết hướng dẫn đọc secure boot/flash encryption từ chip."),
    ("tooling", "Rà soát fido_check đường lỗi", "Timeout, CID sai, rút thiết bị giữa chừng, GetInfo lỗi từng mã."),
    ("tooling", "Fuzz cbor_decode", "Input ngẫu nhiên + corpus, mọi crash đều phải thành ValueError có thông điệp."),
    ("tooling", "Rà soát hid_echo hai nền tảng", "Report ID có/không, thiết bị câm, payload biên 0/64 byte."),
    ("tooling", "Rà soát split_secret biên", "N=255, K=1, K=N, secret 1 byte và 1KB, file share hỏng."),
    ("tooling", "Fuzz parse_share", "Input rác chỉ được ném ValueError, không crash loại khác."),
    ("tooling", "Rà soát mnemonic input lạ", "Chữ hoa, khoảng trắng thừa, từ gần đúng, thiếu/thừa từ."),
    ("tooling", "Rà soát vault file hỏng", "Két cụt, salt/nonce sai dài, magic sai, mật khẩu rỗng."),
    ("tooling", "Rà soát lệnh qr hai tool", "File không tồn tại, thiếu lib (thử bằng cách đổi tên lib tạm thời)."),
    ("tooling", "Chuẩn hóa mã thoát tool", "Lập một bảng mã thoát và thông điệp chung cho mọi tool, sửa chỗ lệch."),
    ("tooling", "Test hiệu năng Shamir", "N=255/K=128 với secret 1KB mất bao lâu, có cần tối ưu không."),
    ("tailieu", "Rà soát liên kết gãy docs", "Quét mọi liên kết nội bộ trong docs, liệt kê và sửa chỗ gãy."),
    ("tailieu", "Sơ đồ kiến trúc ASCII", "Vẽ luồng Browser→OS→ESP32 cho 02-kien-truc.md."),
    ("tailieu", "Sơ đồ luồng khôi phục", "Vẽ 3 đường khôi phục cho 07."),
    ("tailieu", "Rà soát chính tả toàn repo", "Quét .md, sửa lỗi chính tả và thuật ngữ không nhất quán."),
    ("tailieu", "Viết FAQ dự án", "Gom câu hỏi đã gặp trong quá trình làm thành FAQ có trả lời."),
    ("tailieu", "Hướng dẫn môi trường dev Windows", "Từ máy trắng đến chạy được run_tests và build."),
    ("tailieu", "Hướng dẫn môi trường dev Ubuntu", "Tương tự bản Windows."),
    ("tailieu", "Ghi chú tuân thủ giấy phép", "MIT repo mình vs AGPL pico-fido: được/không được làm gì."),
    ("tailieu", "Tóm tắt dự án 1 trang", "Người mới đọc 5 phút hiểu toàn bộ dự án."),
    ("tailieu", "Bảng thuật ngữ Việt-Anh", "Mọi thuật ngữ dùng trong repo, một nghĩa duy nhất."),
    ("kiemdinh", "Chạy run_tests tiến trình sạch", "Ghi toàn bộ output, xác nhận 5 self-test xanh."),
    ("kiemdinh", "Build sạch hai chế độ", "Xóa cache arduino rồi build OTG+HWCDC để chắc tái hiện được."),
    ("kiemdinh", "Kiểm chéo Shamir độc lập", "Tự viết GF(256) riêng, so kết quả chia/ghép với tool."),
    ("kiemdinh", "Vector BIP-39 bổ sung", "Tra thêm vector 24 từ chuẩn, chạy qua tool mnemonic."),
    ("kiemdinh", "Đối chiếu vault với openssl", "PBKDF2+AES-GCM bằng openssl CLI, so khớp với tool."),
    ("kiemdinh", "Quét secret lọt repo", "Tìm mật khẩu/khóa/bí mật thật trong file, báo cáo hoặc xác nhận sạch."),
    ("kiemdinh", "Kiểm .gitignore", "Xác nhận .tooling/build/__pycache__/ảnh QR đều bị loại."),
    ("kiemdinh", "Báo cáo bao phủ kiểm thử", "Cái gì đã test, cái gì chưa, theo từng tool và firmware."),
    ("kiemdinh", "Cài lib trên venv sạch", "Thử mọi requirements trên venv mới, ghi lỗi."),
    ("kiemdinh", "Danh sách rủi ro còn lại", "Xếp theo mức độ, mỗi rủi ro có cách giảm thiểu."),
]

TIER3 = [
    "So sánh YubiKey với key tự build: khác biệt bảo mật cụ thể từng điểm.",
    "Khảo sát SoloKeys/OpenSK: ba bài học áp dụng được cho dự án.",
    "Nghiên cứu tấn công vật lý lên ESP32-S3 đã công bố (glitching, side-channel).",
    "Khảo sát chính sách FIDO của Google/GitHub/Microsoft năm 2026.",
    "CTAP 2.3 có gì mới so với 2.1 liên quan đến dự án.",
    "Phần mềm passkey nguồn mở tương thích với key của ta.",
    "Sao lưu thép: sản phẩm hiện có và phương pháp khắc 24 từ.",
    "Rủi ro khi truyền share qua ảnh QR và cách giảm.",
    "Mô hình đe dọa của Bluetooth/Quick Share khi chuyển share.",
    "esptool nâng cao: đọc flash, verify, giới hạn chống tấn công.",
    "Rust port cho vault/shamir: phân tích chi phí-lợi ích.",
    "Changelog pico-fido sau v8.2: có bản mới thì đánh giá có nên lên không.",
]

SKIP_DIRS = {".git", ".tooling", "__pycache__", "vien-nghien-cuu", "QGAC"}
EXTS = {".py", ".ino", ".md", ".ps1", ".sh"}


def tier2_files() -> list[str]:
    out = []
    for p in sorted(ROOT.rglob("*")):
        if not p.is_file() or p.suffix not in EXTS:
            continue
        if any(part in SKIP_DIRS for part in p.parts):
            continue
        out.append(p.relative_to(ROOT).as_posix())
    return out


def main() -> None:
    files = tier2_files()
    queues: dict[str, list[dict]] = {g: [] for g in NHOM}
    for nhom, tieu_de, mo_ta in TIER1:
        queues[nhom].append({"tieu_de": tieu_de, "mo_ta": mo_ta, "loai": "t1-tay-chon"})
    t2 = [{"tieu_de": f"Rà soát chéo file {f}",
           "mo_ta": f"Đọc toàn bộ {f}, tìm lỗi logic và trường hợp biên, báo cáo [KIEM-DINH].",
           "loai": "t2-theo-file"} for f in files]
    t3pos, t4pos = 0, 0
    roster = []
    for i in range(1, 201):
        ten = f"{HO[(i - 1) % len(HO)]} {TEN[((i - 1) // len(HO)) % len(TEN)]}"
        nhom = NHOM[(i - 1) % len(NHOM)]
        vai_tro = "nhóm trưởng" if i <= 6 else ("kiểm định viên" if nhom == "kiemdinh" else "thành viên")
        dot = 1 if i <= 12 else (2 if i <= 56 else (3 if i <= 128 else 4))
        if queues[nhom]:
            nv = queues[nhom].pop(0)
        elif t2:
            nv = t2.pop(0)
        elif t3pos < len(TIER3):
            nv = {"tieu_de": f"Nghiên cứu: {TIER3[t3pos][:60]}…", "mo_ta": TIER3[t3pos], "loai": "t3-nghien-cuu"}
            t3pos += 1
        else:
            a, b = files[t4pos % len(files)], files[(t4pos * 7 + 3) % len(files)]
            nv = {"tieu_de": f"Kiểm cặp {a} ↔ {b}",
                  "mo_ta": f"Đối chiếu {a} với {b}: tài liệu-code-test có khớp nhau không, lệch đâu báo đó.",
                  "loai": "t4-theo-cap"}
            t4pos += 1
        roster.append({"ma": f"NCKH-{i:03d}", "ten": ten, "nhom": nhom,
                       "vai_tro": vai_tro, "dot": dot, "nhiem_vu": nv})
    OUT.write_text(json.dumps(roster, ensure_ascii=False, indent=1), encoding="utf-8")
    from collections import Counter
    print(f"agent={len(roster)} file-t2={len(files)} t3={t3pos} t4={t4pos}")
    print("dot:", dict(Counter(a["dot"] for a in roster)))
    print("loai:", dict(Counter(a["nhiem_vu"]["loai"] for a in roster)))


if __name__ == "__main__":
    main()
