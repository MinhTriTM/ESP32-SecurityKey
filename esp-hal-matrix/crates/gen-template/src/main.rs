//! Chạy dòng lệnh `new-esp-firmware`: sinh crate firmware từ mẫu.
//!
//! Ví dụ:
//! ```powershell
//! new-esp-firmware --chip esp32s3 --ten esp32s3-hello --o firmware/esp32s3-hello
//! ```

use esp_gen_template::tao_firmware;
use std::env;
use std::path::PathBuf;
use std::process::ExitCode;

/// In hướng dẫn dùng rồi trả mã thoát 2.
fn dung() -> ExitCode {
    eprintln!("Dùng: new-esp-firmware --chip <mã> --ten <tên-crate> --o <thư-mục>");
    eprintln!(
        "Ví dụ: new-esp-firmware --chip esp32s3 --ten esp32s3-hello --o firmware/esp32s3-hello"
    );
    eprintln!("Mã chip: esp32, esp32s2, esp32s3, esp32c2, esp32c3, esp32c5, esp32c6, esp32c61, esp32h2, esp32s31, esp32p4");
    ExitCode::from(2)
}

fn main() -> ExitCode {
    let doi_so: Vec<String> = env::args().skip(1).collect();
    let mut chip: Option<String> = None;
    let mut ten: Option<String> = None;
    let mut ra: Option<PathBuf> = None;
    let mut i = 0;
    while i < doi_so.len() {
        match doi_so[i].as_str() {
            "--chip" => {
                i += 1;
                chip = doi_so.get(i).cloned();
            }
            "--ten" => {
                i += 1;
                ten = doi_so.get(i).cloned();
            }
            "--o" => {
                i += 1;
                ra = doi_so.get(i).map(PathBuf::from);
            }
            "--help" | "-h" => return dung(),
            la => {
                eprintln!("Đối số lạ: {la}");
                return dung();
            }
        }
        i += 1;
    }
    let (Some(chip), Some(ten), Some(ra)) = (chip, ten, ra) else {
        eprintln!("Thiếu đối số bắt buộc.");
        return dung();
    };
    match tao_firmware(&ten, &chip, &ra) {
        Ok(()) => {
            println!(
                "Đã sinh firmware '{ten}' cho chip {chip} tại {}",
                ra.display()
            );
            ExitCode::SUCCESS
        }
        Err(loi) => {
            eprintln!("Lỗi: {loi}");
            ExitCode::FAILURE
        }
    }
}
