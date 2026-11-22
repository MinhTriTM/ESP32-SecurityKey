//! Chạy dòng lệnh `esp-provision`: in hoặc chạy kế hoạch khóa chip.
//!
//! Mặc định chỉ in lệnh (`--dry-run`). Muốn chạy thật phải thêm đồng thời:
//! `--thuc-thi --toi-hieu-rui-ro --ma-doc-ve <mã đọc từ board-info>`.
//!
//! Ví dụ:
//! ```powershell
//! esp-provision --chip esp32s3 --port COM5 --dry-run
//! ```

use esp_provision::{dung_ke_hoach, in_ke_hoach, kiem_tra_truoc_thuc_thi};
use std::env;
use std::process::ExitCode;

/// In hướng dẫn dùng rồi trả mã thoát 2.
fn dung() -> ExitCode {
    eprintln!("Dùng: esp-provision --chip <mã> [--port COM5] [--toc-do 460800] [--dry-run]");
    eprintln!("     esp-provision --chip <mã> --thuc-thi --toi-hieu-rui-ro --ma-doc-ve <mã> [--port COM5]");
    eprintln!("Ví dụ: esp-provision --chip esp32s3 --port COM5 --dry-run");
    ExitCode::from(2)
}

fn main() -> ExitCode {
    let doi_so: Vec<String> = env::args().skip(1).collect();
    let mut chip: Option<String> = None;
    let mut cong: String = "COM5".to_string();
    let mut toc_do: String = "460800".to_string();
    let mut thuc_thi = false;
    let mut hieu_rui_ro = false;
    let mut ma_doc_ve: Option<String> = None;
    let mut i = 0;
    while i < doi_so.len() {
        match doi_so[i].as_str() {
            "--chip" => {
                i += 1;
                chip = doi_so.get(i).cloned();
            }
            "--port" => {
                i += 1;
                if let Some(p) = doi_so.get(i) {
                    cong = p.clone();
                }
            }
            "--toc-do" => {
                i += 1;
                if let Some(t) = doi_so.get(i) {
                    toc_do = t.clone();
                }
            }
            "--dry-run" => {}
            "--thuc-thi" => thuc_thi = true,
            "--toi-hieu-rui-ro" => hieu_rui_ro = true,
            "--ma-doc-ve" => {
                i += 1;
                ma_doc_ve = doi_so.get(i).cloned();
            }
            "--help" | "-h" => return dung(),
            la => {
                eprintln!("Đối số lạ: {la}");
                return dung();
            }
        }
        i += 1;
    }
    let Some(chip) = chip else {
        eprintln!("Thiếu --chip bắt buộc.");
        return dung();
    };
    let ke_hoach = match dung_ke_hoach(&chip, &cong, &toc_do) {
        Ok(kh) => kh,
        Err(loi) => {
            eprintln!("Lỗi: {loi}");
            return ExitCode::FAILURE;
        }
    };
    if !thuc_thi {
        println!("(Chế độ dry-run: chỉ in lệnh, không chạy gì.)\n");
        println!("{}", in_ke_hoach(&ke_hoach));
        return ExitCode::SUCCESS;
    }
    if let Err(loi) = kiem_tra_truoc_thuc_thi(&chip, ma_doc_ve.as_deref(), hieu_rui_ro) {
        eprintln!("Lỗi: {loi}");
        return ExitCode::FAILURE;
    }
    // Chạy thật từng bước theo đúng thứ tự; dừng ngay khi một bước lỗi.
    for buoc in &ke_hoach.buoc {
        println!("Bước {}: {}", buoc.so_thu_tu, buoc.mo_ta);
        println!("> {}", buoc.lenh);
        let chay = if cfg!(windows) {
            std::process::Command::new("cmd")
                .args(["/C", &buoc.lenh])
                .status()
        } else {
            std::process::Command::new("sh")
                .args(["-c", &buoc.lenh])
                .status()
        };
        match chay {
            Ok(trang_thai) if trang_thai.success() => {}
            Ok(trang_thai) => {
                eprintln!("Dừng: bước {} thoát với mã {trang_thai}", buoc.so_thu_tu);
                return ExitCode::FAILURE;
            }
            Err(loi) => {
                eprintln!("Dừng: không chạy được bước {}: {loi}", buoc.so_thu_tu);
                return ExitCode::FAILURE;
            }
        }
    }
    println!("Xong kế hoạch khóa {}.", ke_hoach.chip);
    ExitCode::SUCCESS
}
