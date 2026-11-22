//! CLI chia/ghép Shamir, tương đương `tools/split_secret.py`.
//! Mã thoát theo bảng chuẩn NCKH-052: 0 ok, 1 lỗi chạy, 2 sai dùng.

use clap::{Parser, Subcommand};
use esk_shamir::{combine, format_share, gf_self_check, parse_share, split};
use rand::Rng;
use std::fs;
use std::path::PathBuf;
use zeroize::Zeroize;

#[derive(Parser)]
#[command(name = "split-secret", about = "Chia/ghép bí mật Shamir K-trên-N.")]
struct Cli {
    /// Tự kiểm nhanh, không cần file.
    #[arg(long = "self-test", short = 't')]
    self_test: bool,
    #[command(subcommand)]
    cmd: Option<Cmd>,
}

#[derive(Subcommand)]
enum Cmd {
    /// Chia bí mật thành N share.
    Split {
        /// Số share N (tối đa 255).
        #[arg(long)]
        shares: u16,
        /// Số share tối thiểu K để ghép.
        #[arg(long)]
        threshold: u16,
        /// Đọc bí mật từ file thay vì gõ.
        #[arg(long)]
        from_file: Option<PathBuf>,
        /// Thư mục ghi các file share.
        #[arg(long)]
        out: PathBuf,
    },
    /// Ghép các share thành bí mật.
    Combine {
        /// File share (ít nhất K file).
        shares: Vec<PathBuf>,
        /// Ghi bí mật ra file thay vì in màn hình.
        #[arg(long)]
        out: Option<PathBuf>,
    },
    /// Vẽ file share thành ảnh QR để quét sang điện thoại.
    Qr {
        /// File share cần vẽ.
        share: PathBuf,
        /// File ảnh PNG (mặc định cùng tên, đuôi .png).
        #[arg(long)]
        out: Option<PathBuf>,
    },
}

/// Đọc bí mật: từ file hoặc gõ 2 lần xác nhận. Xóa sạch bộ nhớ sau khi dùng.
fn read_secret(from_file: Option<&PathBuf>) -> Result<Vec<u8>, String> {
    if let Some(path) = from_file {
        return fs::read(path).map_err(|e| format!("không đọc được file bí mật: {e}"));
    }
    let mut first = rpassword::prompt_password("Nhập bí mật cần chia: ")
        .map_err(|e| format!("không đọc được bàn phím: {e}"))?;
    let mut second = rpassword::prompt_password("Nhập lại để xác nhận: ")
        .map_err(|e| format!("không đọc được bàn phím: {e}"))?;
    if first != second || first.is_empty() {
        first.zeroize();
        second.zeroize();
        return Err("Hai lần nhập không khớp hoặc rỗng.".to_string());
    }
    let secret = first.as_bytes().to_vec();
    first.zeroize();
    second.zeroize();
    Ok(secret)
}

fn cmd_split(shares_n: u16, threshold: u16, from_file: Option<PathBuf>, out: PathBuf) -> i32 {
    let mut secret = match read_secret(from_file.as_ref()) {
        Ok(s) => s,
        Err(e) => {
            println!("{e}");
            return 1;
        }
    };
    if threshold < 1 || threshold > shares_n || shares_n < 1 || shares_n > 255 {
        println!(
            "Sai tham số: cần 1 <= threshold <= shares <= 255, nhận k={threshold} n={shares_n}"
        );
        secret.zeroize();
        return 2;
    }
    let mut rng = rand::rng();
    let shares = match split(&secret, shares_n as u8, threshold as u8, &mut rng) {
        Ok(s) => s,
        Err(e) => {
            println!("Sai tham số: {e}");
            secret.zeroize();
            return 2;
        }
    };
    secret.zeroize();
    if let Err(e) = fs::create_dir_all(&out) {
        println!("Không tạo được thư mục ra: {e}");
        return 1;
    }
    for (x, y) in &shares {
        let path = out.join(format!("share-{x}-of-{shares_n}.txt"));
        if let Err(e) = fs::write(&path, format_share(shares_n as u8, threshold as u8, *x, y)) {
            println!("Không ghi được {}: {e}", path.display());
            return 1;
        }
        println!("Đã ghi {}", path.display());
    }
    println!("Xong: {shares_n} share, cần {threshold} share để ghép.");
    println!("Chép mỗi file sang một USB khác nhau, cất ở nơi khác nhau.");
    0
}

fn cmd_combine(files: Vec<PathBuf>, out: Option<PathBuf>) -> i32 {
    let mut parsed = Vec::new();
    for name in &files {
        let text = match fs::read_to_string(name) {
            Ok(t) => t,
            Err(e) => {
                println!("File {} lỗi: {e}", name.display());
                return 1;
            }
        };
        match parse_share(&text) {
            Ok(s) => parsed.push(s),
            Err(e) => {
                println!("File {} lỗi: {e}", name.display());
                return 1;
            }
        }
    }
    let head = (parsed[0].n, parsed[0].k, parsed[0].y.len());
    if parsed.iter().any(|s| (s.n, s.k, s.y.len()) != head) {
        println!("Các share không cùng một lần chia (shares/threshold/len khác nhau).");
        return 1;
    }
    let (n, k, _) = head;
    if parsed.len() < k as usize {
        println!(
            "Thiếu share: cần ít nhất {k} trong {n}, mới đưa {}.",
            parsed.len()
        );
        return 2;
    }
    let inputs: Vec<(u8, Vec<u8>)> = parsed.into_iter().map(|s| (s.x, s.y)).collect();
    let mut secret = match combine(&inputs) {
        Ok(s) => s,
        Err(e) => {
            println!("Không ghép được: {e}");
            return 1;
        }
    };
    let code = match out {
        Some(path) => match fs::write(&path, &secret) {
            Ok(()) => {
                println!("Đã ghi bí mật ra {}", path.display());
                0
            }
            Err(e) => {
                println!("Không ghi được {}: {e}", path.display());
                1
            }
        },
        None => {
            match String::from_utf8(secret.clone()) {
                Ok(s) => println!("Bí mật: {s}"),
                Err(_) => println!("Bí mật (hex): {}", hex_of(&secret)),
            }
            0
        }
    };
    secret.zeroize();
    code
}

fn hex_of(data: &[u8]) -> String {
    data.iter().map(|b| format!("{b:02x}")).collect()
}

/// Vẽ text thành QR PNG: khung trắng 4 module, mỗi module 8 px.
fn cmd_qr(share: PathBuf, out: Option<PathBuf>) -> i32 {
    let text = match fs::read_to_string(&share) {
        Ok(t) => t,
        Err(e) => {
            println!("File {} lỗi: {e}", share.display());
            return 1;
        }
    };
    if let Err(e) = parse_share(&text) {
        println!("File {} lỗi: {e}", share.display());
        return 1;
    }
    let code = match qrcode::QrCode::new(text.trim().as_bytes()) {
        Ok(c) => c,
        Err(e) => {
            println!("Không vẽ được QR: {e}");
            return 1;
        }
    };
    let out_path = out.unwrap_or_else(|| share.with_extension("png"));
    let img = code
        .render::<image::Luma<u8>>()
        .quiet_zone(true)
        .module_dimensions(8, 8)
        .build();
    if let Err(e) = img.save(&out_path) {
        println!("Không ghi được {}: {e}", out_path.display());
        return 1;
    }
    println!(
        "Đã vẽ QR ra {}. Quét xong thì xóa file ảnh.",
        out_path.display()
    );
    0
}

/// Self-test: vector AES + round-trip mọi ngưỡng + từ chối file hỏng.
fn self_test() -> i32 {
    gf_self_check();
    let mut rng = rand::rng();
    for (n, k) in [(3u8, 2u8), (5, 3), (5, 5), (8, 2)] {
        let secret: Vec<u8> = (0..16).map(|_| rng.random()).collect();
        let shares = split(&secret, n, k, &mut rng).unwrap();
        assert_eq!(combine(&shares).unwrap(), secret);
        assert_ne!(combine(&shares[..1]).unwrap(), secret);
    }
    assert!(parse_share("rác").is_err());
    println!("self-test ok: GF(256) đúng vector AES, chia/ghép đúng mọi ngưỡng thử.");
    0
}

fn main() {
    let cli = Cli::parse();
    let code = if cli.self_test {
        self_test()
    } else {
        match cli.cmd {
            Some(Cmd::Split {
                shares,
                threshold,
                from_file,
                out,
            }) => cmd_split(shares, threshold, from_file, out),
            Some(Cmd::Combine { shares, out }) => {
                if shares.is_empty() {
                    println!("Sai dùng: combine cần ít nhất một file share.");
                    2
                } else {
                    cmd_combine(shares, out)
                }
            }
            Some(Cmd::Qr { share, out }) => cmd_qr(share, out),
            None => {
                println!("Sai dùng: thiếu lệnh con (split, combine, qr) hoặc --self-test.");
                2
            }
        }
    };
    std::process::exit(code);
}
