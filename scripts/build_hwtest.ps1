# Biên dịch sketch hwtest cho ESP32-S3 bằng arduino-cli trong .tooling.
$Root = Split-Path -Parent $PSScriptRoot
$env:ARDUINO_DIRECTORIES_DATA = Join-Path $Root '.tooling/data'
& (Join-Path $Root '.tooling/arduino-cli/arduino-cli.exe') compile `
    --fqbn 'esp32:esp32:esp32s3:CDCOnBoot=cdc,USBMode=default,FlashMode=dio,PSRAM=opi' `
    (Join-Path $Root 'firmware/hwtest')
