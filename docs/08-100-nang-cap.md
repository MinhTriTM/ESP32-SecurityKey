# 100 nâng cấp dự án ESP32-S3 Security Key

> Ngày: 2026-11-21. Nguồn: toàn bộ sổ cái NCKH-001…056, thẻ FIX/DOC/OPS trên Kanzo,
> quyết định QD-001…005, và hiện trạng repo. Mỗi mục ghi rõ VÌ SAO + Ở ĐÂU + CỠ VIỆC.
> Cỡ việc: S (dưới 1 giờ) · M (nửa ngày–2 ngày) · L (trên 2 ngày hoặc cần phần cứng).
> Ưu tiên: P0 (chặn dùng thật) · P1 (nên làm sớm) · P2 (làm dần).

## Nhóm A — Firmware dùng thật pico-fido + hwtest (U001–U015)

- **U001 — Build pico-fido v8.2 kiểm chứng.** Chốt tag đã 2 tuần mà chưa ai build; phải xác nhận
  biên dịch sạch ESP-IDF v5.5.1 trước mọi hứa hẹn khác. Ở ĐÂU: repo pico-fido ngoài + `docs/04-firmware.md` ghi kết quả. Cỡ M, P0.
- **U002 — Bật Secure Boot V2 đúng `docs/04` (KHÔNG Flash Encryption).** Không có Secure Boot
  thì key chỉ là board dev gắn mác bảo mật; FE bị loại sau khi xác minh trên board thật
  (pico-fido v8.2 hỏng kho khi bật FE). Ở ĐÂU: `config/sdkconfig.hardened` + runbook ký. Cỡ M, P0.
- **U003 — Đọc trạng thái eFuse/bảo mật bằng `espefuse.py` (chỉ đọc).** Xác minh Secure Boot/Flash Encryption
  đã bật thật trước khi nạp credential. Ở ĐÂU: mục mới trong runbook bring-up. Cỡ S, P0.
- **U004 — Chính sách PIN/UV + giới hạn lần thử PIN.** CTAP2 cho phép brute-force PIN nếu triển khai ẩu;
  chốt số lần thử và hành vi khóa. Ở ĐÂU: cấu hình pico-fido + `docs/06-bao-mat.md`. Cỡ M, P0.
- **U005 — Resident key / discoverable credential.** Thiếu là không đăng nhập không-username được trên nhiều
  dịch vụ mới. Ở ĐÂU: cấu hình pico-fido, kiểm bằng `fido_check` mở rộng. Cỡ M, P1.
- **U006 — Bật extension `hmac-secret` + `largeBlobs`.** Nhiều ví/passkey cần hmac-secret để suy khóa mã hóa.
  Ở ĐÂU: cấu hình pico-fido + test liên thông. Cỡ M, P1.
- **U007 — Cứng hóa nút BOOT làm cử chỉ chạm (debounce + chống kẹt).** Nút kẹt = bỏ qua user presence.
  Ở ĐÂU: `firmware/hwtest/hwtest.ino` (mẫu) rồi port sang pico-fido. Cỡ S, P1.
- **U008 — Đóng băng HID report descriptor + test hồi quy.** Descriptor đổi lén là gãy tool PC; khóa 36 byte
  đã kiểm (NCKH-009) thành test. Ở ĐÂU: test mới trong `scripts/run_tests.*`. Cỡ S, P1.
- **U009 — Provisioning attestation riêng (AAGUID + cert batch).** Dùng cert mẫu của pico-fido thì key của bạn
  không phân biệt được với key người khác. Ở ĐÂU: quy trình offline + két chứa khóa ký. Cỡ L, P0.
- **U010 — Cập nhật firmware có chữ ký + chống rollback.** Key không update được thì lỗ hổng là vĩnh viễn;
  update không ký thì thành cửa hậu. Ở ĐÂU: secure OTA + eFuse anti-rollback. Cỡ L, P1.
- **U011 — Factory reset an toàn.** Xóa credential nhưng giữ attestation; cấm reset lén qua lệnh lạ.
  Ở ĐÂU: pico-fido config + checklist kiểm. Cỡ M, P1.
- **U012 — Mã LED/trạng thái chuẩn cho mọi trạng thái CTAP.** Người dùng phải phân biệt được chờ chạm /
  lỗi / khóa bằng mắt thường. Ở ĐÂU: `docs/05-huong-dan-su-dung.md` + firmware. Cỡ S, P2.
- **U013 — Sửa race echo + nuốt lỗi gửi trong hwtest (thẻ FIX-177).** Lỗi đã biết từ NCKH-003, là mẫu xấu nếu
  ai copy code hwtest sang chỗ khác. Ở ĐÂU: `firmware/hwtest/hwtest.ino`. Cỡ S, P1.
- **U014 — hwtest tự báo bo mạch sai (fail nhanh nếu không phải S3).** Tránh nạp nhầm board họ ESP32 khác.
  Ở ĐÂU: `firmware/hwtest/hwtest.ino` (`#ifdef CONFIG_IDF_TARGET_ESP32S3`). Cỡ S, P2.
- **U015 — Khóa cổng nạp sau provisioning (eFuse download-mode).** Chốt đúng yêu cầu gốc của bạn: nạp xong thì
  đóng cửa nạp, chỉ mở bằng quy trình. CẤM thử trên board chính trước khi duyệt. Ở ĐÂU: runbook + board thử rẻ. Cỡ M, P0.

## Nhóm B — Phần cứng (U016–U023)

- **U016 — Mua board thứ 2 đúng mã N16R8 (quy tắc hai key, `docs/06`).** Một key là một điểm chết duy nhất.
  Ở ĐÂU: `hardware/BOM.md` + nhà bán. Cỡ S (mua) , P0.
- **U017 — Chạy checklist bring-up NCKH-051 tick thật từng ô trên board.** Checklist 47 ô hiện mới đúng trên
  giấy. Ở ĐÂU: `docs/checklist-bring-up-board.md`. Cỡ M, P0.
- **U018 — Vỏ + móc khóa chống mở lén (tamper-evident).** Kẻ trộm mở vỏ nạp firmware lạ mà bạn không biết thì
  mọi mã hóa vô nghĩa. Ở ĐÂU: mua vỏ + keo niêm phong. Cỡ S, P1.
- **U019 — Đo dòng tiêu thụ + bảo vệ ESD đường USB.** Board chết vì tĩnh điện khi rút/cắm là mất key.
  Ở ĐÂU: đo bằng USB tester, ghi vào `hardware/`. Cỡ S, P2.
- **U020 — Ma trận tương thích C-to-C: Android × Linux × Win11.** Mục tiêu dùng thật bạn đặt ra, phải có bảng
  tick xanh từng combo cáp/máy. Ở ĐÂU: `docs/` + `fido_check`. Cỡ M, P0.
- **U021 — Hộp dự phòng: cáp C-to-C, đầu chuyển, nút thay.** Mất cáp lúc cần khôi phục thì bằng mất key.
  Ở ĐÂU: mua sắm + checklist. Cỡ S, P2.
- **U022 — Sổ theo dõi key (SN/MAC/vị trí/phiên bản firmware).** MAC chỉ để định danh như bạn đã chốt, ghi
  riêng khỏi bí mật. Ở ĐÂU: file mới `hardware/so-theo-doi-key.md`. Cỡ S, P1.
- **U023 — Kiểm tra key qua hub USB-C và OTG điện thoại.** Nhiều key lỗi chỉ lòi ra sau hub/OTG thiếu nguồn.
  Ở ĐÂU: bổ sung checklist U017. Cỡ S, P1.

## Nhóm C — Tool PC (U024–U041)

- **U024 — Sửa CBOR TypeError key unhashable (26 case fuzz NCKH-010).** Key lạ làm tool nổ thay vì báo lỗi sạch.
  Ở ĐÂU: `tools/fido_check.py:cbor_decode`. Cỡ S, P1.
- **U025 — Chặn CBOR lồng sâu gây RecursionError (4 case).** Giới hạn depth theo chuẩn. Ở ĐÂU: cùng hàm trên. Cỡ S, P1.
- **U026 — Từ chối rác đuôi CBOR và bytes/text cụt (F6).** Im lặng bỏ qua là sai ngữ nghĩa CTAP2.
  Ở ĐÂU: cùng hàm trên. Cỡ S, P1.
- **U027 — Kiểm CID + thứ tự seq gói nối (F1/F2/F3).** Hiện không caller nào kiểm CID trả về; seq không wrap
  mod 128; message dài mất nhận lại. Ở ĐÂU: `tools/fido_check.py` tầng nối gói. Cỡ M, P1.
- **U028 — Sửa nhãn CTAP2 sai ngữ nghĩa (F5) + thay `assert` bằng ValueError (F8).** Nhãn sai làm debug lạc hướng;
  assert mất tác dụng dưới `python -O`. Ở ĐÂU: `tools/fido_check.py`. Cỡ S, P1.
- **U029 — `pqc.py`: OSError sạch + `chmod 0o600` cho `.sk` + chặn prefix `../` + đưa CLI vào self-test.**
  Gộp 4 phát hiện NCKH-001/006 (thẻ FIX-169). Ở ĐÂU: `tools/pqc.py`. Cỡ M, P1.
- **U030 — `hid_echo`: lọc đúng thiết bị (VID/PID/usage) + kiểm report ID trả về.** Hiện bắt nhầm thiết bị 0xFF00
  lạ trên máy thật (NCKH-016). Ở ĐÂU: `tools/hid_echo.py`. Cỡ S, P0.
- **U031 — `mnemonic`: sửa đếm `nhận 1` với input rỗng + cảnh báo khi `seed` gặp cụm hỏng (P1/P2 NCKH-034).**
  Ở ĐÂU: `tools/mnemonic.py:56` + `cmd_seed`. Cỡ S, P1.
- **U032 — `split_secret`: sửa P1–P4 (KeyError traceback, index=-1 ra bí mật SAI LẶNG, index=300, thông điệp Anh).**
  P2 là nguy hiểm nhất toàn repo tool. Ở ĐÂU: `tools/split_secret.py`. Cỡ M, P0.
- **U033 — `vault`: tách thông điệp két cụt/rỗng/file sửa + tài liệu hóa chi phí đoán sai (PBKDF2 600k).**
  Người dùng nhập sai pass mà báo chung chung sẽ hoảng. Ở ĐÂU: `tools/vault.py`. Cỡ S, P1.
- **U034 — Lệnh `qr` hai tool: tự tạo thư mục cha + bọc try ImportError/OSError (NCKH-046/051).**
  Ở ĐÂU: `tools/split_secret.py:288-304`, `tools/mnemonic.py:206-221`. Cỡ S, P1.
- **U035 — Áp bảng mã thoát chuẩn NCKH-052 (0 ok / 1 lỗi chạy / 2 sai dùng) vào cả 7 tool.** Script tự động
  không đoán exit code bằng mắt được. Ở ĐÂU: 7 file `tools/*.py`. Cỡ M, P1.
- **U036 — Tool quản lý key hợp nhất (`keymgr`: provision / list / reset / attest).** Hiện thao tác rời rạc,
  dễ làm sai thứ tự trên key thật. Ở ĐÂU: file mới `tools/keymgr.py`. Cỡ L, P1.
- **U037 — Chạy `fido_check` + `hid_echo` end-to-end với key thật.** Mọi đường HID thật hiện chưa ai chạy (U1
  lớn nhất, NCKH-048). Ở ĐÂU: cần board + mở rộng self-test. Cỡ M, P0.
- **U038 — Gợi ý từ gần đúng (`did you mean?`) cho mnemonic.** Gõ sai 1 chữ cái mà tool chỉ nói "từ lạ" thì
  người dùng mò rất lâu. Ở ĐÂU: `tools/mnemonic.py`. Cỡ M, P2.
- **U039 — Test lệnh `qr` + đường nhập tay `getpass` của `split_secret` (U2 NCKH-022).** Hai đường chưa ai chạm.
  Ở ĐÂU: mở rộng self-test. Cỡ S, P2.
- **U040 — `pqc` self-test assert kích thước FIPS + tính ngẫu nhiên encap.** Bắt lén đổi lib/version sai.
  Ở ĐÂU: `tools/pqc.py` self-test. Cỡ S, P2.
- **U041 — Sửa nhãn-0 theo đúng Gohr trong `ml_distinguisher` (lỗ hổng phương pháp NCKH-020).** Nhãn 0 hiện tại
  là ngẫu nhiên thuần — bài toán dễ hơn Gohr, số liệu khó so sánh. Ở ĐÂU: `tools/ml_distinguisher.py:make_dataset`. Cỡ M, P1.

## Nhóm D — Bảo mật & hậu lượng tử (U042–U053)

- **U042 — Code `pqc_wrap.py` theo đặc tả PQC-WRAP-V1 (NCKH-025 + QD-002).** Đặc tả xong mà chưa có code thì
  bọc S bằng ML-KEM vẫn là lời hứa. Ở ĐÂU: file mới `tools/pqc_wrap.py`. Cỡ L, P0.
- **U043 — Lịch rotation khóa bọc 2 năm + nhắc tự động.** Quên rotation thì "2 năm" trong QD-002 vô nghĩa.
  Ở ĐÂU: lịch + checklist vận hành. Cỡ S, P2.
- **U044 — Chuyển trường `kind` của share sang SỐ (QD-002).** Parser hiện tại từ chối `kind` chữ.
  Ở ĐÂU: `tools/split_secret.py` + đặc tả. Cỡ S, P1.
- **U045 — Theo dõi chữ ký PQC lai cho firmware (chờ Espressif).** Ký Secure Boot hôm nay vẫn ECDSA/RSA, Shor
  phá được — phải có vé theo dõi, không được quên. Ở ĐÂU: vé định kỳ + `docs/de-doa-luong-tu.md`. Cỡ S, P2.
- **U046 — Theo dõi chuẩn PQC cho FIDO (ML-DSA/SLH-DSA).** Ngày chuẩn chốt là ngày phải nâng cấp key + đăng ký
  lại. Ở ĐÂU: vé định kỳ 6 tháng. Cỡ S, P2.
- **U047 — Gắn quét secret vào CI (gitleaks) theo đề xuất NCKH-036.** Kết luận repo SẠCH hôm nay không bảo vệ
  commit ngày mai. Ở ĐÂU: CI + `.gitleaks.toml`. Cỡ S, P1.
- **U048 — Áp 3 dòng ignore NCKH-042 đã kiểm vào `.gitignore`.** Đã mô phỏng kỹ, chưa ai áp.
  Ở ĐÂU: `.gitignore`. Cỡ S, P1.
- **U049 — Cập nhật threat model sau bring-up thật.** Mô hình đe dọa trên giấy khác với board đã khóa eFuse.
  Ở ĐÂU: `docs/06-bao-mat.md`. Cỡ M, P1.
- **U050 — Chốt chính sách PIN (độ dài, lần thử, khóa) thành văn.** Trùng ý U004 phía firmware — đây là phía
  tài liệu/vận hành cho người dùng. Ở ĐÂU: `docs/05-huong-dan-su-dung.md`. Cỡ S, P1.
- **U051 — Cất `ket.bin` offsite (để đâu cũng được vì đã mã hóa) + ghi vị trí.** Két mã hóa mà chỉ nằm 1 máy
  thì cháy máy là mất. Ở ĐÂU: vận hành + sổ vị trí. Cỡ S, P1.
- **U052 — Đánh giá lại PBKDF2 600k vòng mỗi 2 năm.** Phần cứng mạnh lên thì vòng lặp phải tăng theo.
  Ở ĐÂU: vé định kỳ. Cỡ S, P2.
- **U053 — Tách khóa ký release + quy trình ký (máy lạnh/offline).** Khóa ký nằm cùng máy dev thì kẻ chiếm máy
  ký được firmware giả. Ở ĐÂU: quy trình + két riêng. Cỡ M, P0.

## Nhóm E — Sao lưu & khôi phục (U054–U063)

- **U054 — Diễn tập 3 đường khôi phục mỗi 6 tháng (USB + ổ cứng + 24 từ).** Quy trình chưa từng diễn tập thì
  ngày mất key mới biết nó hỏng. Ở ĐÂU: lịch + biên bản diễn tập. Cỡ M, P0.
- **U055 — Đăng ký cả 2 key vào mọi dịch vụ ngay khi có key 2.** Key dự phòng chưa đăng ký thì lúc cần vẫn phải
  dùng đường khôi phục chậm. Ở ĐÂU: checklist dịch vụ. Cỡ M, P0.
- **U056 — In 24 từ BIP-39 + niêm phong 2 nơi tách biệt.** Giấy vẫn là bản sao bền nhất khi mọi thiết bị cùng
  hỏng. Ở ĐÂU: vận hành (máy in offline, đốt bản nháp). Cỡ S, P0.
- **U057 — Test khôi phục bằng QR share end-to-end.** Đường QR hiện mới test vẽ ảnh, chưa test quét → ghép →
  mở két. Ở ĐÂU: `tools/` + 1 điện thoại. Cỡ M, P1.
- **U058 — Đánh giá đe dọa đường Bluetooth khi chuyển share.** Bluetooth tiện nhưng nghe lén được; chốt khi nào
  được dùng, khi nào bắt buộc cáp/QR. Ở ĐÂU: `docs/07-sao-luu-va-khoi-phuc.md`. Cỡ M, P1.
- **U059 — Người thừa kế số (recovery contact).** Bạn bất tỉnh mà không ai mở được két thì tài sản kẹt vĩnh viễn.
  Ở ĐÂU: phong bì niêm phong + di chúc. Cỡ S, P1.
- **U060 — Sổ vị trí share (ghi Ở ĐÂU, không ghi share).** Quên share nằm đâu thì ngưỡng K-trên-N thành đố vui.
  Ở ĐÂU: file mới `hardware/vi-tri-share.md` (không bí mật). Cỡ S, P1.
- **U061 — Diễn tập mất 1 share (giả lập hỏng 1 thiết bị).** Chứng minh K-trên-N chịu được mất mát thật.
  Ở ĐÂU: cùng buổi với U054. Cỡ S, P1.
- **U062 — Đo hiệu năng Shamir N=255 secret 1KB (U1 NCKH-022, ước ~14s).** Số ước cần số đo trước khi ai dùng
  ngưỡng lớn. Ở ĐÂU: chạy 1 lần, ghi vào tài liệu. Cỡ S, P2.
- **U063 — Tờ khôi phục 1 trang in giấy để cạnh key.** Lúc hoảng không ai đọc nổi tài liệu 7 chương.
  Ở ĐÂU: file mới `docs/to-khoi-phuc-1-trang.md`. Cỡ S, P0.

## Nhóm F — ML & QGAC (U064–U071)

- **U064 — Implement + validate Simon32/64 (thẻ 1 đề xuất NCKH-056).** Bước đầu so sánh distinguisher qua họ mã.
  Ở ĐÂU: mở rộng `tools/ml_distinguisher.py` + cổng 0. Cỡ L, P1.
- **U065 — Sweep Simon R=5..9 + x10 điểm mù (thẻ 2).** Tìm điểm rơi accuracy, so Speck-vs-Simon công bằng.
  Ở ĐÂU: cùng tool + báo cáo số. Cỡ M, P1.
- **U066 — Thử chênh lệch mới (0x2800,0x0010) ở Speck R=8 (thẻ 3, ~25 giây CPU).** Câu hỏi rẻ nhất nhóm ML.
  Ở ĐÂU: 1 lần chạy + ghi kết quả. Cỡ S, P1.
- **U067 — Đọc tài liệu SKINNY + chốt chênh lệch (thẻ 4, CHƯA code).** Cấm bịa chênh lệch như NCKH-056 đã nêu.
  Ở ĐÂU: tài liệu kiểu NCKH-020 cho SKINNY-64. Cỡ M, P2.
- **U068 — Refactor nhãn-0 Gohr thành chế độ mặc định (sau U041).** Giữ chế độ cũ làm flag so sánh 1 thời gian
  rồi bỏ. Ở ĐÂU: `tools/ml_distinguisher.py`. Cỡ M, P2.
- **U069 — Thử ResNet khi có GPU/cloud (máy 5090).** MLP CPU đã cạn ở R≥7; muốn đào sâu phải đổi mạng.
  Ở ĐÂU: máy cloud + ticket riêng. Cỡ L, P2.
- **U070 — Gắn cảnh báo giới hạn vào mọi số liệu ML (âm tính ≠ mã an toàn).** Trích sai 1 câu là thành quảng cáo
  láo. Ở ĐÂU: `docs/research/06-ml-distinguisher.md` + mọi báo cáo. Cỡ S, P1.
- **U071 — Nhật ký số liệu thí nghiệm (1 bảng append-only).** Số rải rác 6 sổ rất khó so sánh về sau.
  Ở ĐÂU: file mới `docs/research/so-lieu-ml.md`. Cỡ S, P2.

## Nhóm G — Tài liệu (U072–U079)

- **U072 — Sửa ghi chú vector Gohr "chưa xác nhận" trong `docs/06` (nợ đã biết).** NCKH-032 đã xác nhận khớp
  deep_speck mà tài liệu vẫn ghi chưa — sai sự thật. Ở ĐÂU: `docs/06-bao-mat.md` + comment tool. Cỡ S, P0.
- **U073 — Mở rộng FAQ từ unresolved mới (đợt 2B/2C).** FAQ hiện tại chỉ gom tới NCKH-028.
  Ở ĐÂU: `docs/FAQ.md`. Cỡ M, P2.
- **U074 — Đóng dấu "đã chạy thật" lên runbook sau U017.** Runbook chưa tick thật phải ghi rõ là lý thuyết.
  Ở ĐÂU: 2 file runbook + checklist. Cỡ S, P1.
- **U075 — Cập nhật sơ đồ kiến trúc theo đường pico-fido.** Sơ đồ hiện tại vẽ hwtest là trung tâm, sai trọng tâm
  dùng thật. Ở ĐÂU: `docs/02-kien-truc.md` (NCKH-011). Cỡ M, P1.
- **U076 — Bảng thuật ngữ Việt-Anh (nhiệm vụ NCKH-059 đợt 3).** Dịch lung tung ("share" nửa Anh nửa Việt) làm
  tài liệu khó đọc. Ở ĐÂU: file mới `docs/bang-thuat-ngu.md`. Cỡ M, P2.
- **U077 — Tóm tắt dự án 1 trang (nhiệm vụ NCKH-053 — đã xong, cần soát + in).** Tờ này để trong hộp key.
  Ở ĐÂU: soát deliverable NCKH-053. Cỡ S, P1.
- **U078 — Hook kiểm chính tả + link trước commit.** Rẻ hơn thuê agent rà 51 mục như NCKH-023 mỗi lần.
  Ở ĐÂU: pre-commit + CI. Cỡ M, P2.
- **U079 — Quy trình changelog/release notes.** Mỗi lần sửa firmware/tool phải có dòng ghi thay đổi, không thì
  không ai biết key mình đang chạy bản nào. Ở ĐÂU: file mới `CHANGELOG.md`. Cỡ S, P1.

## Nhóm H — Kiểm định & CI (U080–U089)

- **U080 — Commit baseline git đầu tiên (thẻ OPS-171, CHỜ BẠN DUYỆT).** Không có baseline thì không diff, không
  revert, không CI ý nghĩa. Ở ĐÂU: `git add` + commit. Cỡ S, P0.
- **U081 — CI chạy `run_tests` mỗi push.** Test chỉ chạy khi nhớ thì bằng không test.
  Ở ĐÂU: GitHub Actions hoặc runner cục bộ. Cỡ M, P0.
- **U082 — CI build hwtest 2 chế độ (thẻ DOC-170: script build OTG+HWCDC).** Gộp luôn việc của thẻ 170 vào CI.
  Ở ĐÂU: `scripts/build_hwtest.*` + CI. Cỡ M, P1.
- **U083 — Fuzz định kỳ cbor/parse_share với corpus lưu lại.** Fuzz 1 lần rồi bỏ thì lỗi mới chui lại.
  Ở ĐÂU: CI đêm + `tests/corpus/`. Cỡ M, P1.
- **U084 — Test hồi quy cho mọi P1–P4 sau khi sửa (U024–U034).** Sửa không kèm test thì lần sau tái phạm.
  Ở ĐÂU: cùng PR với mỗi bản sửa. Cỡ M, P0.
- **U085 — Báo cáo bao phủ tự động từ NCKH-048.** Báo cáo bao phủ viết tay sẽ cũ sau 1 tuần.
  Ở ĐÂU: CI sinh bảng bao phủ. Cỡ M, P2.
- **U086 — Runner Ubuntu chạy `run_tests.sh` (hiện WSL hỏng, `.sh` chưa từng chạy).** Nửa repo script chưa ai
  thực thi. Ở ĐÂU: máy Ubuntu hoặc sửa WSL. Cỡ M, P1.
- **U087 — Test cài lib trên venv sạch (mở rộng NCKH-054).** Bắt lỗi "máy tôi chạy được" do lib toàn cục.
  Ở ĐÂU: CI job riêng. Cỡ S, P1.
- **U088 — Ghim phiên bản liboqs + vé bump định kỳ.** Lib nhảy version lén là self-test PQC đổi ý nghĩa.
  Ở ĐÂU: requirements + vé 6 tháng. Cỡ S, P2.
- **U089 — SBOM có ký mỗi release.** Biết chính xác key/tool chứa lib nào khi có CVE.
  Ở ĐÂU: `pip freeze` + chữ ký. Cỡ S, P2.

## Nhóm I — Vận hành Viện & Kanzo (U090–U100)

- **U090 — Mở đợt 3 (72 agent NCKH-057…128).** Đợt 2 xong, cổng ĐẠT, không lý do gì để 144 agent ngồi chơi.
  Ở ĐÂU: Viện trưởng giao sóng 16 agent/lượt. Cỡ L, P0.
- **U091 — Dọn 5 thẻ trùng (172/173, 174/175, 187/191 — CHỜ BẠN DUYỆT XÓA).** Bảng bẩn gây nhầm thẻ.
  Ở ĐÂU: Kanzo DELETE. Cỡ S, P1.
- **U092 — Khởi động lại service Kanzo khi SQLite nghẽn + backup DB định kỳ.** Bao nhiêu công vá bảng cũng không
  bằng 1 lần restart đúng lúc. Ở ĐÂU: máy chạy Kanzo + cron backup. Cỡ S, P0.
- **U093 — Dashboard tự làm mới sau mỗi đợt (cron gọi generator).** Dashboard cũ là dashboard nói dối.
  Ở ĐÂU: cron + `tools/vien_dashboard.py`. Cỡ S, P1.
- **U094 — Tìm full-text xuyên sổ cái trên dashboard.** Hiện chỉ tìm được mã/tên/việc, chưa tìm được nội dung
  báo cáo. Ở ĐÂU: `dashboard/template.html`. Cỡ M, P2.
- **U095 — Viết quy trình biểu quyết hội đồng thành văn.** "Bàn tròn, biểu quyết" hiện mới là khẩu hiệu.
  Ở ĐÂU: `vien-nghien-cuu/HIEN-CHUONG.md`. Cỡ M, P2.
- **U096 — Lưu trữ sổ đợt cũ (archive theo đợt).** 200 sổ trong 1 thư mục sẽ thành bãi rác.
  Ở ĐÂU: `vien-nghien-cuu/so-cai/archive/`. Cỡ S, P2.
- **U097 — Tờ onboarding agent mới 1 trang.** Mỗi agent đọc 4 file hiến chương/phân công mới hiểu việc — lãng phí.
  Ở ĐÂU: `vien-nghien-cuu/KHOI-DONG.md` rút gọn. Cỡ S, P2.
- **U098 — Thư viện gọi Kanzo chung (retry + giãn cách + nhật ký).** Mỗi agent tự viết retry là mỗi kiểu lỗi mới.
  Ở ĐÂU: `tools/kanzo.py` dùng chung. Cỡ M, P1.
- **U099 — Chuẩn hóa mẫu báo cáo kiểm chéo (verdict 1 dòng đầu mục).** Parser dashboard đã phải đoán verdict bằng
  3-4 mẫu câu khác nhau. Ở ĐÂU: `vien-nghien-cuu/so-cai/README.md`. Cỡ S, P1.
- **U100 — Tổng kết đợt thành release notes Viện.** Mỗi đợt xong phải có 1 trang: làm gì, quyết gì, nợ gì.
  Ở ĐÂU: `vien-nghien-cuu/tong-ket-dot-*.md`. Cỡ S, P1.

---

*Hết 100 mục. Thứ tự đọc gợi ý khi chỉ có 1 ngày: U080 → U016 → U020 → U001 → U030 → U032 → U042 → U054 → U056 → U072.*

