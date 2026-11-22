#!/usr/bin/env bash
# Biên dịch sketch hwtest cho ESP32-S3. Cần arduino-cli + core ESP32 trên máy.
set -euo pipefail
if ! command -v arduino-cli >/dev/null; then
  echo "Chưa có arduino-cli. Cài theo https://arduino.github.io/arduino-cli/ rồi cài core esp32:esp32."
  exit 1
fi
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
arduino-cli compile --fqbn 'esp32:esp32:esp32s3:CDCOnBoot=cdc,USBMode=default' firmware/hwtest
