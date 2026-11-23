# Chạy mọi self-test Python của repo. Thoát mã != 0 nếu có test hỏng.
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root
$env:PYTHONPATH = (Join-Path $Root '.tooling/pylibs')
# pqc cần DLL liboqs native trong .tooling/oqs (xem docstring tools/pqc.py).
$env:OQS_INSTALL_PATH = (Join-Path $Root '.tooling/oqs')
$fail = 0
foreach ($tool in @('secureio', 'cborx', 'lintsec', 'fido_check', 'hid_echo', 'split_secret', 'mnemonic', 'vault', 'pqc', 'keymgr', 'gen_fe_key', 'ml_distinguisher', 'kanzo', 'vien_nhip_tim', 'vien_cong')) {
    Write-Output "=== $tool ==="
    python "tools/$tool.py" --self-test
    if ($LASTEXITCODE -ne 0) { $fail = 1 }
}
Write-Output "=== web_firmware --check ==="
python tools/web_firmware.py --check
if ($LASTEXITCODE -ne 0) { $fail = 1 }
exit $fail
