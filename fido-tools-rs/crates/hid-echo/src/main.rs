//! CLI kiểm tra echo HID, tương đương `tools/hid_echo.py`.
//! Mã thoát: 0 ok, 1 lỗi chạy, 2 sai dùng.

use clap::Parser;
use esk_hid_echo::{
    build_report, matches, verify_echo, Filter, ECHO_USAGE_PAGE, PAYLOAD_LEN, REPORT_LEN,
};
use rand::Rng;

#[derive(Parser)]
#[command(
    name = "hid-echo",
    about = "Kiểm tra echo HID của sketch hwtest (vendor page 0xFF00)."
)]
struct Cli {
    /// Tự kiểm đóng gói report, không cần phần cứng.
    #[arg(long = "self-test", short = 't')]
    self_test: bool,
    /// Lọc thêm usage (vá bắt nhầm thiết bị hệ thống).
    #[arg(long)]
    usage: Option<u16>,
    /// Lọc thêm VID (ví dụ 0x303A Espressif).
    #[arg(long)]
    vid: Option<u16>,
    /// Lọc thêm PID.
    #[arg(long)]
    pid: Option<u16>,
}

fn self_test() -> i32 {
    let report = build_report(b"abc").unwrap();
    assert_eq!(report.len(), REPORT_LEN + 1);
    assert_eq!(report[0], esk_hid_echo::REPORT_ID);
    assert!(build_report(&vec![0u8; REPORT_LEN + 1]).is_err());
    println!("self-test ok: đóng gói report HID echo đúng.");
    0
}

fn hex_u16(v: Option<u16>) -> String {
    match v {
        Some(x) => format!("0x{x:04X}"),
        None => "*".to_string(),
    }
}

fn main() {
    let cli = Cli::parse();
    let code = if cli.self_test {
        self_test()
    } else {
        run(&cli)
    };
    std::process::exit(code);
}

fn run(cli: &Cli) -> i32 {
    let api = match hidapi::HidApi::new() {
        Ok(a) => a,
        Err(e) => {
            println!("Không khởi tạo được HID: {e}");
            return 1;
        }
    };
    let filter = Filter {
        usage_page: ECHO_USAGE_PAGE,
        usage: cli.usage,
        vid: cli.vid,
        pid: cli.pid,
    };
    let mut target = None;
    for dev in api.device_list() {
        if matches(
            dev.usage_page(),
            dev.usage(),
            dev.vendor_id(),
            dev.product_id(),
            &filter,
        ) {
            target = Some(dev);
            break;
        }
    }
    let info = match target {
        Some(d) => d,
        None => {
            println!(
                "Không thấy HID echo (usage page 0xFF00, usage {}, VID {}, PID {}).",
                hex_u16(cli.usage),
                hex_u16(cli.vid),
                hex_u16(cli.pid)
            );
            println!("Kiểm tra: đã nạp hwtest ở USB Mode = USB-OTG, cắm cổng USB native.");
            return 1;
        }
    };
    let device = match info.open_device(&api) {
        Ok(d) => d,
        Err(e) => {
            println!("Không mở được thiết bị: {e}");
            return 1;
        }
    };
    let mut payload = vec![0u8; PAYLOAD_LEN];
    rand::rng().fill(&mut payload[..]);
    if let Err(e) = device.write(&build_report(&payload).unwrap()) {
        println!("Lỗi HID: {e}");
        return 1;
    }
    let mut buf = [0u8; REPORT_LEN + 1];
    let n = match device.read_timeout(&mut buf, 2000) {
        Ok(n) => n,
        Err(e) => {
            println!("Lỗi HID: {e}");
            return 1;
        }
    };
    if n == 0 {
        println!("Thiết bị không trả lời.");
        return 1;
    }
    match verify_echo(&payload, &buf[..n]) {
        Ok(()) => {
            println!("HID echo ok: 60 byte đi về khớp từng byte. Đường USB HID sống.");
            0
        }
        Err(e) => {
            println!("{e}");
            1
        }
    }
}
