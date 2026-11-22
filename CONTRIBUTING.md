# Contributing · Đóng góp · 贡献指南

## English

1. Fork, branch from `main`, open a pull request. One change per PR.
2. Every code change needs a regression test: extend the tool's `--self-test`
   (repo convention, no separate `tests/` directory).
3. Before pushing, run the full gate and keep it green:
   `scripts/run_tests.ps1` (Windows) or `scripts/run_tests.sh` (Linux),
   including `lintsec` and `web_firmware --check`.
4. Commit messages in Vietnamese or English, imperative mood, short.
5. Never commit secrets, keys, passwords or private data. Check
   `git status` before every commit.
6. User-facing web text must ship in all 3 languages (VI/EN/CN) — see the
   `I18N` dictionary in `web/index.html`. Tool CLI output stays Vietnamese
   (documented choice); docs beyond README stay Vietnamese for now.

## Tiếng Việt

1. Fork, branch từ `main`, mở pull request. Mỗi PR một thay đổi.
2. Mọi sửa code phải kèm test hồi quy: mở rộng `--self-test` của đúng tool
   (quy ước repo, không lập thư mục `tests/` riêng).
3. Trước khi đẩy, chạy cổng kiểm tra đầy đủ và giữ xanh:
   `scripts/run_tests.ps1` (Windows) hoặc `scripts/run_tests.sh` (Linux),
   gồm cả `lintsec` và `web_firmware --check`.
4. Commit message tiếng Việt hoặc tiếng Anh, ngắn gọn, dạng mệnh lệnh.
5. Không bao giờ commit bí mật, khóa, mật khẩu hay dữ liệu riêng tư. Kiểm tra
   `git status` trước mỗi commit.
6. Chữ trên web dùng thật phải đủ 3 ngôn ngữ (VI/EN/CN) — xem từ điển `I18N`
   trong `web/index.html`. Tool CLI giữ tiếng Việt (đã chốt); tài liệu ngoài
   README暫 giữ tiếng Việt.

## 简体中文

1. Fork，从 `main` 建分支，提交 pull request，每个 PR 只做一件事。
2. 每次代码修改都要有回归测试：扩展对应工具的 `--self-test`
   （仓库约定，不另建 `tests/` 目录）。
3. 推送前跑通完整检查并保持绿色：`scripts/run_tests.ps1`（Windows）
   或 `scripts/run_tests.sh`（Linux），包括 `lintsec` 和
   `web_firmware --check`。
4. Commit 信息用越南语或英语，祈使语气，简短。
5. 绝不提交密钥、密码或隐私数据，每次 commit 前检查 `git status`。
6. 面向用户的网页文字必须提供 3 种语言（VI/EN/CN）——见
   `web/index.html` 中的 `I18N` 词典。命令行工具输出保持越南语
   （既定选择）；README 之外的文档暂保持越南语。
