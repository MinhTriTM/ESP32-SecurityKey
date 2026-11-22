# Sổ cái NCKH-004 — Phạm An (nhóm tooling, nhóm trưởng, đợt 1)

## 2026-11-21 01:29 — nhận việc
- Thẻ: [tooling] Rà soát fido_check đường lỗi (Kanzo id 141)
- Người nhận: Phạm An (NCKH-004)
- Việc nhận: rà soát tools/fido_check.py đường lỗi (timeout, CID sai, gói nối sai thứ tự,
  rút thiết bị giữa chừng, từng mã lỗi GetInfo; self-test có bao hết không). REPO CHỈ ĐỌC.
- Đã đọc: vien-nghien-cuu/HIEN-CHUONG.md, mục NCKH-004 trong vien-nghien-cuu/phan-cong.json,
  vien-nghien-cuu/so-cai/README.md, toàn bộ tools/fido_check.py (463 dòng).
- Ghi chú tên: objective ban đầu ghi "Phạm Dung", Viện trưởng đã đính chính tên chính thức
  theo phan-cong.json là Phạm An (mã NCKH-004 giữ nguyên). Từ đây dùng Phạm An.
- Trạng thái dự kiến: todo -> doing -> review (Kanzo đang nghẽn, đồng bộ opportunistic sau).

## 2026-11-21 01:32 — báo cáo rà soát tools/fido_check.py
- Đã làm: đọc toàn bộ 463 dòng; chạy self-test; chạy 3 probe chỉ-đọc bằng `python -B`
  (không ghi repo, không sinh __pycache__; script chạy trực tiếp nên không tạo .pyc).
- Phạm vi: mọi nhánh raise/except trong recv_msg, ctap2_get_info, cbor_decode,
  parse_init_response, send_msg/fragment/build_*, main; đối chiếu với self_test/FakeDevice.

### Kết quả từng đường lỗi trong nhiệm vụ

1. Timeout — ĐẠT (thiếu bao phủ self-test một phần).
   - Gói đầu: TimeoutError "thiết bị không trả lời" (recv_msg:122-124); main bắt sạch, exit 1.
   - Gói nối: TimeoutError "gói nối không tới" (recv_msg:136-138); main bắt sạch.
   - Timeout là per-packet 2000ms, chưa có timeout tổng cho message dài (chấp nhận được).
   - Đã kiểm chứng TimeoutError là subclass của OSError nhưng thứ tự except trong main
     đúng (TimeoutError trước OSError) nên không lọt nhầm nhánh.
   - Gap S1: self-test chỉ bao timeout gói đầu (dòng 367-372), KHÔNG bao timeout gói nối.

2. CID sai — ĐẠT một nửa, có gap chức năng.
   - Gói nối sai CID -> ValueError "gói nối sai CID" (140-141). Probe BADCID: đúng.
   - F1 (trung bình): CID gói ĐẦU không được kiểm ở bất cứ caller nào. main không đối
     chiếu CID trả về của INIT (đáng lẽ broadcast) và PING echo (đáng lẽ == cid đã cấp);
     ctap2_get_info bỏ CID (`_`, dòng 213). Crosstalk từ kênh khác/key khác không bị phát hiện.
   - Gap S2: self-test KHÔNG bao CID sai (cả gói đầu lẫn gói nối).

3. Gói nối sai thứ tự — ĐẠT cơ bản, có 2 gap chức năng.
   - Seq lệch -> ValueError chi tiết "muốn {seq}, thấy {...}" (142-143). Probe BADSEQ: đúng.
   - F2 (trung bình): gói INIT (bit 0x80), đặc biệt CTAPHID_ERROR, đến giữa lúc đang chờ
     gói nối bị báo nhầm thành ValueError "sai thứ tự" thay vì CtapHidError thật. Probe:
     MASK: ValueError: gói nối sai thứ tự (muốn 0, thấy 191). Key báo CHANNEL_BUSY (0x06)
     giữa chừng sẽ bị hiểu sai thành lỗi thứ tự.
   - F3 (thấp, bẫy tái sử dụng): seq không wrap modulo 128 và không kiểm tra bit 7 == 0
     của gói nối; message > 7609 byte (129 gói nối) wrap đúng chuẩn vẫn hỏng. Probe:
     WRAP: gói nối sai thứ tự (muốn 128, thấy 0). fragment() cho gửi tới 64KB nhưng
     recv_msg không bao giờ nhận lại được message lớn. GetInfo/PING hiện tại nhỏ nên chưa chạm.
   - Gap S3: self-test KHÔNG bao thứ tự sai; chỉ có happy-path 2 gói (100 byte).

4. Rút thiết bị giữa chừng — ĐẠT (chưa kiểm chứng phần cứng).
   - Khi gửi: OSError từ dev.write -> main nhánh OSError -> "Lỗi HID", exit 1. Đạt.
   - Khi nhận: hidapi raise OSError (bắt sạch) hoặc trả rỗng -> TimeoutError (bắt sạch
     nhưng thông điệp "hết giờ" dễ gây hiểu nhầm là key chậm chứ không phải đã rút). Nhẹ.
   - finally: device.close() luôn chạy. Đạt.
   - F4 (nhẹ): device.set_nonblocking(False) (dòng 411) nằm NGOÀI try; nếu nó raise
     OSError thì traceback và không close. Nên đưa vào trong try.
   - Gap S4: self-test KHÔNG mô phỏng rút thiết bị (FakeDevice.read chỉ trả rỗng,
     không raise OSError; write luôn thành công).

5. Từng mã lỗi GetInfo (CTAP2) — đường raise ĐẠT, nhãn/gap bao phủ cần sửa.
   - Mọi status != 0 -> Ctap2Error giữ đúng code (218-219). Probe GI27: code = 0x27. Đạt.
   - Rỗng -> "CBOR trả về rỗng", non-map -> "GetInfo không trả về map", sai lệnh CBOR
     (214-215) đều ValueError sạch. Probe GEMPTY/GNONMAP: đúng.
   - F5 (nhẹ, nhãn sai): bảng CTAP2_STATUS gán sai ngữ nghĩa chuẩn CTAP2: 0x0A trong CTAP2
     là CBOR_UNEXPECTED_TYPE nhưng ghi "cần mở khóa"; 0x27 là PIN_NOT_SET nhưng ghi
     "lệnh chưa hỗ trợ"; thiếu nhiều mã chuẩn (0x07, 0x08, 0x0B, 0x10-0x16, 0x1A-0x22...).
     Mã lạ vẫn raise đúng code, chỉ fallback "không rõ". Bảng hiện tại copy nhầm ngữ
     nghĩa CTAPHID sang CTAP2. GetInfo hiếm lỗi nên ảnh hưởng chủ yếu khi debug.
   - F6 (nhẹ): rác sau CBOR map bị bỏ qua im lặng (probe GITRAIL parse OK dù +b"XYZ":
     `info, _ = ...` dòng 220); CBOR bytes/text khai dài hơn thực tế bị cắt cụt im lặng
     (probe CBOR-cut: text(3) chỉ 2 byte -> trả 2 byte, không báo; dòng 185/187 không
     kiểm tra len(rest) >= arg). GetInfo hỏng nhẹ vẫn báo "ok".
   - Không phải lỗi (đã kiểm chứng): CBOR text UTF-8 sai -> UnicodeDecodeError, là
     subclass của ValueError nên main bắt sạch.
   - F7 (rất thấp): CBOR lồng sâu (key độc hại) -> RecursionError (subclass RuntimeError,
     không phải ValueError) -> traceback thay vì lỗi sạch.
   - Gap S5 (gap bao phủ lớn nhất): self-test KHÔNG bao bất kỳ nhánh lỗi GetInfo nào:
     không Ctap2Error, không rỗng, không non-map. FakeDevice luôn trả GetInfo thành công.

6. Lỗi CTAPHID gói đầu (ngoài nhiệm vụ nhưng liền kề).
   - Gói đầu ERROR -> CtapHidError đúng code (132-133), kể cả data rỗng -> 0x00.
     Bảng HID_ERRORS khớp spec (01,02,03,04,05,06,0A,0B). Đạt.
   - Gap S6 (nhẹ): self-test chỉ bao 1 trường hợp lệnh lạ -> 0x01 (360-366); đường raise
     chung một dòng nên rủi ro thấp.

7. F8 (nhẹ): build_init_packet/build_ping_packet/fragment dùng assert (81,88,95);
   AssertionError KHÔNG nằm trong except của main -> traceback; `python -O` tắt hết
   kiểm tra. Self-test còn khóa chặt hành vi này (304-309 expect AssertionError).
   Probe PING58: AssertionError. Nên đổi sang ValueError.

8. Nhỏ khác (ghi nhận, không cần sửa gấp): --index âm (vd -1) được chấp nhận im lặng
   do indexing Python; parse_init_response bỏ qua byte 13-15 và không từ chối
   new_cid == 0/broadcast; FakeDevice không kiểm tra CID/seq gói host gửi lên nên lỗi
   phía fragment/send_msg của chính tool không bị self-test phát hiện.

### Kết luận self-test
- Self-test xanh và bao hết happy path (framing, 2-gói, CBOR mẫu, hội thoại đầu-cuối ở
  cả 2 chế độ report ID, 1 lỗi HID 0x01, 1 timeout gói đầu).
- Self-test KHÔNG bao: timeout gói nối (S1), CID sai (S2), thứ tự sai (S3), rút thiết
  bị/OSError (S4), mọi lỗi GetInfo/CTAP2 (S5), INIT ngắn, gói HID dài lạ, các mã HID
  còn lại (S6). Bản chất hiện tại là kiểm tra regression happy-path, chưa phải kiểm
  tra đường lỗi. Đề nghị NCKH-010 (fuzz cbor_decode) và đợt sau bổ sung các case S1-S5.

### Tự kiểm (lệnh đã chạy + output, shell pwsh)
- `python tools/fido_check.py --self-test` ->
  `self-test ok: framing, gói nối, CBOR, GetInfo và hội thoại đầu-cuối đều đúng.` EXIT:0
- Probe 1 -> `CBOR-cut: (b'\x01\x02', b'')` (cụt im lặng, xác nhận F6);
  `CTAP2-27: lỗi CTAP2 0x27: lệnh chưa hỗ trợ` (xác nhận F5);
  `HID-99: lỗi CTAPHID 0x99: không rõ` (fallback tốt);
  `Timeout-la-OSError: True` (thứ tự except đúng);
  `PING58: AssertionError` (xác nhận F8);
  `RID60: gói HID dài lạ: 60 byte`, `INIT10: INIT trả về quá ngắn: 10 byte` (sạch).
- Probe 2 -> `MASK: ValueError: gói nối sai thứ tự (muốn 0, thấy 191)` (xác nhận F2);
  `BADCID: gói nối sai CID`, `BADSEQ: gói nối sai thứ tự (muốn 0, thấy 3)` (đúng);
  `WRAP: gói nối sai thứ tự (muốn 128, thấy 0)` (xác nhận F3).
- Probe 3 -> `UDecode-la-ValueError: True`, `CBOR61FF: ValueError: UnicodeDecodeError`
  (bắt sạch, không phải lỗi); `GI27: ... code = 0x27` (giữ đúng code);
  `GEMPTY: CBOR trả về rỗng`, `GNONMAP: GetInfo không trả về map` (sạch);
  `GITRAIL: {...đúng...}` dù +b"XYZ" (rác đuôi bị bỏ qua, xác nhận F6).
- Repo chỉ đọc được tôn trọng: mọi probe dùng `python -B`, không tạo file mới trong
  repo ngoài sổ cái này; không git commit.
- Lỗi shell gặp: lần đầu gọi muse.powershell thiếu shell='pwsh' -> "program not found";
  Viện trưởng đã nhắc, đã thử lại với shell='pwsh' và thành công (lệnh liệt kê so-cai:
  đã có NCKH-001..003,005..012, thiếu NCKH-004 — chính file này).

### Unresolved
- U1: chưa kiểm chứng trên key vật lý thật (không có phần cứng trong phiên; đường hid
  thật trong main() chưa chạy). Cần đợt có phần cứng chạy `python tools/fido_check.py`.
- U2: đối chiếu "chuẩn CTAP2" cho F5 dựa trên kiến thức spec của agent, chưa đối chiếu
  tài liệu trong repo (repo không chứa bản spec CTAP2). Cần nhóm tài liệu xác nhận.
- U3: hành vi hidapi khi rút thiết bị (raise OSError hay trả rỗng) khác nhau theo nền
  tảng/phiên bản hidapi — chưa kiểm chứng trên máy này vì không có thiết bị.
- U4: Kanzo — đã đồng bộ opportunistic thành công ngay lần thử đầu (không cần thử lại):
  MOVE-doing OK, COMMENT-baocao OK, MOVE-review OK (mỗi lệnh cách nhau 5s, timeout 30s).
- Trạng thái: todo -> doing -> review. Chờ kiểm chéo ([KIEM-DINH] từ nhóm khác).

## 2026-11-21 01:41 — kiểm chéo thẻ NCKH-011 (người kiểm: Phạm An NCKH-004, nhóm tooling)
- Thẻ: [tailieu] Sơ đồ kiến trúc ASCII (Kanzo id 149). Tác giả: Đỗ An (NCKH-011, nhóm tailieu).
  Kiểm chéo khác nhóm, đúng Hiến chương mục 2 (kiểm bằng đường khác, không chạy lại đúng lệnh tác giả).
- Phạm vi lượt này: REPO CHỈ ĐỌC ngoài sổ cái này; không git commit; không sửa file repo nào khác.
- Đã đọc: vien-nghien-cuu/so-cai/NCKH-011.md (toàn bộ), mục Tổng quan luồng + toàn bộ
  docs/02-kien-truc.md (68 dòng), đối chiếu phan-cong.json (tên Đỗ An) và HIEN-CHUONG.md.

### Kết luận
- [KIEM-DINH] đạt — Sơ đồ ASCII 7 bước đúng thứ tự, khớp mô tả kiến trúc trong file và luồng
  thật; căn lề 100%; ASCII thuần; markdown hợp lệ; giữ nội dung cũ; attribution đúng tên.
  Đề nghị: review -> done (Kanzo move chưa ghi được do nghẽn, xem mục Kanzo bên dưới,
  nhờ Viện trưởng vá khi Kanzo sống lại).

### Đối chiếu từng bước sơ đồ với file và luồng thật
- B1 (navigator.credentials.get/.create): khớp WebAuthn API thật; khớp dòng tóm tắt
  "Browser (WebAuthn)" và mục Giải thích bước 1. Mũi tên Browser -> OS đúng chiều.
- B2 (CTAPHID_INIT/MSG/CBOR qua USB HID report): khớp dòng tóm tắt "OS (CTAPHID/USB HID)",
  mục Thành phần và "Vì sao cắm C-to-C là chạy" (USB HID chuẩn, usage page FIDO).
  Ghi chú nhỏ: gộp "CBOR" vào nhãn tầng CTAPHID hơi imprecise (CBOR nằm trong MSG/CTAP2)
  nhưng phần Giải thích bước 2 diễn đạt đúng ("gói request thành message CTAPHID
  (INIT/MSG/CBOR)"), chấp nhận được cho sơ đồ tóm tắt. Mũi tên OS -> ESP32 đúng chiều.
- B3 (Parse CTAPHID, xử lý CTAP2/U2F): khớp "Firmware chính: pico-fido... xử lý U2F và CTAP2"
  và "Ranh giới an toàn" (mọi xử lý crypto/giao thức nằm trong pico-fido + mbedTLS).
- B4 (LED báo chờ, đợi chạm nút BOOT, User Presence): khớp "Nút BOOT làm nút xác nhận chạm",
  "LED RGB báo trạng thái". Cặp mũi tên ESP32 <-> Người dùng (dòng 27-28) biểu diễn đúng
  vòng chờ chạm. Sơ đồ không dấu (ASCII thuần), phần Giải thích có dấu đầy đủ — nhất quán.
- B5 (ký bằng private key trong flash, key không rời chip): khớp dòng 5 "Private key không bao
  giờ rời khỏi chip", mục "Lưu trữ key" (credential trong flash nội, bật flash encryption/
  secure boot bản thật) và "Ranh giới an toàn" (code tự viết không chạm private key).
- B6 (HID report response về OS): đúng chiều ngược ESP32 -> OS, khớp luồng HID hai chiều.
- B7 (assertion/credential về Browser): đúng chiều OS -> Browser, khớp WebAuthn thật
  (trình duyệt nhận assertion/credential trả cho ứng dụng web), khớp Giải thích bước 7.

### Tự kiểm bằng đường khác (shell pwsh, script riêng)
- Căn lề pipe: script Python riêng (khác lệnh pwsh của tác giả) quét code block dòng 13-36:
  21/21 dòng chứa '|' đều có '|' tại đúng vị trí 0-based [8,40,72,104], mỗi dòng dài 105 ký tự.
  Khớp con số tự kiểm của tác giả bằng đường độc lập. 6 dòng mũi tên (-->/ <--, dòng
  18,21,27,28,33,35) đều nằm trong 4 lifeline, đúng chiều từng bước.
- ASCII thuần: quét code block, 0 dòng chứa ký tự non-ASCII (kể cả "Nguoi dung", "Ky", "nut BOOT"
  đều không dấu có chủ ý). Đúng yêu cầu sơ đồ ASCII.
- Markdown: file 68 dòng, đúng 2 fence ``` (1 cặp mở/đóng dòng 13 và 36); mục "Giải thích các bước"
  đủ cả 7 mục; dòng tiêu đề cột dài 110 ký tự (text header, không mang '|') — không phải lỗi căn lề.
- Giữ nội dung cũ: dòng luồng tóm tắt (dòng 9, có mũi tên →) và câu "Private key không bao giờ
  rời khỏi chip" (dòng 5) còn nguyên; sơ đồ là bổ sung, không ghi đè ý cũ.
- Attribution: dòng 11 "Sơ đồ chi tiết từng bước (đóng góp bởi Đỗ An, NCKH-011):" — đúng tên
  chính thức theo phan-cong.json sau đính chính của Viện trưởng.
- Phạm vi 1 file: git KHÔNG xác minh được — repo chưa có commit nào (git log: "No commits yet",
  git status: toàn bộ untracked, git diff rỗng). Bằng chứng phụ bằng mtime: trong cửa sổ làm việc
  của tác giả (01:29-01:33), chỉ docs/02-kien-truc.md đổi (LastWriteTime 01:31:13, khớp giờ báo cáo
  01:31 của tác giả); các file docs khác đổi trước đó (07 lúc 01:13, còn lại từ hôm trước).
  File tools/__pycache__/fido_check.cpython-312.pyc lúc 01:30:51 là artifact chạy Python của agent
  khác (tác giả làm tài liệu, sổ cái không ghi chạy python) — không tính là sửa repo của NCKH-011.

### Kanzo opportunistic (base http://100.101.100.100:4242/api, timeout 30s, tối đa 2 lần thử lại)
- Lần thử đầu lỗi cú pháp client (URI escape sai, chưa chạm server) — không tính vào quota nghẽn.
- Thử thật: COMMENT '[KIEM-DINH] đạt...' lần 1 lỗi 500 (Internal Server Error, đúng kiểu SQLite
  khóa khi ghi dồn dập), lần 2 OK. Nghỉ 5s. MOVE {status: done} cả 3 lần đều lỗi 500, hết quota.
- Kết quả: comment=True, move_done=False. Đã dừng thử theo luật. Lưu ý theo Hiến chương:
  lỗi 500/timeout không đồng nghĩa server chưa ghi — comment lần 1 (500) có thể đã được ghi
  rồi lần 2 (OK) ghi thêm bản trùng; cần Viện trưởng đối chiếu số comment trên thẻ 149 khi
  Kanzo sống lại, và vá trạng thái thẻ lên done (hiện thẻ có thể vẫn kẹt doing hoặc review
  do lệnh move doing->review của tác giả cũng 500 cả 3 lần).
- Trạng thái thẻ mong muốn: review -> done. Trạng thái ghi được xác nhận: chỉ comment OK.

### Unresolved
- U1: git không có baseline commit nên không chứng minh tuyệt đối "chỉ sửa đúng 1 file" —
  chỉ có mtime ủng hộ. Đề nghị Viện trưởng tạo commit baseline đầu tiên để các lượt kiểm sau
  dùng được git diff.
- U2: trạng thái thực của thẻ 149 trên Kanzo (doing/review/done) và số comment thực tế chưa đọc
  được do board API cũng 500 — cần đối chiếu khi Kanzo sống lại.
- U3 (góp ý nhỏ, không chặn đạt): nhãn B2 "CTAPHID_INIT / MSG / CBOR" gộp CBOR vào tầng CTAPHID;
  đợt sau có thể sửa thành "CTAPHID_INIT / CTAPHID_MSG (CBOR)" cho chính xác tầng, nếu nhóm
  tài liệu đồng ý. Không yêu cầu sửa trong lượt này.
