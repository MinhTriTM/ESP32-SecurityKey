# Nghiên cứu 03 — Các dự án liên quan đã tham khảo

## pico-fido (firmware chính của dự án)

FIDO authenticator nguồn mở cho Raspberry Pi Pico và ESP32, hỗ trợ CTAP và U2F. Dự án có bản build cho ESP32-S3 và cộng đồng dùng thực tế. Đây là firmware được chọn làm tầng dùng thật.

- Repo: [polhenarejos/pico-fido](https://github.com/polhenarejos/pico-fido).
- Fork cho board LilyGO T-Dongle S3: [CDRLpart/tdongle-yk](https://github.com/CDRLpart/tdongle-yk).

## esp32_u2f

Triển khai U2F tối giản trên ESP32-S2 và ESP32-S3. Giá trị tham khảo là cách dựng khung U2FHID và message U2F gọn nhẹ. Không đủ tính năng cho mục tiêu dùng thật nên chỉ học ý tưởng.

- Repo: [jocover/esp32_u2f](https://github.com/jocover/esp32_u2f).

## OpenSK của Google

Nền tảng key bảo mật nguồn mở viết bằng Rust trên TockOS, mục tiêu ban đầu là board Nordic nRF52840. Giá trị tham khảo là kiến trúc crypto và cách test CTAP. Không có port chính thức cho ESP32-S3 nên không dùng trực tiếp.

- Giới thiệu: [Help Net Security](https://www.helpnetsecurity.com/2020/01/31/make-security-key/).

## SoloKeys Solo

Key FIDO2 nguồn mở phần cứng lẫn firmware đời đầu, chạy STM32. Giá trị tham khảo là thiết kế mở toàn stack và tool solo-python. Solo đời đầu đã ngừng phát triển mạnh nên không chọn làm nền.

## EvilKey

Dự án tự chế key FIDO2 trên ESP32-S3 có màn hình cảm ứng, log quá trình build rất đáng đọc. Giá trị tham khảo là kinh nghiệm bring-up USB và UX trên S3.

- Nhật ký dự án: [Hackaday.io](https://hackaday.io/project/206807/logs).

## Bài tổng hợp đáng đọc

- Hỏi đáp YubiKey clone bằng ESP32: [UMA Technology](http://umatechnology.org/can-you-build-a-6-yubikey-clone-with-an-esp32-whats-verified/).
- Giải thích claim build 6 đô: [GeekChamp](https://geekchamp.com/can-you-build-an-esp32-security-key-what-the-6-yubikey-clone-claim-proves/).
