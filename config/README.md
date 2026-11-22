# config — Cấu hình hệ thống

## Linux: udev rules cho FIDO

File `70-u2f.rules` cho phép trình duyệt và tool mở key HID mà không cần
sudo. Cài một lần:

```
sudo cp config/70-u2f.rules /etc/udev/rules.d/
sudo udevadm control --reload-rules
sudo udevadm trigger
```

Rút ra cắm lại key, rồi kiểm tra bằng `python tools/fido_check.py`.
Quy tắc gồm key thương mại phổ biến (Yubico…), VID Espressif `303a` cho board
tự build và công thức chung cho mọi HID FIDO (usage page `0xF1D0`).
