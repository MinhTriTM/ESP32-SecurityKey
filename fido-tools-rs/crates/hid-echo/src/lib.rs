//! Đóng gói report và lọc thiết bị cho HID echo của sketch hwtest.
//!
//! Tương thích giao thức với `tools/hid_echo.py` (vendor page 0xFF00,
//! report ID 1, report 64 byte, payload 60 byte), đồng thời vá 2 lỗi đã biết
//! (sổ NCKH-016): lọc thêm usage/VID/PID thay vì chỉ usage page, và trả lỗi
//! tường minh thay vì `assert` (assert biến mất dưới `python -O`).

use std::fmt;

pub const ECHO_USAGE_PAGE: u16 = 0xFF00;
pub const REPORT_ID: u8 = 1;
pub const REPORT_LEN: usize = 64;
pub const PAYLOAD_LEN: usize = 60;

#[derive(Debug, Clone, PartialEq, Eq)]
pub enum Error {
    /// Payload dài hơn 64 byte.
    TooLong(usize),
    /// Gói trả về dài lạ (không phải 64 hay 65 byte).
    BadLength(usize),
    /// Echo không khớp từng byte.
    Mismatch { sent: Vec<u8>, got: Vec<u8> },
}

impl fmt::Display for Error {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            Error::TooLong(n) => write!(f, "payload tối đa {REPORT_LEN} byte, nhận {n}"),
            Error::BadLength(n) => write!(f, "gói trả về dài lạ: {n} byte"),
            Error::Mismatch { got, .. } => {
                write!(
                    f,
                    "Echo sai: nhận {}",
                    hex_of(&got[..got.len().min(PAYLOAD_LEN)])
                )
            }
        }
    }
}

impl std::error::Error for Error {}

fn hex_of(data: &[u8]) -> String {
    data.iter().map(|b| format!("{b:02x}")).collect()
}

/// Report gửi đi: 1 byte report ID + 64 byte dữ liệu (đệm 0).
pub fn build_report(payload: &[u8]) -> Result<Vec<u8>, Error> {
    if payload.len() > REPORT_LEN {
        return Err(Error::TooLong(payload.len()));
    }
    let mut report = Vec::with_capacity(REPORT_LEN + 1);
    report.push(REPORT_ID);
    report.extend_from_slice(payload);
    report.resize(REPORT_LEN + 1, 0);
    Ok(report)
}

/// Điều kiện chọn thiết bị. Mặc định chỉ lọc usage page như bản Python;
/// thêm usage/VID/PID khi máy có nhiều thiết bị lạ cùng usage page.
#[derive(Debug, Clone, Copy)]
pub struct Filter {
    pub usage_page: u16,
    pub usage: Option<u16>,
    pub vid: Option<u16>,
    pub pid: Option<u16>,
}

impl Default for Filter {
    fn default() -> Self {
        Filter {
            usage_page: ECHO_USAGE_PAGE,
            usage: None,
            vid: None,
            pid: None,
        }
    }
}

/// Thiết bị HID có khớp bộ lọc không. Tách riêng để test không cần phần cứng.
pub fn matches(usage_page: u16, usage: u16, vid: u16, pid: u16, filter: &Filter) -> bool {
    usage_page == filter.usage_page
        && filter.usage.map_or(true, |u| u == usage)
        && filter.vid.map_or(true, |v| v == vid)
        && filter.pid.map_or(true, |p| p == pid)
}

/// Bóc report ID khỏi gói trả về (nền tảng trả 65 byte, có nền tảng 64 byte).
pub fn strip_report_id(echo: &[u8]) -> Result<&[u8], Error> {
    if echo.len() == REPORT_LEN + 1 {
        Ok(&echo[1..])
    } else if echo.len() == REPORT_LEN {
        Ok(echo)
    } else {
        Err(Error::BadLength(echo.len()))
    }
}

/// Đối chiếu từng byte echo với payload đã gửi.
pub fn verify_echo(sent: &[u8], echo: &[u8]) -> Result<(), Error> {
    let body = strip_report_id(echo)?;
    if body.len() < sent.len() || &body[..sent.len()] != sent {
        return Err(Error::Mismatch {
            sent: sent.to_vec(),
            got: body.to_vec(),
        });
    }
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn dong_goi_report_dung() {
        let report = build_report(b"abc").unwrap();
        assert_eq!(report.len(), REPORT_LEN + 1);
        assert_eq!(report[0], REPORT_ID);
        assert_eq!(&report[1..4], b"abc");
        assert_eq!(&report[4..], &vec![0u8; 61][..]);
        assert_eq!(
            build_report(&vec![0u8; REPORT_LEN + 1]),
            Err(Error::TooLong(REPORT_LEN + 1))
        );
    }

    #[test]
    fn loc_thiet_bi_dung() {
        let any = Filter::default();
        assert!(matches(0xFF00, 0x01, 0x303A, 0x1001, &any));
        assert!(!matches(0x0001, 0x01, 0x303A, 0x1001, &any));
        // Vá NCKH-016: máy test có HIDI2C và Alienware AW-ELC cùng usage page
        // 0xFF00 nên phải lọc thêm mới khỏi gửi nhầm 65 byte vào driver hệ thống.
        let strict = Filter {
            usage_page: 0xFF00,
            usage: Some(0x01),
            vid: Some(0x303A),
            pid: None,
        };
        assert!(matches(0xFF00, 0x01, 0x303A, 0x1001, &strict));
        assert!(!matches(0xFF00, 0x02, 0x303A, 0x1001, &strict));
        assert!(!matches(0xFF00, 0x01, 0x046D, 0x1001, &strict));
    }

    #[test]
    fn doi_chieu_echo_dung() {
        let sent = vec![7u8; PAYLOAD_LEN];
        let mut echo = vec![REPORT_ID];
        echo.extend_from_slice(&sent);
        echo.resize(REPORT_LEN + 1, 0);
        verify_echo(&sent, &echo).unwrap();
        verify_echo(&sent, &echo[1..]).unwrap(); // kiểu không report ID
        let mut bad = echo.clone();
        bad[10] ^= 1;
        assert!(verify_echo(&sent, &bad).is_err());
        assert_eq!(strip_report_id(&[0u8; 10]), Err(Error::BadLength(10)));
    }
}
