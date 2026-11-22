//! Dựng câu lệnh espflash/espefuse để bật Secure Boot v2 + Flash Encryption.
//!
//! Crate thuần host: chỉ dựng chuỗi lệnh, không tự chạy lệnh nguy hiểm.
//! Ghi eFuse là thao tác MỘT CHIỀU (không hoàn tác), nên lệnh thật luôn
//! phải qua hàm [`kiem_tra_truoc_thuc_thi`]: bắt cờ `--toi-hieu-rui-ro`
//! và mã chip đọc về phải khớp chip khai báo.

use esp_inventory::{tim_chip, TrangThaiRust};

/// Một bước trong kế hoạch khóa chip.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Buoc {
    /// Số thứ tự (bắt đầu từ 1).
    pub so_thu_tu: usize,
    /// Giải thích tiếng Việt: bước này làm gì.
    pub mo_ta: String,
    /// Dòng lệnh đầy đủ để chạy trong PowerShell.
    pub lenh: String,
    /// `true` nếu bước ghi eFuse (một chiều, không hoàn tác).
    pub nguy_hiem: bool,
}

/// Kế hoạch khóa một con chip cụ thể.
#[derive(Debug, Clone)]
pub struct KeHoach {
    /// Tên chip, ví dụ `ESP32-S3`.
    pub chip: String,
    /// Cổng COM, ví dụ `COM5`.
    pub cong_com: String,
    /// Các bước theo đúng thứ tự phải chạy.
    pub buoc: Vec<Buoc>,
    /// Cảnh báo an toàn phải đọc trước khi chạy.
    pub canh_bao: Vec<String>,
}

/// Dựng kế hoạch bật Secure Boot v2 + Flash Encryption cho chip.
///
/// `ma_chip` chấp nhận mọi cách viết mà `esp-inventory` hiểu
/// (`esp32s3`, `ESP32-S3`...). `cong_com` là cổng trên PC (`COM5`...),
/// `toc_do` là baud nạp (`460800`...).
pub fn dung_ke_hoach(ma_chip: &str, cong_com: &str, toc_do: &str) -> Result<KeHoach, String> {
    let chip = tim_chip(ma_chip)
        .ok_or_else(|| format!("mã chip lạ: '{ma_chip}' (thử esp32s3, esp32c6...)"))?;
    match chip.trang_thai {
        TrangThaiRust::KhongCo => {
            return Err(format!(
                "chip {} không được esp-rs hỗ trợ, không có quy trình khóa chuẩn",
                chip.ten
            ));
        }
        TrangThaiRust::ChuaCo => {
            return Err(format!(
                "chip {} chưa có esp-hal nên chưa có quy trình khóa đã kiểm chứng",
                chip.ten
            ));
        }
        TrangThaiRust::DayDu | TrangThaiRust::MoiThieu => {}
    }
    let ma = chip.ma;
    let mut buoc = Vec::new();
    let mut them = |mo_ta: &str, lenh: String, nguy_hiem: bool| {
        let so_thu_tu = buoc.len() + 1;
        buoc.push(Buoc {
            so_thu_tu,
            mo_ta: mo_ta.to_string(),
            lenh,
            nguy_hiem,
        });
    };

    // Bước đọc (an toàn) luôn chạy trước để xác minh đúng chip.
    them(
        "Đọc thông tin board để xác minh đúng mã chip",
        format!("espflash board-info --port {cong_com}"),
        false,
    );
    them(
        "Đọc trạng thái eFuse hiện tại (xem đã khóa gì chưa)",
        format!("espefuse --chip {ma} --port {cong_com} summary"),
        false,
    );
    // Sinh khóa nằm trên PC, chưa ghi gì vào chip.
    them(
        "Sinh khóa Flash Encryption trên PC (giữ file này bí mật)",
        "espsecure generate-flash-encryption-key khoa-flash.key".to_string(),
        false,
    );
    them(
        "Sinh khóa ký Secure Boot trên PC (giữ file này bí mật)",
        "espsecure generate-signing-key --version 2 khoa-ky.pem".to_string(),
        false,
    );
    // Từ đây là các bước ghi một chiều vào eFuse.
    let (ten_bit_khoa_boot, ten_bit_ma_hoa) = bit_efuse(ma);
    them(
        "Ghi khóa Flash Encryption vào eFuse (MỘT CHIỀU)",
        format!("espefuse --chip {ma} --port {cong_com} burn-key BLOCK_KEY0 khoa-flash.key XTS_AES_128_KEY"),
        true,
    );
    them(
        &format!("Bật Secure Boot v2: ghi bit {ten_bit_khoa_boot} (MỘT CHIỀU)"),
        format!("espefuse --chip {ma} --port {cong_com} burn-efuse {ten_bit_khoa_boot}"),
        true,
    );
    them(
        &format!("Bật Flash Encryption: ghi bit {ten_bit_ma_hoa} (MỘT CHIỀU)"),
        format!("espefuse --chip {ma} --port {cong_com} burn-efuse {ten_bit_ma_hoa}"),
        true,
    );
    them(
        "Nạp bootloader + firmware đã ký ở tốc độ cao",
        format!(
            "espflash write-bin --chip {ma} --port {cong_com} --baud {toc_do} 0x0 bootloader-digest.bin 0x10000 firmware.bin"
        ),
        false,
    );

    let mut canh_bao = vec![
        "eFuse chỉ ghi được MỘT CHIỀU: ghi sai bit là hỏng chip vĩnh viễn.".to_string(),
        "Hai file khoa-flash.key và khoa-ky.pem mất là mất khả năng cập nhật/sửa chữa; sao lưu ngoại tuyến.".to_string(),
        "Luôn chạy --dry-run và đọc từng lệnh trước khi chạy thật.".to_string(),
        "Tên bit eFuse khác nhau theo chip; đối chiếu 'espefuse --chip <mã> --help' trước khi chạy.".to_string(),
    ];
    if ma == "esp32p4" {
        canh_bao.push(
            "ESP32-P4 silicon rev ≤v3.2 lỗi ECDSA ROM: phải ký Secure Boot bằng RSA-3072, không dùng ECDSA."
                .to_string(),
        );
    }
    if ma == "esp32s31" {
        canh_bao.push(
            "ESP32-S31 còn sơ khai: quy trình trên là mẫu tham khảo, phải đối chiếu tài liệu mới nhất của Espressif."
                .to_string(),
        );
    }

    Ok(KeHoach {
        chip: chip.ten.to_string(),
        cong_com: cong_com.to_string(),
        buoc,
        canh_bao,
    })
}

/// Tên bit eFuse theo từng dòng chip.
///
/// Ghi chú trung thực: tên bit lấy theo quy ước espefuse của IDF 5.x;
/// luôn đối chiếu `espefuse --chip <mã> --help` vì Espressif có thể đổi tên.
fn bit_efuse(ma: &str) -> (&'static str, &'static str) {
    match ma {
        // ESP32 đời đầu dùng tên bit khác dòng mới.
        "esp32" => ("ABS_DONE_0", "FLASH_CRYPT_CNT"),
        "esp32s2" => ("SECURE_BOOT_EN", "FLASH_CRYPT_CNT"),
        _ => ("SECURE_BOOT_EN", "SPI_BOOT_CRYPT_CNT"),
    }
}

/// Kiểm tra điều kiện trước khi chạy lệnh ghi eFuse thật.
///
/// Bắt buộc: có cờ `--toi-hieu-rui-ro` VÀ mã chip đọc về
/// (`--ma-doc-ve`, lấy từ `espflash board-info`) khớp chip khai báo.
pub fn kiem_tra_truoc_thuc_thi(
    chip_khai_bao: &str,
    ma_doc_ve: Option<&str>,
    co_co_rui_ro: bool,
) -> Result<(), String> {
    if !co_co_rui_ro {
        return Err(
            "từ chối chạy thật: thiếu cờ --toi-hieu-rui-ro (ghi eFuse là một chiều)".to_string(),
        );
    }
    let ma_doc_ve = ma_doc_ve
        .ok_or_else(|| "từ chối chạy thật: thiếu --ma-doc-ve để đối chiếu chip".to_string())?;
    let khai_bao = esp_inventory::chuan_hoa_ma(chip_khai_bao);
    let doc_ve = esp_inventory::chuan_hoa_ma(ma_doc_ve);
    if khai_bao != doc_ve {
        return Err(format!(
            "từ chối chạy thật: chip khai báo '{chip_khai_bao}' khác chip đọc về '{ma_doc_ve}'"
        ));
    }
    Ok(())
}

/// Định dạng kế hoạch thành văn bản cho `--dry-run`.
pub fn in_ke_hoach(ke_hoach: &KeHoach) -> String {
    let mut ra = String::new();
    ra.push_str(&format!(
        "Kế hoạch khóa {} qua {}\n\nCẢNH BÁO:\n",
        ke_hoach.chip, ke_hoach.cong_com
    ));
    for canh_bao in &ke_hoach.canh_bao {
        ra.push_str(&format!("- {canh_bao}\n"));
    }
    ra.push_str("\nCÁC BƯỚC:\n");
    for buoc in &ke_hoach.buoc {
        let nhan = if buoc.nguy_hiem {
            " [GHI EFUSE - MỘT CHIỀU]"
        } else {
            ""
        };
        ra.push_str(&format!(
            "\n{}. {}{}\n   {}\n",
            buoc.so_thu_tu, buoc.mo_ta, nhan, buoc.lenh
        ));
    }
    ra
}

#[cfg(test)]
mod tests {
    use super::*;

    // Kế hoạch S3 phải đủ 8 bước, lệnh nào cũng gắn đúng chip/cổng.
    #[test]
    fn ke_hoach_s3_du_8_buoc() {
        let kh = dung_ke_hoach("esp32s3", "COM5", "460800").unwrap();
        assert_eq!(kh.chip, "ESP32-S3");
        assert_eq!(kh.buoc.len(), 8);
        assert!(kh.buoc[0].lenh.contains("board-info"));
        assert!(kh.buoc[1].lenh.contains("--chip esp32s3"));
        assert!(kh.buoc[1].lenh.contains("COM5"));
        assert!(kh.buoc[4].nguy_hiem);
        assert!(kh.buoc[4].lenh.contains("burn-key"));
        assert!(kh.buoc[5].lenh.contains("SECURE_BOOT_EN"));
        assert!(kh.buoc[6].lenh.contains("SPI_BOOT_CRYPT_CNT"));
        assert!(kh.buoc[7].lenh.contains("460800"));
    }

    // Kế hoạch C6: lệnh espefuse phải gắn chip c6.
    #[test]
    fn ke_hoach_c6_gan_dung_chip() {
        let kh = dung_ke_hoach("ESP32-C6", "COM7", "115200").unwrap();
        assert!(kh.buoc[1].lenh.contains("--chip esp32c6"));
        assert!(kh.buoc[7].lenh.contains("--chip esp32c6"));
        assert!(kh.buoc[7].lenh.contains("COM7"));
    }

    // ESP32 đời đầu dùng tên bit cũ ABS_DONE_0.
    #[test]
    fn esp32_doi_dau_dung_bit_cu() {
        let kh = dung_ke_hoach("esp32", "COM5", "460800").unwrap();
        assert!(kh.buoc[5].lenh.contains("ABS_DONE_0"));
    }

    // P4 phải cảnh báo RSA-3072 vì lỗi ECDSA ROM.
    #[test]
    fn p4_canh_bao_rsa3072() {
        let kh = dung_ke_hoach("esp32p4", "COM5", "460800").unwrap();
        assert!(kh.canh_bao.iter().any(|c| c.contains("RSA-3072")));
    }

    // Chip không/chưa hỗ trợ thì từ chối dựng kế hoạch.
    #[test]
    fn tu_choi_chip_khong_khoa_duoc() {
        assert!(dung_ke_hoach("esp8266", "COM5", "460800").is_err());
        assert!(dung_ke_hoach("esp32h21", "COM5", "460800").is_err());
        assert!(dung_ke_hoach("esp99", "COM5", "460800").is_err());
    }

    // Thiếu cờ rủi ro thì từ chối chạy thật.
    #[test]
    fn thieu_co_rui_ro_thi_tu_choi() {
        assert!(kiem_tra_truoc_thuc_thi("esp32s3", Some("esp32s3"), false).is_err());
    }

    // Mã đọc về khác khai báo thì từ chối (chống khóa nhầm chip).
    #[test]
    fn sai_chip_doc_ve_thi_tu_choi() {
        assert!(kiem_tra_truoc_thuc_thi("esp32s3", Some("esp32c6"), true).is_err());
        assert!(kiem_tra_truoc_thuc_thi("esp32s3", None, true).is_err());
    }

    // Đủ cờ + khớp chip (kể cả viết hoa/gạch ngang) thì cho qua.
    #[test]
    fn du_dieu_kien_thi_cho_qua() {
        assert!(kiem_tra_truoc_thuc_thi("esp32s3", Some("ESP32-S3"), true).is_ok());
    }

    // Văn bản dry-run phải liệt kê cảnh báo và lệnh.
    #[test]
    fn van_ban_dry_run_day_du() {
        let kh = dung_ke_hoach("esp32s3", "COM5", "460800").unwrap();
        let van_ban = in_ke_hoach(&kh);
        assert!(van_ban.contains("MỘT CHIỀU"));
        assert!(van_ban.contains("burn-efuse"));
        assert!(van_ban.contains("khoa-flash.key"));
    }
}
