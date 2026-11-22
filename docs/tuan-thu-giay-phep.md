# Ghi chú tuân thủ giấy phép: MIT (repo này) vs AGPL-3.0 (pico-fido)

> Ghi chú thực hành nội bộ, không phải tư vấn pháp lý. Khi nghi ngờ, giữ lại
> nhiều quyền cho người nhận hơn mức tối thiểu và hỏi người có chuyên môn.

## 1. Hai phần độc lập, hai giấy phép khác nhau

| Phần | Giấy phép | Nguồn xác nhận |
|------|-----------|----------------|
| Repo này (docs, sketch hwtest, scripts, tools, hardware) | MIT | [LICENSE](../LICENSE), Copyright (c) 2026 ESP32-SecurityKey contributors |
| Firmware dùng thật pico-fido (clone riêng, build riêng) | AGPL-3.0 bản cộng đồng | [docs/04-firmware.md](04-firmware.md), tag `v8.2`, commit `15b848d821b4995eb1b29a5c2a4c24c25d1a768e` |

Ranh giới phải giữ: repo này **chỉ tham chiếu** pico-fido bằng URL + commit SHA,
**không copy** code pico-fido vào repo. Nếu nhúng code AGPL vào repo MIT rồi phát
hành chung, phần kết hợp chịu AGPL — lúc đó không được gắn mác "tất cả là MIT" nữa.

## 2. Được làm gì

### 2.1 Với repo MIT này
- Dùng, copy, sửa, gộp, xuất bản, phân phối, cấp phép lại (sublicense), bán —
  kể cả dùng trong sản phẩm đóng — với một điều kiện duy nhất: giữ nguyên dòng
  copyright và toàn văn `LICENSE` trong mọi bản copy hoặc phần đáng kể.
- Không bắt buộc công bố source của phần mình sửa hay viết thêm.

### 2.2 Với pico-fido (AGPL-3.0)
- Tự build, tự sửa, tự dùng cá nhân hoặc nội bộ tổ chức **thoải mái**, không phát
  sinh nghĩa vụ công bố source chừng nào chưa đưa binary ra ngoài.
- Nghiên cứu, kiểm thử, đối chiếu SHA commit sau checkout như quy trình ở
  [docs/04-firmware.md](04-firmware.md).
- Phân phối binary (kể cả bản build từ commit gốc chưa sửa) **kèm theo**
  Corresponding Source: hoặc đóng gói source cùng binary, hoặc cho người nhận một
  đường lấy source tương ứng rõ ràng (link repo + đúng commit SHA đã build, kèm
  mọi patch/sửa đổi của mình). Giữ nguyên mọi notice bản quyền và giấy phép.
- Chạy bản đã sửa để cung cấp dịch vụ qua mạng: AGPL khác GPL ở điểm này —
  người dùng tương tác qua mạng có quyền lấy source bản đang chạy (điều 13).
  Với key FIDO cắm máy cá nhân thì điều này hiếm khi kích hoạt, nhưng hễ bản sửa
  phục vụ người khác qua mạng là phải mở đường lấy source.

## 3. Không được làm gì

- **Không** phân phối binary pico-fido (gốc hay đã sửa) mà không cho người nhận
  cách lấy Corresponding Source. Flash key giúp/người khác rồi đưa key đi **là**
  phân phối — phải kèm source hoặc đường lấy source, không được "đưa mỗi key".
- **Không** đóng source phần mình sửa trong pico-fido khi phân phối: mọi sửa đổi
  trên code AGPL khi convey ra ngoài đều phải tiếp tục dưới AGPL.
- **Không** xóa hay sửa notice bản quyền, notice giấy phép của pico-fido trong
  source lẫn binary phân phối.
- **Không** gắn thêm điều khoản hạn chế (cấm sửa, cấm chia sẻ, thu phí bản quyền)
  lên phần AGPL khi phân phối.
- **Không** copy code pico-fido vào repo này rồi phát hành tất cả dưới MIT.
- **Không** tin tag mù: tag có thể bị dời — luôn đối chiếu SHA commit sau checkout
  (`git rev-parse HEAD` phải in đúng SHA đã ghim) trước khi build bản phân phối.

## 4. Checklist theo từng việc

### Build (cá nhân, chưa đưa ai)
- [ ] Clone đúng URL gốc, checkout đúng commit đã ghim, kiểm tra SHA, cập nhật submodule.
- [ ] Dùng nội bộ: không cần công bố gì thêm.

### Dùng (tự flash key của mình)
- [ ] Được phép toàn bộ, không nghĩa vụ giấy phép phát sinh.
- [ ] Nên ghi lại đã build từ commit nào để sau này truy vết.

### Phân phối (đưa binary/key đã flash cho người khác, tặng hay bán đều tính)
- [ ] Chuẩn bị Corresponding Source: đúng commit SHA + toàn bộ patch/sửa đổi của mình.
- [ ] Người nhận có đường lấy source rõ ràng (kèm theo hoặc link + cam kết giữ sẵn).
- [ ] Giữ nguyên notice bản quyền/giấy phép, ghi rõ phần pico-fido là AGPL-3.0.
- [ ] Phần repo MIT đi kèm: giữ nguyên `LICENSE` và dòng copyright.
- [ ] Không gắn thêm hạn chế lên phần AGPL.

## 5. Điểm cần lưu ý (chưa chốt, cần hỏi thêm)

- **Secure Boot + flash encryption vs Installation Information:** AGPLv3/GPLv3 yêu
  cầu khi convey object code trong hoặc cho một User Product thì phải kèm thông
  tin/hướng dẫn cài đặt (Installation Information) để người nhận cài được bản sửa.
  Quy trình khóa thiết bị ở [docs/06-bao-mat.md](06-bao-mat.md) (khóa nạp, bịt UART,
  efuse một chiều) đi ngược hướng này. Nếu có ngày phân phối key đã khóa kèm
  firmware AGPL, phải xin ý kiến pháp lý trước — ghi chú này chưa kết luận được.
- Ghi chú này viết từ nội dung repo (LICENSE + mục giấy phép trong
  docs/04-firmware.md), chưa đối chiếu toàn văn AGPL-3.0 từng điều khoản.

## Nguồn
- [LICENSE](../LICENSE) — MIT, Copyright (c) 2026 ESP32-SecurityKey contributors.
- [docs/04-firmware.md](04-firmware.md) — tag v8.2, commit ghim, ESP-IDF v5.5.1,
  quy trình build/flash, giấy phép pico-fido AGPL-3.0.
- [pico-fido v8.2](https://github.com/polhenarejos/pico-fido/releases/tag/v8.2).
