# Nghiên cứu 07 — Giải thích distinguisher cho người mới

Tài liệu này giải thích từ đầu cho người chưa từng nghe về thám mã:
distinguisher là gì, thí nghiệm ở nghiên cứu 06 làm gì, và vì sao
"mã của ta chống được distinguisher này" không phải bằng chứng an toàn.

Đọc kèm: [nghiên cứu 06](06-ml-distinguisher.md) (thí nghiệm chi tiết),
script `tools/ml_distinguisher.py`.

## 1. Distinguisher là gì?

### 1.1 Ý tưởng trực quan

Hãy tưởng tượng có hai chiếc hộp đen:

- Hộp A luôn trả ra số **hoàn toàn ngẫu nhiên** (như tung đồng xu công bằng).
- Hộp B chạy một **thuật toán mã hóa** nào đó rồi trả kết quả ra.

Bạn được bấm nút lấy mẫu bao nhiêu lần tùy thích, nhưng không được mở hộp.
**Distinguisher** (bộ phân biệt) là bất kỳ thủ tục nào cố trả lời câu hỏi:
"mẫu tôi đang cầm đến từ hộp A hay hộp B?" — tức là phân biệt
**đầu ra của mã** với **dữ liệu ngẫu nhiên thật sự**.

Nếu không ai phân biệt được (tỉ lệ đoán đúng chỉ ~50%, ngang tung đồng xu),
mã đó "trông ngẫu nhiên" trước con mắt của distinguisher ấy.
Nếu có người đoán đúng rõ ràng trên 50% (ví dụ 60%), mã đó **rò rỉ cấu trúc**:
đầu ra của nó không ngẫu nhiên hoàn toàn, và đó là một vết nứt an toàn.

### 1.2 Vì sao khái niệm này quan trọng?

Trong mật mã hiện đại, một mã khối tốt phải có đầu ra **không thể phân biệt
được với ngẫu nhiên** trước mọi kẻ tấn công thực tế. Đây là yêu cầu nền tảng:
nếu đối thủ chỉ cần nhìn bản mã mà đã nhận ra "đây là bản mã, không phải rác
ngẫu nhiên", thì mã đã để lộ thông tin, và từ vết nứt đó người ta có thể đào
sâu thành đòn tấn công khôi phục khóa hoặc đọc bản rõ.

Nói ngắn gọn: **distinguisher là bài kiểm tra tối thiểu** — mã nào trượt bài này
(rớt ngay vòng "trông có ngẫu nhiên không") thì chắc chắn yếu. Nhưng như mục 3
sẽ giải thích, **đỗ bài này không có nghĩa là mã an toàn**.

### 1.3 Distinguisher cổ điển và distinguisher học máy

- **Cổ điển**: nhà thám mã dùng toán học (thám mã vi sai, tuyến tính...) để viết
  công thức phân biệt bằng tay. Hiệu quả nhưng đòi hỏi chuyên môn sâu và mỗi mã
  phải phân tích riêng.
- **Học máy (kiểu Gohr)**: thay vì viết công thức bằng tay, ta **huấn luyện một
  mạng nơ-ron** làm nhiệm vụ phân biệt. Ta cho mạng xem nhiều mẫu "thật" (đầu ra
  của mã) và mẫu "giả" (ngẫu nhiên), mạng tự học đặc trưng phân biệt. Cách này
  rẻ, tự động, và đôi khi tìm ra tín hiệu mà mắt người bỏ sót — đó chính là điều
  thí nghiệm của ta minh họa.

## 2. Thí nghiệm của ta làm gì?

Thí nghiệm ở nghiên cứu 06 là một bài học minh họa, không phải đánh giá an toàn
sản phẩm. Các bước, diễn giải bằng lời thường:

### 2.1 Sân chơi: mã toy Speck32/64 rút gọn

Ta dùng **Speck32/64**, một mã khối nhỏ gọn, dễ cài đặt để học tập —
không phải mã dùng trong sản phẩm thật. Điểm then chốt: ta chỉ chạy
**R = 5, 6, 7 vòng**, trong khi bản chuẩn đầy đủ chạy tới **22 vòng**.
Mã rút gọn vòng yếu hơn hẳn bản đầy đủ, nên nó là "con mồi" phù hợp để cho
người mới thấy distinguisher hoạt động ra sao: ở ít vòng, tín hiệu còn đủ mạnh
để mạng học được.

### 2.2 Cách tạo hai loại mẫu

- **Mẫu "thật" (nhãn 1)**: lấy hai bản rõ lệch nhau một chênh lệch cố định
  `(dx, dy) = (0x0040, 0x0000)` (theo phong cách Gohr), mã hóa cả hai bằng cùng
  một khóa ngẫu nhiên qua R vòng, rồi nối hai khối bản mã thành một vector
  64 bit. Chênh lệch đầu vào cố định này là "mồi": nếu mã yếu, dấu vết của nó
  còn in hằn trong cặp bản mã.
- **Mẫu "giả" (nhãn 0)**: 64 bit hoàn toàn ngẫu nhiên, không qua mã hóa gì cả.

Tập dữ liệu cân bằng 50/50, nên đoán mò được ~50% — mọi con số trên mức đó
đều là tín hiệu thật mà mạng học được.

### 2.3 Mô hình và ngân sách (cố tình nhỏ)

Mạng chỉ là một MLP nhỏ: 64 -> 128 -> 64 -> 1 (ReLU + sigmoid, tối ưu Adam,
mất mát BCE). Ngân sách huấn luyện rất khiêm tốn: 6000 mẫu train, 2000 mẫu
test, 5 epoch cho mỗi mức R. Toàn bộ thí nghiệm chạy CPU trong **~2 giây**:

```text
python tools/ml_distinguisher.py --rounds 5,6,7 --samples 6000 --epochs 5
```

### 2.4 Kết quả và cách đọc

| R (số vòng) | Accuracy trên 2000 mẫu test | Cách hiểu |
|-------------|-----------------------------|-----------|
| 5 | 0.5970 | Phân biệt rõ trên mức đoán mò 0.50 — mã 5 vòng rò rỉ cấu trúc |
| 6 | 0.5245 | Còn tín hiệu yếu |
| 7 | 0.5070 | Gần như đoán mò — mạng cụ thể này đã "mù" |

Bài học trực quan: **thêm vòng giết distinguisher rất nhanh** — chỉ từ 5 lên
7 vòng, accuracy đã rơi từ ~0.60 về ~0.51. Đó chính là vai trò của số vòng lặp
trong thiết kế mã khối: mỗi vòng khuấy trộn thêm, xóa dần dấu vết của chênh
lệch đầu vào. Và bài học quan trọng nhất nằm ở mục tiếp theo.

## 3. Vì sao "chống được nó" không phải bằng chứng an toàn?

Ở R = 7, mạng của ta chỉ đạt ~0.51, gần như đoán mò. Người mới rất dễ kết luận:
"mã này an toàn rồi". Kết luận đó **sai**, vì bốn lý do:

### 3.1 Kết quả âm tính chỉ nói về đúng một mạng, một ngân sách

Con số 0.51 chỉ có nghĩa duy nhất: **mạng MLP cụ thể này**, với **6000 mẫu**,
**5 epoch**, **chênh lệch cụ thể này**, không tìm ra gì. Đổi bất kỳ yếu tố nào
— mạng sâu hơn, dữ liệu nhiều hơn, chênh lệch khác, huấn luyện lâu hơn —
kết quả có thể đổi. Không tìm thấy chìa khóa trong một căn phòng không chứng
minh chìa khóa không tồn tại; nó chỉ chứng minh **lần tìm này** chưa thấy.

### 3.2 Kẻ tấn công thật không bị giới hạn như ta

Ta tự trói tay mình: vài nghìn mẫu, vài giây CPU, một kiến trúc mạng duy nhất.
Kẻ tấn công thật không ký vào giới hạn đó — họ có thể dùng nhiều dữ liệu hơn,
máy mạnh hơn, kiến trúc mới hơn, hoặc kết hợp ML với thám mã cổ điển. Chống
được "đứa trẻ con" (MLP nhỏ, ngân sách nhỏ) không nói lên điều gì về khả năng
chống "võ sĩ chuyên nghiệp".

### 3.3 An toàn là khẳng định phổ quát, thí nghiệm chỉ là mẫu hữu hạn

"An toàn" nghĩa là **không tồn tại** đòn tấn công nào khả thi — một khẳng định
"với mọi" trên không gian vô hạn các cách tấn công. Một thí nghiệm chỉ kiểm tra
**một điểm** trong không gian đó. Logic cơ bản: một ví dụ không bao giờ chứng
minh được khẳng định phổ quát; nó chỉ có thể **bác bỏ** (tìm ra một đòn tấn
công thành công) chứ không thể **chứng minh** (không còn đòn nào tồn tại).
Distinguisher là công cụ tìm vết nứt, không phải giấy chứng nhận.

### 3.4 Chuẩn mực an toàn thực sự là gì?

Trong thực tế, niềm tin vào một thuật toán đến từ: thuật toán **chuẩn, công
khai**, đã trải qua **nhiều năm bị cộng đồng thám mã toàn cầu "đánh"** mà vẫn
đứng vững (xem nghiên cứu 05), cộng với cài đặt đúng và quản lý khóa tốt.
Không ai kết luận an toàn từ một thí nghiệm ML nội bộ duy nhất — và dự án ta
cũng vậy: mọi khóa thật đều dùng phép toán đã kiểm chứng, mã toy rút gọn vòng
chỉ phục vụ học tập trong `docs/research`.

## 4. Tóm tắt một đoạn

Distinguisher là phép thử "đầu ra của mã có trông ngẫu nhiên không". Thí nghiệm
của ta huấn luyện một mạng nơ-ron nhỏ làm phép thử đó trên mã toy Speck32/64
rút gọn, và thấy mạng phân biệt được ở 5 vòng nhưng "mù" dần ở 6–7 vòng —
minh họa sống động rằng thám mã bằng ML là thật và số vòng có tác dụng. Nhưng
kết quả "mạng không phân biệt được" chỉ là một kết quả âm tính gắn với đúng một
mạng và một ngân sách nhỏ; nó không chứng minh mã an toàn, vì kẻ tấn công thật
không bị giới hạn đó và một thí nghiệm duy nhất không bao giờ chứng minh được
khẳng định phổ quát "không tồn tại đòn tấn công".
