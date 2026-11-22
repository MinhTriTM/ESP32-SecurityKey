//! Cụm từ khôi phục chuẩn BIP-39, tương thích với `tools/mnemonic.py`.
//!
//! Bảng 2048 từ tiếng Anh nhúng thẳng vào binary để chạy độc lập một file.
//! Nguồn bảng: `tools/bip39_english.txt` (bảng BIP-39 chính thức).

use sha2::{Digest, Sha256, Sha512};
use std::fmt;
use unicode_normalization::UnicodeNormalization;

const WORDLIST_TEXT: &str = include_str!("../wordlist/bip39_english.txt");

#[derive(Debug, Clone, PartialEq, Eq)]
pub enum Error {
    /// Bảng từ nhúng sai (phải đúng 2048 từ).
    BadWordlistLen(usize),
    /// Entropy không dài 128/160/192/224/256 bit.
    BadEntropyBits(usize),
    /// Số từ không thuộc 12/15/18/21/24.
    BadWordCount(usize),
    /// Từ lạ không có trong bảng BIP-39.
    UnknownWord(String),
    /// Sai checksum: gõ nhầm từ hoặc sai thứ tự.
    BadChecksum,
}

impl fmt::Display for Error {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            Error::BadWordlistLen(n) => write!(f, "bảng từ phải có 2048 từ, thấy {n}"),
            Error::BadEntropyBits(n) => {
                write!(
                    f,
                    "entropy phải dài [128, 160, 192, 224, 256] bit, nhận {n}"
                )
            }
            Error::BadWordCount(n) => write!(f, "số từ phải là [12, 15, 18, 21, 24], nhận {n}"),
            Error::UnknownWord(w) => write!(f, "từ lạ không có trong bảng BIP-39: {w}"),
            Error::BadChecksum => write!(f, "sai checksum: gõ nhầm từ hoặc sai thứ tự"),
        }
    }
}

impl std::error::Error for Error {}

/// Tải bảng từ nhúng sẵn, kiểm tra đủ 2048 từ.
pub fn load_wordlist() -> Result<Vec<&'static str>, Error> {
    let words: Vec<&str> = WORDLIST_TEXT.split_whitespace().collect();
    if words.len() != 2048 {
        return Err(Error::BadWordlistLen(words.len()));
    }
    Ok(words)
}

/// Chuẩn hóa như BIP-39: NFKD, chữ thường, một khoảng trắng.
pub fn normalize_mnemonic(text: &str) -> String {
    text.nfkd()
        .collect::<String>()
        .to_lowercase()
        .split_whitespace()
        .collect::<Vec<_>>()
        .join(" ")
}

fn valid_entropy_bits(ent: usize) -> bool {
    matches!(ent, 128 | 160 | 192 | 224 | 256)
}

/// Bytes bí mật -> chuỗi từ. Độ dài entropy phải là 16/20/24/28/32 byte.
pub fn entropy_to_mnemonic(entropy: &[u8], words: &[&str]) -> Result<String, Error> {
    let ent = entropy.len() * 8;
    if !valid_entropy_bits(ent) {
        return Err(Error::BadEntropyBits(ent));
    }
    let hash = Sha256::digest(entropy);
    let mut bits: Vec<u8> = Vec::with_capacity(ent + ent / 32);
    for b in entropy {
        for i in (0..8).rev() {
            bits.push((b >> i) & 1);
        }
    }
    for i in 0..ent / 32 {
        bits.push((hash[i / 8] >> (7 - i % 8)) & 1);
    }
    let out: Vec<&str> = bits
        .chunks_exact(11)
        .map(|c| {
            let mut idx = 0usize;
            for &b in c {
                idx = (idx << 1) | b as usize;
            }
            words[idx]
        })
        .collect();
    Ok(out.join(" "))
}

/// Chuỗi từ -> bytes bí mật. Ném lỗi nếu sai từ hoặc sai checksum.
pub fn mnemonic_to_entropy(text: &str, words: &[&str]) -> Result<Vec<u8>, Error> {
    let norm = normalize_mnemonic(text);
    let cleaned: Vec<&str> = norm.split(' ').collect();
    let total = cleaned.len() * 11;
    let ent = total * 32 / 33;
    if !valid_entropy_bits(ent) || ent * 33 / 32 != total {
        return Err(Error::BadWordCount(cleaned.len()));
    }
    let mut bits: Vec<u8> = Vec::with_capacity(total);
    for w in &cleaned {
        match words.iter().position(|x| x == w) {
            Some(i) => {
                for k in (0..11).rev() {
                    bits.push(((i >> k) & 1) as u8);
                }
            }
            None => return Err(Error::UnknownWord(w.to_string())),
        }
    }
    let entropy: Vec<u8> = bits[..ent]
        .chunks_exact(8)
        .map(|c| c.iter().fold(0u8, |a, &b| (a << 1) | b))
        .collect();
    let hash = Sha256::digest(&entropy);
    for i in 0..ent / 32 {
        if bits[ent + i] != (hash[i / 8] >> (7 - i % 8)) & 1 {
            return Err(Error::BadChecksum);
        }
    }
    Ok(entropy)
}

/// Seed 64 byte theo BIP-39: PBKDF2-HMAC-SHA512, 2048 vòng.
pub fn mnemonic_to_seed(text: &str, passphrase: &str) -> [u8; 64] {
    let norm = normalize_mnemonic(text);
    let password: String = norm.as_str().nfkd().collect();
    let raw_salt = format!("mnemonic{passphrase}");
    let salt: String = raw_salt.as_str().nfkd().collect();
    let mut seed = [0u8; 64];
    pbkdf2::pbkdf2_hmac::<Sha512>(password.as_bytes(), salt.as_bytes(), 2048, &mut seed);
    seed
}

#[cfg(test)]
mod tests {
    use super::*;
    use rand::{Rng, SeedableRng};

    #[test]
    fn bang_tu_nguyen_ven() {
        let words = load_wordlist().unwrap();
        assert_eq!(words[0], "abandon");
        assert_eq!(words[3], "about");
        assert_eq!(words[2047], "zoo");
        let uniq: std::collections::HashSet<&&str> = words.iter().collect();
        assert_eq!(uniq.len(), 2048, "bảng từ trùng từ");
        let pref: std::collections::HashSet<String> =
            words.iter().map(|w| w.chars().take(4).collect()).collect();
        assert_eq!(pref.len(), 2048, "tiền tố 4 chữ không phân biệt");
    }

    #[test]
    fn vector_chuan_bip39() {
        let words = load_wordlist().unwrap();
        let zero12 = "abandon ".repeat(11) + "about";
        assert_eq!(entropy_to_mnemonic(&[0u8; 16], &words).unwrap(), zero12);
        assert_eq!(mnemonic_to_entropy(&zero12, &words).unwrap(), vec![0u8; 16]);
    }

    #[test]
    fn roundtrip_moi_do_dai() {
        let words = load_wordlist().unwrap();
        let mut rng = rand::rngs::StdRng::seed_from_u64(42);
        for (ent_bytes, n_words) in [(16, 12), (20, 15), (24, 18), (28, 21), (32, 24)] {
            let entropy: Vec<u8> = (0..ent_bytes).map(|_| rng.random()).collect();
            let text = entropy_to_mnemonic(&entropy, &words).unwrap();
            assert_eq!(text.split(' ').count(), n_words);
            assert_eq!(mnemonic_to_entropy(&text, &words).unwrap(), entropy);
        }
    }

    #[test]
    fn cum_tu_hong_bi_tu_choi() {
        let words = load_wordlist().unwrap();
        assert_eq!(
            mnemonic_to_entropy(&"abandon ".repeat(12), &words),
            Err(Error::BadChecksum)
        );
        assert!(mnemonic_to_entropy(
            &("abandon từ-lạ ".to_string() + &"abandon ".repeat(10)),
            &words
        )
        .is_err());
        assert_eq!(
            mnemonic_to_entropy("abandon abandon", &words),
            Err(Error::BadWordCount(2))
        );
    }

    #[test]
    fn seed_on_dinh_va_nhay_passphrase() {
        let zero12 = "abandon ".repeat(11) + "about";
        let s1 = mnemonic_to_seed(&zero12, "TREZOR");
        assert_eq!(s1, mnemonic_to_seed(&zero12, "TREZOR"));
        assert_ne!(mnemonic_to_seed(&zero12, ""), s1);
    }

    #[test]
    fn chuan_hoa_chu_hoa_va_khoang_trang() {
        let words = load_wordlist().unwrap();
        let messy = "  ABANDON  abandon\nAbandon\t".to_string() + &"abandon ".repeat(8) + "about  ";
        assert_eq!(mnemonic_to_entropy(&messy, &words).unwrap(), vec![0u8; 16]);
    }
}
