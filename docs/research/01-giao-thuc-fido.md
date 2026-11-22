# Nghiên cứu 01 — Giao thức FIDO: U2F, CTAP1, CTAP2, WebAuthn

## Bản đồ thuật ngữ

U2F là thế hệ đầu: khóa làm yếu tố xác thực thứ hai. CTAP1 là tên chuẩn hóa của U2F. CTAP2 là thế hệ hai, thêm đăng nhập không mật khẩu và quản lý credential. WebAuthn là API phía trình duyệt gọi xuống authenticator qua CTAP. FIDO2 gồm CTAP2 và WebAuthn.

Key trong dự án này nói cả CTAP1 và CTAP2 nên dịch vụ cũ và mới đều dùng được.

## Tầng truyền tải CTAPHID

Cả CTAP1 và CTAP2 đều chạy trên USB HID với usage page 0xF1D0. Mỗi packet 64 byte. Gói mở đầu gồm CID 4 byte, mã lệnh 1 byte, độ dài 2 byte và tối đa 57 byte dữ liệu. Gói tiếp theo gồm CID, số thứ tự và 59 byte dữ liệu.

Các lệnh nền dùng trong tool kiểm tra: INIT 0x06 để mở kênh mới, PING 0x01 để kiểm tra echo, MSG 0x03 cho message U2F, CBOR 0x10 cho message CTAP2, ERROR 0x3F khi lỗi. CID broadcast 0xFFFFFFFF chỉ dùng cho INIT đầu tiên.

## U2F (CTAP1)

Hai thao tác chính là Register và Authenticate. Register tạo cặp khóa gắn với AppID của dịch vụ và trả public key về. Authenticate ký thử thách từ server sau khi người dùng chạm nút. Private key không rời key.

## CTAP2 và WebAuthn

CTAP2 nhắn tin bằng CBOR thay vì APDU thô. Ba lệnh cốt lõi: MakeCredential tạo credential mới, GetAssertion ký thử thách đăng nhập, GetInfo hỏi khả năng của key. ClientPin đặt và xác minh PIN, Reset xóa trắng key.

WebAuthn phía web gọi hai hàm tương ứng: tạo credential khi đăng ký và lấy assertion khi đăng nhập. Trình duyệt lo phần giao tiếp CTAP, trang web không bao giờ thấy private key.

## Resident key và passkey

Resident key lưu credential trên key để đăng nhập không cần gõ tên tài khoản. Passkey là cách gọi thân thiện của credential FIDO2 có thể đồng bộ hoặc gắn thiết bị. Pico-fido hỗ trợ resident key nên dùng được luồng passkey cơ bản.

## Nguồn chính

- Chuẩn CTAP của FIDO Alliance: [CTAP 2.3](https://fidoalliance.org/specs/fido-v2.3-ps-20260226/fido-client-to-authenticator-protocol-v2.3-ps-20260226.html).
- So sánh FIDO2 và U2F: [Beyond Identity](https://www.beyondidentity.com/resource/fido2-vs-u2f-whats-the-difference).
- Giải thích họ thuật ngữ: [WebAuthn Works](https://medium.com/webauthnworks/sorting-fido-ctap-webauthn-terminology-7d32067c0b01).
