//! Sinh crate firmware esp-hal 1.2 từ mẫu theo mã chip.
//!
//! Crate thuần host: chỉ render chuỗi văn bản và ghi file,
//! không cần toolchain nhúng. Dữ liệu chip lấy từ `esp-inventory`
//! để làm nguồn chân lý duy nhất.

use esp_inventory::{tim_chip, TrangThaiRust};
use std::path::Path;

// Phiên bản đã kiểm chứng tồn tại trên crates.io (tra ngày 22/11/2026).
const ESP_HAL: &str = "1.2";
const ESP_PRINTLN: &str = "0.18";
const ESP_BACKTRACE: &str = "0.20";
const ESP_BOOTLOADER: &str = "0.6";

/// LED mặc định trên kit DevKit của từng chip (để mẫu chớp đèn).
fn led_mac_dinh(ma: &str) -> &'static str {
    match ma {
        "esp32" => "GPIO2",
        "esp32s2" => "GPIO18",
        "esp32s3" => "GPIO48",
        "esp32c2" => "GPIO8",
        "esp32c3" => "GPIO8",
        "esp32c5" => "GPIO8",
        "esp32c6" => "GPIO8",
        "esp32c61" => "GPIO8",
        "esp32h2" => "GPIO8",
        _ => "GPIO8",
    }
}

/// Render `Cargo.toml` cho firmware của chip.
pub fn render_cargo_toml(ten_crate: &str, ma_chip: &str) -> Result<String, String> {
    let chip = tim_chip(ma_chip)
        .ok_or_else(|| format!("mã chip lạ: '{ma_chip}' (thử esp32s3, esp32c6...)"))?;
    if !chip.build_duoc() {
        return Err(format!(
            "chip {} trạng thái '{}', chưa sinh được firmware",
            chip.ten,
            chip.trang_thai.ten_viet()
        ));
    }
    let ma = chip.ma;
    Ok(format!(
        r#"[package]
name = "{ten_crate}"
version = "0.1.0"
edition = "2021"
resolver = "2"
rust-version = "1.95"

[dependencies]
esp-hal = {{ version = "{ESP_HAL}", features = ["{ma}"] }}
esp-println = {{ version = "{ESP_PRINTLN}", features = ["{ma}"] }}
esp-backtrace = {{ version = "{ESP_BACKTRACE}", features = ["{ma}", "panic-handler", "println"] }}
esp-bootloader-esp-idf = {{ version = "{ESP_BOOTLOADER}", features = ["{ma}"] }}
log = "0.4"

[profile.dev]
debug = true
opt-level = "s"

[profile.release]
debug = false
opt-level = "s"
lto = true
codegen-units = 1
"#,
    ))
}

/// Render `src/main.rs`: chớp LED + in dòng chào.
pub fn render_main_rs(ma_chip: &str) -> Result<String, String> {
    let chip = tim_chip(ma_chip)
        .ok_or_else(|| format!("mã chip lạ: '{ma_chip}' (thử esp32s3, esp32c6...)"))?;
    if !chip.build_duoc() {
        return Err(format!(
            "chip {} trạng thái '{}', chưa sinh được firmware",
            chip.ten,
            chip.trang_thai.ten_viet()
        ));
    }
    let ma = chip.ma;
    let ten = chip.ten;
    let led = led_mac_dinh(ma);
    Ok(format!(
        r#"//! Ví dụ chào + chớp LED cho {ten} (esp-hal 1.2).
//!
//! LED mặc định: {led} (xem lại sơ đồ chân của đúng kit đang dùng).
//! API theo tài liệu esp-hal 1.2.2 trong cache crates.io ngày 22/11/2026.

#![no_std]
#![no_main]

use esp_backtrace as _;
use esp_hal::{{
    clock::CpuClock,
    gpio::{{Level, Output, OutputConfig}},
    main,
    time::{{Duration, Instant}},
}};
use esp_println::println;

esp_bootloader_esp_idf::esp_app_desc!();

#[main]
fn main() -> ! {{
    let cau_hinh = esp_hal::Config::default().with_cpu_clock(CpuClock::max());
    let ngoai_vi = esp_hal::init(cau_hinh);

    println!("Xin chao tu {ten} ({ma})!");

    let mut led = Output::new(ngoai_vi.{led}, Level::High, OutputConfig::default());

    loop {{
        led.toggle();
        let bat_dau = Instant::now();
        while bat_dau.elapsed() < Duration::from_millis(500) {{}}
    }}
}}
"#,
    ))
}

/// Render `build.rs`: nối script link của esp-hal.
pub fn render_build_rs() -> String {
    r#"//! Script build: nối linker script của esp-hal (linkall.x).

fn main() {
    println!("cargo:rustc-link-arg=-Tlinkall.x");
    // Một số chip cần thêm hàm ROM:
    // println!("cargo:rustc-link-arg=-Trom_functions.x");
}
"#
    .to_string()
}

/// Render `.cargo/config.toml`: target + runner espflash.
pub fn render_cargo_config(ma_chip: &str) -> Result<String, String> {
    let chip = tim_chip(ma_chip)
        .ok_or_else(|| format!("mã chip lạ: '{ma_chip}' (thử esp32s3, esp32c6...)"))?;
    let target = chip
        .target
        .ok_or_else(|| format!("chip {} chưa có target Rust", chip.ten))?;
    Ok(format!(
        r#"[build]
target = "{target}"

[target.{target}]
runner = "espflash flash --monitor"

[env]
ESP_LOG = "info"
"#,
    ))
}

/// Render `README.md` hướng dẫn build cho firmware vừa sinh.
pub fn render_readme(ten_crate: &str, ma_chip: &str) -> Result<String, String> {
    let chip = tim_chip(ma_chip)
        .ok_or_else(|| format!("mã chip lạ: '{ma_chip}' (thử esp32s3, esp32c6...)"))?;
    let target = chip.target.unwrap_or("chua-co-target");
    let cai_toolchain = if chip.can_espup() {
        "Chip Xtensa nên phải cài toolchain fork qua espup trước:\n\n```powershell\ncargo install espup\nespup install\n. $env:USERPROFILE\\export-esp.ps1\n```"
    } else {
        "Chip RISC-V dùng rustc chuẩn, chỉ cần thêm target esp:\n\n```powershell\nrustup target add {target}\n```\n\n(Nếu target esp chưa có trên kênh đang dùng, cài qua espup như chip Xtensa.)"
    };
    Ok(format!(
        r#"# {ten_crate}

Ví dụ chào + chớp LED cho {ten} (mã `{ma}`), sinh tự động bằng `new-esp-firmware`.

- Target: `{target}`
- Toolchain: {toolchain}
- Trạng thái esp-hal: {trang_thai}

## Cài toolchain

{cai_toolchain}

## Build

```powershell
cargo build --release
```

## Nạp và xem log

```powershell
espflash flash --monitor --port COM5 target\{target}\release\{ten_crate}
```

(Thay `COM5` bằng cổng COM của kit.)
"#,
        ten = chip.ten,
        ma = chip.ma,
        toolchain = chip.toolchain,
        trang_thai = chip.trang_thai.ten_viet(),
    ))
}

/// Ghi trọn một crate firmware ra thư mục (tạo thư mục nếu chưa có).
pub fn tao_firmware(ten_crate: &str, ma_chip: &str, thu_muc: &Path) -> Result<(), String> {
    let chip = tim_chip(ma_chip)
        .ok_or_else(|| format!("mã chip lạ: '{ma_chip}' (thử esp32s3, esp32c6...)"))?;
    if chip.trang_thai == TrangThaiRust::KhongCo || chip.trang_thai == TrangThaiRust::ChuaCo {
        return Err(format!(
            "chip {} trạng thái '{}', chưa sinh được firmware",
            chip.ten,
            chip.trang_thai.ten_viet()
        ));
    }
    let ghi = |duong_dan: std::path::PathBuf, noi_dung: String| -> Result<(), String> {
        if let Some(cha) = duong_dan.parent() {
            std::fs::create_dir_all(cha).map_err(|e| format!("không tạo được thư mục: {e}"))?;
        }
        std::fs::write(&duong_dan, noi_dung)
            .map_err(|e| format!("không ghi được {}: {e}", duong_dan.display()))
    };
    ghi(
        thu_muc.join("Cargo.toml"),
        render_cargo_toml(ten_crate, ma_chip)?,
    )?;
    ghi(thu_muc.join("src/main.rs"), render_main_rs(ma_chip)?)?;
    ghi(thu_muc.join("build.rs"), render_build_rs())?;
    ghi(
        thu_muc.join(".cargo/config.toml"),
        render_cargo_config(ma_chip)?,
    )?;
    ghi(
        thu_muc.join("README.md"),
        render_readme(ten_crate, ma_chip)?,
    )?;
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;

    // Mẫu S3: chip của khóa FIDO2 (Xtensa).
    #[test]
    fn mau_s3_day_du() {
        let toml = render_cargo_toml("hello", "esp32s3").unwrap();
        assert!(toml.contains(r#"features = ["esp32s3"]"#));
        assert!(toml.contains("esp-hal"));
        let main = render_main_rs("ESP32-S3").unwrap();
        assert!(main.contains("ESP32-S3"));
        assert!(main.contains("GPIO48"));
        assert!(main.contains("esp_app_desc"));
        let cau_hinh = render_cargo_config("esp32s3").unwrap();
        assert!(cau_hinh.contains("xtensa-esp32s3-none-elf"));
        assert!(cau_hinh.contains("espflash flash --monitor"));
        let doc = render_readme("hello", "esp32s3").unwrap();
        assert!(doc.contains("espup install"));
    }

    // Mẫu C6: chip RISC-V (WiFi 6 + Thread).
    #[test]
    fn mau_c6_day_du() {
        let toml = render_cargo_toml("hello", "esp32c6").unwrap();
        assert!(toml.contains(r#"features = ["esp32c6"]"#));
        let main = render_main_rs("esp32c6").unwrap();
        assert!(main.contains("ESP32-C6"));
        let cau_hinh = render_cargo_config("esp32c6").unwrap();
        assert!(cau_hinh.contains("riscv32imac-esp-espidf"));
        let doc = render_readme("hello", "esp32c6").unwrap();
        assert!(doc.contains("rustup target add"));
    }

    // Chip không hỗ trợ thì từ chối sinh, kèm lý do.
    #[test]
    fn tu_choi_chip_khong_ho_tro() {
        assert!(render_cargo_toml("x", "esp8266").is_err());
        assert!(render_main_rs("esp32h21").is_err());
        assert!(render_cargo_toml("x", "esp99").is_err());
    }

    // Ghi firmware ra đĩa tạo đủ 5 file.
    #[test]
    fn ghi_ra_dia_du_5_file() {
        let thu_muc = std::env::temp_dir().join(format!(
            "mau-firmware-test-{}",
            std::time::SystemTime::now()
                .duration_since(std::time::UNIX_EPOCH)
                .unwrap()
                .as_nanos()
        ));
        tao_firmware("hello", "esp32s3", &thu_muc).unwrap();
        for file in [
            "Cargo.toml",
            "src/main.rs",
            "build.rs",
            ".cargo/config.toml",
            "README.md",
        ] {
            assert!(thu_muc.join(file).exists(), "thiếu file {file}");
        }
        std::fs::remove_dir_all(&thu_muc).ok();
    }
}
