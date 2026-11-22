//! Danh mục chip ESP và trạng thái hỗ trợ Rust.
//!
//! Crate thuần host (chạy trên PC), không phụ thuộc ngoài.
//! Dữ liệu khớp tài liệu `docs/DANH-MUC-ESP.md`.

/// Trạng thái hỗ trợ của esp-hal đối với một chip.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum TrangThaiRust {
    /// esp-hal hỗ trợ đầy đủ, dùng được cho sản phẩm.
    DayDu,
    /// Đã có feature trong esp-hal nhưng còn thiếu ngoại vi/bảo mật.
    MoiThieu,
    /// Chưa có esp-hal (đang lấy mẫu / mới công bố).
    ChuaCo,
    /// esp-rs tuyên bố không hỗ trợ (dòng ESP8266).
    KhongCo,
}

impl TrangThaiRust {
    /// Tên tiếng Việt ngắn gọn của trạng thái.
    pub fn ten_viet(&self) -> &'static str {
        match self {
            TrangThaiRust::DayDu => "đầy đủ",
            TrangThaiRust::MoiThieu => "mới/thiếu",
            TrangThaiRust::ChuaCo => "chưa có",
            TrangThaiRust::KhongCo => "không hỗ trợ",
        }
    }
}

/// Một dòng chip ESP.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct Chip {
    /// Mã chuẩn esp-rs, ví dụ `esp32s3`.
    pub ma: &'static str,
    /// Tên hiển thị, ví dụ `ESP32-S3`.
    pub ten: &'static str,
    /// Nhân CPU, ví dụ `2x Xtensa LX7`.
    pub nhan: &'static str,
    /// Xung nhịp tối đa, ví dụ `240 MHz`.
    pub xung: &'static str,
    /// Radio tích hợp (WiFi/Bluetooth/15.4).
    pub radio: &'static str,
    /// Điểm nổi bật để chọn chip.
    pub dac_diem: &'static str,
    /// Trạng thái hỗ trợ esp-hal.
    pub trang_thai: TrangThaiRust,
    /// Target Rust (`None` khi chưa có toolchain Rust).
    pub target: Option<&'static str>,
    /// Toolchain cần dùng.
    pub toolchain: &'static str,
    /// Tính năng bảo mật liên quan (Secure Boot, Flash Encryption...).
    pub bao_mat: &'static str,
}

impl Chip {
    /// Chip có build được bằng esp-hal hiện tại không.
    pub fn build_duoc(&self) -> bool {
        matches!(
            self.trang_thai,
            TrangThaiRust::DayDu | TrangThaiRust::MoiThieu
        ) && self.target.is_some()
    }

    /// Chip có cần toolchain fork Xtensa qua espup không.
    pub fn can_espup(&self) -> bool {
        matches!(self.target, Some(t) if t.starts_with("xtensa-"))
    }
}

/// Toàn bộ 14 chip ESP32 + ESP8266 (đánh dấu không hỗ trợ).
pub static ALL_CHIPS: &[Chip] = &[
    Chip {
        ma: "esp32",
        ten: "ESP32",
        nhan: "2x Xtensa LX6",
        xung: "240 MHz",
        radio: "WiFi 4 + Bluetooth Classic + BLE 4.2",
        dac_diem: "Chip quốc dân đời đầu, nhiều GPIO, cảm biến Hall/nhiệt độ",
        trang_thai: TrangThaiRust::DayDu,
        target: Some("xtensa-esp32-none-elf"),
        toolchain: "espup (fork Xtensa)",
        bao_mat: "Secure Boot v1 (ECO3+ thêm v2), Flash Encryption AES, eFuse một chiều",
    },
    Chip {
        ma: "esp32s2",
        ten: "ESP32-S2",
        nhan: "1x Xtensa LX7",
        xung: "240 MHz",
        radio: "WiFi 4 (không Bluetooth)",
        dac_diem: "USB OTG native, nhiều ADC, giá rẻ cho thiết bị USB",
        trang_thai: TrangThaiRust::DayDu,
        target: Some("xtensa-esp32s2-none-elf"),
        toolchain: "espup (fork Xtensa)",
        bao_mat: "Secure Boot v2, Flash Encryption XTS-AES, HMAC/DS",
    },
    Chip {
        ma: "esp32s3",
        ten: "ESP32-S3",
        nhan: "2x Xtensa LX7",
        xung: "240 MHz",
        radio: "WiFi 4 + BLE 5.0",
        dac_diem: "USB OTG, lệnh AI vector, PSRAM octal; chip của khóa FIDO2 dự án mẹ",
        trang_thai: TrangThaiRust::DayDu,
        target: Some("xtensa-esp32s3-none-elf"),
        toolchain: "espup (fork Xtensa)",
        bao_mat: "Secure Boot v2, Flash Encryption XTS-AES, HMAC/DS/RSA/ECC, chống rollback",
    },
    Chip {
        ma: "esp32s31",
        ten: "ESP32-S31",
        nhan: "2x RISC-V",
        xung: "320 MHz",
        radio: "WiFi 6 + BT 5.4 + 802.15.4",
        dac_diem: "Đời mới hướng WiFi 6, thay S3 cho sản phẩm mới",
        trang_thai: TrangThaiRust::MoiThieu,
        target: Some("riscv32imac-esp-espidf"),
        toolchain: "rustc chuẩn + target esp",
        bao_mat: "Secure Boot v2, Flash Encryption; esp-hal còn sơ khai",
    },
    Chip {
        ma: "esp32c2",
        ten: "ESP32-C2 (ESP8684)",
        nhan: "1x RISC-V",
        xung: "120 MHz",
        radio: "WiFi 4 + BLE 5.0",
        dac_diem: "Rẻ nhất, RAM/Flash nhỏ, đường nâng cấp từ ESP8266",
        trang_thai: TrangThaiRust::DayDu,
        target: Some("riscv32imc-esp-espidf"),
        toolchain: "rustc chuẩn + target esp",
        bao_mat: "Secure Boot v2, Flash Encryption XTS-AES",
    },
    Chip {
        ma: "esp32c3",
        ten: "ESP32-C3",
        nhan: "1x RISC-V",
        xung: "160 MHz",
        radio: "WiFi 4 + BLE 5.0",
        dac_diem: "RISC-V quốc dân, USB Serial/JTAG gỡ lỗi trực tiếp",
        trang_thai: TrangThaiRust::DayDu,
        target: Some("riscv32imc-esp-espidf"),
        toolchain: "rustc chuẩn + target esp",
        bao_mat: "Secure Boot v2, Flash Encryption XTS-AES, HMAC/DS",
    },
    Chip {
        ma: "esp32c5",
        ten: "ESP32-C5",
        nhan: "1x RISC-V",
        xung: "240 MHz",
        radio: "WiFi 6 hai băng tần 2.4 + 5 GHz + BLE + 15.4",
        dac_diem: "Chip WiFi 6 băng tần 5 GHz duy nhất của Espressif",
        trang_thai: TrangThaiRust::DayDu,
        target: Some("riscv32imac-esp-espidf"),
        toolchain: "rustc chuẩn + target esp",
        bao_mat: "Secure Boot v2, Flash Encryption; silicon mới cần kiểm tra rev",
    },
    Chip {
        ma: "esp32c6",
        ten: "ESP32-C6",
        nhan: "1x RISC-V",
        xung: "160 MHz",
        radio: "WiFi 6 + BLE 5.3 + 802.15.4 (Thread/Zigbee)",
        dac_diem: "Matter/Thread, firmware mẫu thứ hai của repo này",
        trang_thai: TrangThaiRust::DayDu,
        target: Some("riscv32imac-esp-espidf"),
        toolchain: "rustc chuẩn + target esp",
        bao_mat: "Secure Boot v2, Flash Encryption XTS-AES, HMAC/ECC",
    },
    Chip {
        ma: "esp32c61",
        ten: "ESP32-C61",
        nhan: "1x RISC-V",
        xung: "160 MHz",
        radio: "WiFi 6 + BLE + 15.4 (rút gọn từ C6)",
        dac_diem: "Bản rút gọn chân cắm/flash của C6 cho thiết bị nhỏ",
        trang_thai: TrangThaiRust::DayDu,
        target: Some("riscv32imac-esp-espidf"),
        toolchain: "rustc chuẩn + target esp",
        bao_mat: "Như ESP32-C6",
    },
    Chip {
        ma: "esp32h2",
        ten: "ESP32-H2",
        nhan: "1x RISC-V",
        xung: "96 MHz",
        radio: "BLE 5.3 + 802.15.4, KHÔNG WiFi",
        dac_diem: "Node Thread/Zigbee/Matter tiết kiệm pin",
        trang_thai: TrangThaiRust::DayDu,
        target: Some("riscv32imac-esp-espidf"),
        toolchain: "rustc chuẩn + target esp",
        bao_mat: "Secure Boot v2, Flash Encryption XTS-AES",
    },
    Chip {
        ma: "esp32h21",
        ten: "ESP32-H21",
        nhan: "1x RISC-V",
        xung: "đang công bố",
        radio: "BLE + 802.15.4",
        dac_diem: "Đang lấy mẫu, chưa có esp-hal",
        trang_thai: TrangThaiRust::ChuaCo,
        target: None,
        toolchain: "chưa rõ",
        bao_mat: "Dự kiến như ESP32-H2",
    },
    Chip {
        ma: "esp32h4",
        ten: "ESP32-H4",
        nhan: "1x RISC-V",
        xung: "đang công bố",
        radio: "BLE + 802.15.4",
        dac_diem: "Đang lấy mẫu, chưa có esp-hal",
        trang_thai: TrangThaiRust::ChuaCo,
        target: None,
        toolchain: "chưa rõ",
        bao_mat: "Dự kiến như ESP32-H2",
    },
    Chip {
        ma: "esp32p4",
        ten: "ESP32-P4",
        nhan: "2x RISC-V",
        xung: "400 MHz",
        radio: "KHÔNG radio (ghép chip radio đồng xử lý)",
        dac_diem: "Mạnh nhất: MIPI/LVDS, tăng tốc AI, HMI",
        trang_thai: TrangThaiRust::MoiThieu,
        target: Some("riscv32imafc-esp-espidf"),
        toolchain: "rustc chuẩn + target esp",
        bao_mat:
            "esp-hal thiếu HMAC/DS/KeyManager; silicon rev ≤v3.2 lỗi ECDSA ROM, phải dùng RSA-3072",
    },
    Chip {
        ma: "esp32e22",
        ten: "ESP32-E22",
        nhan: "radio đồng xử lý",
        xung: "chưa công bố",
        radio: "WiFi 6E",
        dac_diem: "Radio phụ ghép ESP32-P4, chưa có esp-hal",
        trang_thai: TrangThaiRust::ChuaCo,
        target: None,
        toolchain: "chưa rõ",
        bao_mat: "Chưa rõ",
    },
    Chip {
        ma: "esp8266",
        ten: "ESP8266 (ESP8285)",
        nhan: "1x Xtensa L106",
        xung: "160 MHz",
        radio: "WiFi 4",
        dac_diem: "Huyền thoại giá rẻ, KHÔNG được esp-rs hỗ trợ",
        trang_thai: TrangThaiRust::KhongCo,
        target: None,
        toolchain: "không có (dùng C SDK/Arduino, không phải esp-hal)",
        bao_mat: "Không có Secure Boot v2 / Flash Encryption chuẩn IDF mới",
    },
];

/// Chuẩn hóa mã chip: viết thường, bỏ gạch ngang/gạch dưới/khoảng trắng.
///
/// Ví dụ: `ESP32-S3` → `esp32s3`.
pub fn chuan_hoa_ma(ma: &str) -> String {
    ma.chars()
        .filter(|c| *c != '-' && *c != '_' && *c != ' ')
        .collect::<String>()
        .to_ascii_lowercase()
}

/// Tra cứu chip theo mã (chấp nhận `ESP32-S3`, `esp32s3`, bí danh `esp8684`...).
pub fn tim_chip(ma: &str) -> Option<&'static Chip> {
    let ma = chuan_hoa_ma(ma);
    // Bí danh tên module cũ.
    let ma = match ma.as_str() {
        "esp8684" | "esp8684h2" | "esp8684h4" => "esp32c2",
        "esp8285" => "esp8266",
        _ => ma.as_str(),
    };
    ALL_CHIPS.iter().find(|c| c.ma == ma)
}

/// Liệt kê mã của các chip build được bằng esp-hal hiện tại.
pub fn ma_build_duoc() -> Vec<&'static str> {
    ALL_CHIPS
        .iter()
        .filter(|c| c.build_duoc())
        .map(|c| c.ma)
        .collect()
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::collections::HashSet;

    // Tổng phải là 14 chip ESP32 + ESP8266 = 15 mục.
    #[test]
    fn du_15_muc() {
        assert_eq!(ALL_CHIPS.len(), 15, "thiếu chip trong ALL_CHIPS");
    }

    // Mã chip không được trùng nhau.
    #[test]
    fn ma_khong_trung() {
        let mut thay = HashSet::new();
        for chip in ALL_CHIPS {
            assert!(thay.insert(chip.ma), "mã trùng: {}", chip.ma);
        }
    }

    // Tra cứu S3: chip của khóa FIDO2.
    #[test]
    fn tim_thay_s3() {
        let chip = tim_chip("esp32s3").expect("phải tìm thấy S3");
        assert_eq!(chip.ten, "ESP32-S3");
        assert_eq!(chip.trang_thai, TrangThaiRust::DayDu);
        assert_eq!(chip.target, Some("xtensa-esp32s3-none-elf"));
        assert!(chip.can_espup());
    }

    // Tra cứu C6: chip RISC-V mẫu thứ hai.
    #[test]
    fn tim_thay_c6() {
        let chip = tim_chip("ESP32-C6").expect("phải tìm thấy C6");
        assert_eq!(chip.ma, "esp32c6");
        assert_eq!(chip.trang_thai, TrangThaiRust::DayDu);
        assert_eq!(chip.target, Some("riscv32imac-esp-espidf"));
        assert!(!chip.can_espup());
    }

    // ESP8266 phải bị đánh dấu không hỗ trợ.
    #[test]
    fn esp8266_khong_ho_tro() {
        let chip = tim_chip("esp8266").expect("phải có mục ESP8266");
        assert_eq!(chip.trang_thai, TrangThaiRust::KhongCo);
        assert_eq!(chip.target, None);
        assert!(!chip.build_duoc());
    }

    // Bí danh ESP8684 phải trỏ về ESP32-C2.
    #[test]
    fn bi_danh_esp8684() {
        let chip = tim_chip("ESP8684").expect("phải hiểu bí danh ESP8684");
        assert_eq!(chip.ma, "esp32c2");
    }

    // Mã lạ phải trả về None, không đoán bừa.
    #[test]
    fn ma_la_tra_none() {
        assert!(tim_chip("esp99").is_none());
        assert!(tim_chip("").is_none());
    }

    // P4 là trường hợp đặc biệt: có target nhưng thiếu ngoại vi bảo mật.
    #[test]
    fn p4_moi_thieu_va_can_rsa3072() {
        let chip = tim_chip("esp32p4").expect("phải có P4");
        assert_eq!(chip.trang_thai, TrangThaiRust::MoiThieu);
        assert!(chip.bao_mat.contains("RSA-3072"));
    }

    // Chip chưa có hỗ trợ thì không build được.
    #[test]
    fn chip_chua_co_khong_build_duoc() {
        for ma in ["esp32h21", "esp32h4", "esp32e22"] {
            let chip = tim_chip(ma).unwrap();
            assert_eq!(chip.trang_thai, TrangThaiRust::ChuaCo);
            assert!(!chip.build_duoc());
        }
    }
}
