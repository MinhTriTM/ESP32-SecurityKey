//! Ví dụ chào + chớp LED cho ESP32-C6 (esp-hal 1.2).
//!
//! LED mặc định: GPIO8 (xem lại sơ đồ chân của đúng kit đang dùng).
//! API theo tài liệu esp-hal 1.2.2 trong cache crates.io ngày 22/11/2026.

#![no_std]
#![no_main]

use esp_backtrace as _;
use esp_hal::{
    clock::CpuClock,
    gpio::{Level, Output, OutputConfig},
    main,
    time::{Duration, Instant},
};
use esp_println::println;

esp_bootloader_esp_idf::esp_app_desc!();

#[main]
fn main() -> ! {
    let cau_hinh = esp_hal::Config::default().with_cpu_clock(CpuClock::max());
    let ngoai_vi = esp_hal::init(cau_hinh);

    println!("Xin chao tu ESP32-C6 (esp32c6)!");

    let mut led = Output::new(ngoai_vi.GPIO8, Level::High, OutputConfig::default());

    loop {
        led.toggle();
        let bat_dau = Instant::now();
        while bat_dau.elapsed() < Duration::from_millis(500) {}
    }
}
