//! CLI két mã hóa file, tương đương `tools/vault.py`.
//! Mã thoát: 0 ok, 1 lỗi chạy, 2 sai dùng.

use clap::{Parser, Subcommand};
use esk_vault::{decrypt_bytes, encrypt_bytes};
use std::fs;
use std::path::PathBuf;
use zeroize::Zeroize;

#[derive(Parser)]
#[command(name = "vault", about = "Két mã hóa file AES-256-GCM.")]
struct Cli {
    /// Tự kiểm nhanh, không cần file.
    #[arg(long = "self-test", short = 't')]
    self_test: bool,
    #[command(subcommand)]
    cmd: Option<Cmd>,
}

#[derive(Subcommand)]
enum Cmd {
    /// Mã hóa file thành két.
    Encrypt {
        #[arg(long = "in")]
        in_file: PathBuf,
        #[arg(long)]
        out: PathBuf,
        /// Đọc mật khẩu từ file thay vì gõ.
        #[arg(long)]
        password_file: Option<PathBuf>,
    },
    /// Mở két ra file.
    Decrypt {
        #[arg(long = "in")]
        in_file: PathBuf,
        #[arg(long)]
        out: PathBuf,
        /// Đọc mật khẩu từ file thay vì gõ.
        #[arg(long)]
        password_file: Option<PathBuf>,
    },
}

fn read_password(password_file: Option<&PathBuf>, confirm: bool) -> Result<Vec<u8>, String> {
    if let Some(path) = password_file {
        return fs::read(path).map_err(|e| format!("không đọc được file mật khẩu: {e}"));
    }
    let mut first = rpassword::prompt_password("Mật khẩu két: ")
        .map_err(|e| format!("không đọc được bàn phím: {e}"))?;
    if confirm {
        let mut second = rpassword::prompt_password("Nhập lại để xác nhận: ")
            .map_err(|e| format!("không đọc được bàn phím: {e}"))?;
        if first != second || first.is_empty() {
            first.zeroize();
            second.zeroize();
            return Err("Hai lần nhập không khớp hoặc rỗng.".to_string());
        }
        second.zeroize();
    }
    let pw = first.as_bytes().to_vec();
    first.zeroize();
    Ok(pw)
}

fn cmd_encrypt(in_file: PathBuf, out: PathBuf, password_file: Option<PathBuf>) -> i32 {
    let mut password = match read_password(password_file.as_ref(), true) {
        Ok(p) => p,
        Err(e) => {
            println!("{e}");
            return 1;
        }
    };
    let plain = match fs::read(&in_file) {
        Ok(p) => p,
        Err(e) => {
            println!("Không đọc được file vào: {e}");
            password.zeroize();
            return 1;
        }
    };
    let blob = encrypt_bytes(&plain, &password, &mut rand::rng());
    password.zeroize();
    if let Err(e) = fs::write(&out, blob) {
        println!("Không ghi được {}: {e}", out.display());
        return 1;
    }
    println!(
        "Đã mã hóa ra {}. Két này để ở đâu cũng được, kể cả cloud.",
        out.display()
    );
    0
}

fn cmd_decrypt(in_file: PathBuf, out: PathBuf, password_file: Option<PathBuf>) -> i32 {
    let mut password = match read_password(password_file.as_ref(), false) {
        Ok(p) => p,
        Err(e) => {
            println!("{e}");
            return 1;
        }
    };
    let blob = match fs::read(&in_file) {
        Ok(b) => b,
        Err(e) => {
            println!("Không đọc được két: {e}");
            password.zeroize();
            return 1;
        }
    };
    let plain = match decrypt_bytes(&blob, &password) {
        Ok(p) => p,
        Err(e) => {
            println!("Không mở được két: {e}");
            password.zeroize();
            return 1;
        }
    };
    password.zeroize();
    if let Err(e) = fs::write(&out, plain) {
        println!("Không ghi được {}: {e}", out.display());
        return 1;
    }
    println!(
        "Đã giải mã ra {}. Xóa file này sau khi dùng xong!",
        out.display()
    );
    0
}

fn self_test() -> i32 {
    let mut rng = rand::rng();
    let mut secret = vec![0u8; 200];
    use rand::RngCore;
    rng.fill_bytes(&mut secret);
    let mut password = vec![0u8; 32];
    rng.fill_bytes(&mut password);
    let blob = encrypt_bytes(&secret, &password, &mut rng);
    assert_eq!(decrypt_bytes(&blob, &password).unwrap(), secret);
    assert_ne!(encrypt_bytes(&secret, &password, &mut rng), blob);
    assert!(decrypt_bytes(&blob, b"sai").is_err());
    println!("self-test ok: mã hóa/giải mã đúng, sai mật khẩu và file sửa bị từ chối.");
    0
}

fn main() {
    let cli = Cli::parse();
    let code = if cli.self_test {
        self_test()
    } else {
        match cli.cmd {
            Some(Cmd::Encrypt {
                in_file,
                out,
                password_file,
            }) => cmd_encrypt(in_file, out, password_file),
            Some(Cmd::Decrypt {
                in_file,
                out,
                password_file,
            }) => cmd_decrypt(in_file, out, password_file),
            None => {
                println!("Sai dùng: thiếu lệnh con (encrypt, decrypt) hoặc --self-test.");
                2
            }
        }
    };
    std::process::exit(code);
}
