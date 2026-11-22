# Sổ cái NCKH-037 — Hồ Bình (nhóm PQC, đợt 2B)

## 2026-11-21 02:22 — nhận việc
- Việc: Tài liệu đe dọa lượng tử (mục NCKH-037 trong phan-cong.json, loại t1-tay-chon)
- Mô tả: Viết — khi có máy lượng tử mạnh thì phần nào của dự án vỡ, phần nào còn, thứ tự ưu tiên sửa.
- File tạo: docs/de-doa-luong-tu.md (FILE MỚI duy nhất của việc này)
- Đã đọc: vien-nghien-cuu/HIEN-CHUONG.md, mục NCKH-037 trong vien-nghien-cuu/phan-cong.json,
  vien-nghien-cuu/so-cai/README.md, docs/06-bao-mat.md (+ docs/07-sao-luu-va-khoi-phuc.md,
  vien-nghien-cuu/NHIP-TIM.md, tools/vault.py, tools/pqc.py để đối chiếu crypto thực tế)
- Trạng thái: todo -> doing

## 2026-11-21 02:30 — báo cáo
- Đã làm: tạo docs/de-doa-luong-tu.md (1326 chữ): nhóm vỡ (ECDSA/ECDH P-256 của
  FIDO+PIN, chữ ký Secure Boot — Shor), nhóm còn (AES-256-GCM két, SHA-256/512,
  Shamir GF(256) miễn nhiễm tuyệt đối, cụm 24 từ BIP-39, mã hóa flash — Grover
  chỉ còn ~128 bit), bảng tổng hợp, 4 ưu tiên sửa (1-theo dõi chuẩn PQC FIDO,
  2-giữ hầm đối xứng, 3-vận hành 3 đường khôi phục, 4-dài hạn ML-KEM lai).
- Đối chiếu crypto thực tế: tools/vault.py (AESGCM + PBKDF2-SHA256 600k vòng),
  tools/mnemonic.py (SHA-256 checksum, PBKDF2-SHA512), tools/split_secret.py
  (Shamir GF(256)), tools/pqc.py (ML-KEM-768).
- Tự kiểm: đọc lại file, đủ 3 yêu cầu (phần vỡ — ECDH/PIN FIDO, phần còn —
  AES/SHA/Shamir, thứ tự ưu tiên); chỉ tạo đúng 1 file deliverable mới.
- Trạng thái: doing -> review (chờ đồng bộ Kanzo)

## 2026-11-21 02:35 — đồng bộ Kanzo
- GET /api/board?project=esp32-securitykey: thành công ngay lần 1, 32 thẻ.
- Tìm 'NCKH-037' trong title/description: KHÔNG thấy thẻ nào.
- Tìm mở rộng ('Hồ Bình|lượng tử|PQC|037'): chỉ thấy 6 thẻ PQC đợt 1 đã done
  (id 138, 145, 153, 159, 163) + 1 thẻ FIX-tooling (id 169, todo) — không có thẻ
  của NCKH-037.
- Quyết định: KHÔNG tự tạo thẻ (đúng lệnh), không move/comment. Việc xong ở
  phía file, chờ Viện trưởng/nhịp tim tạo thẻ và đối chiếu sổ.
- Trạng thái: doing -> review (file xong, thẻ chưa có để đồng bộ)

## 2026-11-21 — kiểm chéo đợt 2B: thẻ NCKH-029 Phạm Bình (docs/FAQ.md)

- Vai: Hồ Bình (NCKH-037) kiểm độc lập FAQ 91 câu/10 nhóm của Phạm Bình
  (NCKH-029). Đã đọc `vien-nghien-cuu/so-cai/NCKH-029.md` + toàn bộ `docs/FAQ.md`.
- Cách kiểm (đường khác, shell pwsh): đếm độc lập + mở nguồn được trích để
  đối chiếu từng con số, không chạy lại script của tác giả.
- Đếm: `###` = 91 câu; `## 1..10` = 10 nhóm khớp đúng 10 dòng mục lục;
  23 link duy nhất = 13 link file tồn tại đủ 13/13 + 10 anchor nội bộ;
  bảng unresolved = 15 dòng. Khớp báo cáo của tác giả.
- Mẫu xác minh ngẫu nhiên 10/91 (mở nguồn gốc, khớp 10/10):
  1. Pico-fido v8.2/commit 15b848d/IDF v5.5.1/AGPL ↔ `docs/04-firmware.md` — khớp.
  2. N16R8 chốt, N26R8 ghi nhầm, ảnh 62256 + PDF tr.53 ↔ `hardware/BOM.md` — khớp.
  3. USB CDC On Boot / USB-OTG / `HID echo: TAT` / `USB mode: 1` ↔ 2 runbook — khớp.
  4. Race `echoPending` (USB ctx vs loop, portMUX/2 ngăn, test 60B ok) ↔ NCKH-003 — khớp.
  5. `dialout` + đăng nhập lại, cấm chmod 666/sudo, brltty, ModemManager ↔ runbook
     Ubuntu — khớp từng lệnh.
  6. S 32 byte, 3 đường khôi phục, Shamir 3/5, BIP-39 24 từ + 2^256 ↔ `docs/07` — khớp.
  7. Fuzz cbor 5639 case / 30 sai loại / 0,53% / unhashable / RecursionError /
     cụt thân ↔ NCKH-010 — khớp.
  8. ML-KEM-768 pk 1184/sk 2400/ct 1088/ss 32/NIST level 3 ↔ NCKH-007 — khớp.
  9. ml_distinguisher 0.5970/0.5245/0.5070 seed 1337 MLP 64→128→64→1 ↔ NCKH-002
     + `research/06` — khớp.
  10. Gohr 2019: chênh lệch (0x0040,0x0000), nhãn 0 khác, ResNet vs MLP,
      10M vs 6k mẫu, k0 = từ cuối ↔ NCKH-020 — khớp.
- Lưu ý nhỏ (không ảnh hưởng kết luận): `docs/03-phan-cung.md` vẫn còn câu cũ
  "module được ghi là N26R8... Khả năng cao là N16R8" trong khi BOM đã chốt N16R8;
  FAQ trích đúng phía chốt (BOM + NCKH-027). Lệch này đã có NCKH-023 (B43) ghi nhận.
- Kết luận kiểm định: ĐẠT — review -> done (đề nghị).
- Đồng bộ Kanzo (KHÔNG đồng bộ được, đã ghi sổ): GET board (timeout 30s, cách 5s,
  shell pwsh): lần 1 trả về khó hiểu (parse được 1 card rỗng, không thấy NCKH-029),
  lần 2 và 3 đều HỎNG 500 Internal Server Error. Hết 2 lần thử lại theo lệnh.
  Không comment/move (không có id đích chắc chắn), không tự tạo thẻ.
  Nhờ Viện trưởng khi Kanzo sống lại: dán comment `[KIEM-DINH] đạt — Hồ Bình
  (NCKH-037): đếm 91 câu/10 nhóm/15 unresolved khớp; xác minh ngẫu nhiên 10 câu
  khớp nguồn 10/10` + move thẻ NCKH-029 review -> done giúp.

## Unresolved (lượt kiểm chéo NCKH-029)

1. Thẻ Kanzo NCKH-029 chưa xác nhận được (Kanzo 500) → nhờ Viện trưởng dán
   comment kiểm định + move review -> done giúp.
