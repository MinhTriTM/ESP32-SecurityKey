# scripts — Script một lệnh

Mỗi việc lặp lại có đúng một script cho Windows (`.ps1`) và một cho Linux
(`.sh`). Chạy từ thư mục gốc repo.

| Script | Việc |
|--------|------|
| `run_tests.ps1` / `run_tests.sh` | Chạy mọi self-test + kiểm tra manifest firmware |
| `build_hwtest.ps1` / `build_hwtest.sh` | Biên dịch sketch hwtest (bản OTG) |
| `build_pico_fido.ps1` / `build_pico_fido.sh` | Build pico-fido v8.2 (`plain`/`hardened`), gộp bin, sinh manifest |
| `flash_win.ps1` / `flash_linux.sh` | Mẫu quy trình flash pico-fido (đọc kỹ từng lệnh, không chạy mù) |
| `web_flasher.ps1` / `web_flasher.sh` | Mở siêu web nạp qua `http://localhost:8000` |

Script PowerShell cần chạy với `powershell -ExecutionPolicy Bypass -File
scripts/<ten>.ps1` nếu máy chặn script lạ.
