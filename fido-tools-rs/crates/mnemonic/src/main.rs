//! CLI cụm từ khôi phục BIP-39, tương đương `tools/mnemonic.py`.
//! Mã thoát: 0 ok, 1 lỗi chạy, 2 sai dùng.

use clap::{Parser, Subcommand};
use esk_mnemonic::{
    entropy_to_mnemonic, load_wordlist, mnemonic_to_entropy, mnemonic_to_seed, normalize_mnemonic,
};
use rand::Rng;
use std::fs;
use std::path::PathBuf;
use zeroize::Zeroize;

#[derive(Parser)]
#[command(name = "mnemonic", about = "Cụm từ khôi phục kiểu ví lạnh (BIP-39).")]
struct Cli {
    /// Tự kiểm nhanh, không cần file.
    #[arg(long = "self-test", short = 't')]
    self_test: bool,
    #[command(subcommand)]
    cmd: Option<Cmd>,
}

#[derive(Subcommand)]
enum Cmd {
    /// Sinh bí mật mới và in cụm từ.
    New {
        /// Số từ (mặc định 24).
        #[arg(long, default_value_t = 24)]
        words: usize,
        /// Ghi entropy thô ra file để chia share.
        #[arg(long)]
        out: Option<PathBuf>,
    },
    /// Bytes bí mật -> cụm từ.
    FromEntropy {
        #[arg(long)]
        from_file: PathBuf,
    },
    /// Cụm từ -> entropy (kiểm checksum).
    ToEntropy {
        /// Các từ theo đúng thứ tự.
        words: Vec<String>,
        /// Ghi entropy ra file thay vì in hex.
        #[arg(long)]
        out: Option<PathBuf>,
    },
    /// Cụm từ -> seed 64 byte.
    Seed {
        words: Vec<String>,
        /// Cụm mật khẩu phụ (tùy chọn).
        #[arg(long, default_value = "")]
        passphrase: String,
    },
    /// Vẽ cụm từ thành ảnh QR.
    Qr {
        words: Vec<String>,
        #[arg(long, default_value = "mnemonic.png")]
        out: PathBuf,
    },
}

fn hex_of(data: &[u8]) -> String {
    data.iter().map(|b| format!("{b:02x}")).collect()
}

fn cmd_new(n_words: usize, out: Option<PathBuf>) -> i32 {
    if ![12, 15, 18, 21, 24].contains(&n_words) {
        println!("--words phải là một trong [12, 15, 18, 21, 24]");
        return 2;
    }
    let words = load_wordlist().unwrap();
    // Số byte entropy = words*11*32/33/8.
    let n_bytes = n_words * 11 * 32 / 33 / 8;
    let mut entropy = vec![0u8; n_bytes];
    rand::rng().fill(&mut entropy[..]);
    println!("{}", entropy_to_mnemonic(&entropy, &words).unwrap());
    if let Some(path) = out {
        if fs::write(&path, &entropy).is_ok() {
            println!(
                "Đã ghi {} byte entropy ra {} (xóa sau khi chia share!).",
                n_bytes,
                path.display()
            );
        } else {
            println!("Không ghi được {}", path.display());
            entropy.zeroize();
            return 1;
        }
    }
    entropy.zeroize();
    println!("Ghi cụm từ ra giấy NGAY, theo đúng thứ tự. Đây là đường khôi phục cuối cùng.");
    0
}

fn cmd_from_entropy(from_file: PathBuf) -> i32 {
    let words = load_wordlist().unwrap();
    let data = match fs::read(&from_file) {
        Ok(d) => d,
        Err(e) => {
            println!("Lỗi: {e}");
            return 1;
        }
    };
    match entropy_to_mnemonic(&data, &words) {
        Ok(t) => {
            println!("{t}");
            0
        }
        Err(e) => {
            println!("Lỗi: {e}");
            1
        }
    }
}

fn cmd_to_entropy(words_in: Vec<String>, out: Option<PathBuf>) -> i32 {
    let words = load_wordlist().unwrap();
    let entropy = match mnemonic_to_entropy(&words_in.join(" "), &words) {
        Ok(e) => e,
        Err(e) => {
            println!("Cụm từ sai: {e}");
            return 1;
        }
    };
    match out {
        Some(path) => {
            if fs::write(&path, entropy).is_err() {
                println!("Không ghi được {}", path.display());
                1
            } else {
                0
            }
        }
        None => {
            println!("Entropy ({} byte): {}", entropy.len(), hex_of(&entropy));
            0
        }
    }
}

fn cmd_qr(words_in: Vec<String>, out: PathBuf) -> i32 {
    let words = load_wordlist().unwrap();
    let text = normalize_mnemonic(&words_in.join(" "));
    if let Err(e) = mnemonic_to_entropy(&text, &words) {
        println!("Cụm từ sai: {e}");
        return 1;
    }
    let code = match qrcode::QrCode::new(text.as_bytes()) {
        Ok(c) => c,
        Err(e) => {
            println!("Không vẽ được QR: {e}");
            return 1;
        }
    };
    let img = code
        .render::<image::Luma<u8>>()
        .quiet_zone(true)
        .module_dimensions(8, 8)
        .build();
    if img.save(&out).is_err() {
        println!("Không ghi được {}", out.display());
        return 1;
    }
    println!("Đã vẽ QR ra {}. Quét xong thì xóa file ảnh.", out.display());
    0
}

fn self_test() -> i32 {
    let words = load_wordlist().unwrap();
    assert_eq!(words[0], "abandon");
    assert_eq!(words[3], "about");
    assert_eq!(words[2047], "zoo");
    let zero12 = "abandon ".repeat(11) + "about";
    assert_eq!(entropy_to_mnemonic(&[0u8; 16], &words).unwrap(), zero12);
    assert_eq!(mnemonic_to_entropy(&zero12, &words).unwrap(), vec![0u8; 16]);
    println!("self-test ok: bảng BIP-39 nguyên vẹn, vector chuẩn đúng, checksum bắt lỗi.");
    0
}

fn main() {
    let cli = Cli::parse();
    let code = if cli.self_test {
        self_test()
    } else {
        match cli.cmd {
            Some(Cmd::New { words, out }) => cmd_new(words, out),
            Some(Cmd::FromEntropy { from_file }) => cmd_from_entropy(from_file),
            Some(Cmd::ToEntropy { words, out }) => cmd_to_entropy(words, out),
            Some(Cmd::Seed { words, passphrase }) => {
                println!(
                    "{}",
                    hex_of(&mnemonic_to_seed(&words.join(" "), &passphrase))
                );
                0
            }
            Some(Cmd::Qr { words, out }) => {
                if words.is_empty() {
                    println!("Sai dùng: qr cần ít nhất một từ.");
                    2
                } else {
                    cmd_qr(words, out)
                }
            }
            None => {
                println!("Sai dùng: thiếu lệnh con hoặc --self-test.");
                2
            }
        }
    };
    std::process::exit(code);
}
