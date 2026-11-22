//! CLI kiểm tra key FIDO, tương đương `tools/fido_check.py`.
//! Mã thoát: 0 ok, 1 lỗi chạy, 2 sai dùng.

use clap::Parser;
use esk_fido_check::{
    ctap2_get_info, fido_matches, parse_init_response, recv_msg, send_msg, InitResponse,
    CID_BROADCAST, CTAPHID_INIT, CTAPHID_PING, FIDO_USAGE_PAGE,
};
use rand::Rng;

#[derive(Parser)]
#[command(
    name = "fido-check",
    about = "Kiểm tra key FIDO qua USB HID: INIT, PING, CTAP2 GetInfo."
)]
struct Cli {
    /// Tự kiểm bằng key giả, không cần phần cứng.
    #[arg(long = "self-test", short = 't')]
    self_test: bool,
    /// Dùng key thứ N nếu có nhiều key.
    #[arg(long, default_value_t = 0)]
    index: usize,
    /// Lọc thêm VID.
    #[arg(long)]
    vid: Option<u16>,
    /// Lọc thêm PID.
    #[arg(long)]
    pid: Option<u16>,
}

fn self_test() -> i32 {
    // Framing gói đơn.
    let nonce: [u8; 8] = [0, 1, 2, 3, 4, 5, 6, 7];
    let init = esk_fido_check::build_init_packet(&nonce);
    assert_eq!(&init[0..4], b"\xff\xff\xff\xff");
    assert_eq!(init[4], CTAPHID_INIT | 0x80);
    assert!(esk_fido_check::build_ping_packet(1, &[0u8; 58]).is_err());
    // Cắt gói nối 100 byte.
    let data: Vec<u8> = (0..100u8).collect();
    let parts = esk_fido_check::fragment(0x01020304, CTAPHID_PING, &data).unwrap();
    assert_eq!(parts.len(), 2);
    // Bóc INIT mẫu.
    let mut sample: Vec<u8> = (0..8u8).collect();
    sample.extend_from_slice(&0xDEADBEEFu32.to_be_bytes());
    sample.extend_from_slice(&[2, 1, 0, 3, 0x05]);
    let parsed: InitResponse = parse_init_response(&sample).unwrap();
    assert_eq!(parsed.new_cid, 0xDEADBEEF);
    // CBOR GetInfo mẫu.
    let (info, rest) = esk_fido_check::cbor_decode(esk_fido_check::CANNED_GETINFO).unwrap();
    assert!(rest.is_empty() && matches!(info, esk_fido_check::Cbor::Map(_)));
    // Hội thoại đầu-cuối với key giả.
    for with_rid in [true, false] {
        let mut dev = esk_fido_check::FakeDevice::new(with_rid);
        send_msg(&mut dev, CID_BROADCAST, CTAPHID_INIT, &nonce).unwrap();
        let (_, cmd, data) = recv_msg(&mut dev, 2000).unwrap();
        assert_eq!(cmd, CTAPHID_INIT);
        let cid = parse_init_response(&data).unwrap().new_cid;
        let payload = b"esp32-s3-ping-test";
        send_msg(&mut dev, cid, CTAPHID_PING, payload).unwrap();
        let (_, cmd, echo) = recv_msg(&mut dev, 2000).unwrap();
        assert_eq!(cmd, CTAPHID_PING);
        assert_eq!(echo, payload);
        let info = ctap2_get_info(&mut dev, cid).unwrap();
        assert!(info.get("versions").is_some());
    }
    println!("self-test ok: framing, gói nối, CBOR, GetInfo và hội thoại đầu-cuối đều đúng.");
    0
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
    let found: Vec<_> = api
        .device_list()
        .filter(|d| {
            d.usage_page() == FIDO_USAGE_PAGE
                && fido_matches(
                    d.usage_page(),
                    d.vendor_id(),
                    d.product_id(),
                    cli.vid,
                    cli.pid,
                )
        })
        .collect();
    if found.is_empty() {
        println!("Không thấy thiết bị HID usage page 0xF1D0.");
        println!("Kiểm tra: cắm đúng cổng USB OTG native, cáp dữ liệu, udev rules trên Linux.");
        return 1;
    }
    if cli.index >= found.len() {
        println!(
            "Chỉ thấy {} key, không có key số {}.",
            found.len(),
            cli.index
        );
        return 2;
    }
    for (i, dev) in found.iter().enumerate() {
        let mark = if i == cli.index { ">>" } else { "  " };
        println!(
            "{mark} [{i}] {} {}",
            dev.manufacturer_string().unwrap_or("?"),
            dev.product_string().unwrap_or("?")
        );
    }
    let mut device = match found[cli.index].open_device(&api) {
        Ok(d) => d,
        Err(e) => {
            println!("Không mở được key: {e}");
            return 1;
        }
    };
    let mut nonce = [0u8; 8];
    rand::rng().fill(&mut nonce[..]);
    if send_msg(&mut device, CID_BROADCAST, CTAPHID_INIT, &nonce).is_err() {
        println!("Kiểm tra hỏng: không gửi được INIT.");
        return 1;
    }
    let (_cid0, cmd, data) = match recv_msg(&mut device, 2000) {
        Ok(t) => t,
        Err(e) => {
            println!("Kiểm tra hỏng: {e}");
            return 1;
        }
    };
    if cmd != CTAPHID_INIT {
        println!("INIT trả về lệnh lạ 0x{cmd:02x}.");
        return 1;
    }
    let ans = match parse_init_response(&data) {
        Ok(a) => a,
        Err(e) => {
            println!("Kiểm tra hỏng: {e}");
            return 1;
        }
    };
    if ans.nonce != nonce {
        println!("INIT sai nonce, key hoặc đường truyền có vấn đề.");
        return 1;
    }
    let cid = ans.new_cid;
    println!(
        "INIT ok. CID mới: 0x{cid:08x}, giao thức HID v{}.",
        ans.version
    );
    let payload = b"esp32-s3-ping-test";
    send_msg(&mut device, cid, CTAPHID_PING, payload).unwrap();
    match recv_msg(&mut device, 2000) {
        Ok((_, CTAPHID_PING, echo)) if echo == payload => println!("PING ngắn ok."),
        _ => {
            println!("PING ngắn không echo đúng.");
            return 1;
        }
    }
    let mut long = vec![0u8; 100];
    rand::rng().fill(&mut long[..]);
    send_msg(&mut device, cid, CTAPHID_PING, &long).unwrap();
    match recv_msg(&mut device, 2000) {
        Ok((_, CTAPHID_PING, echo)) if echo == long => {
            println!("PING dài ok. Đường gói nối tiếp hoạt động.")
        }
        _ => {
            println!("PING dài 100 byte (gói nối) không echo đúng.");
            return 1;
        }
    }
    match ctap2_get_info(&mut device, cid) {
        Ok(info) => println!(
            "CTAP2 GetInfo ok: versions={:?}, options={:?}, maxMsgSize={:?}.",
            info.get("versions"),
            info.get("options"),
            info.get("maxMsgSize")
        ),
        Err(e) => {
            println!("Kiểm tra hỏng: {e}");
            return 1;
        }
    }
    println!("Key trả lời đúng cả ba tầng: HID, PING nối gói và CTAP2.");
    0
}
