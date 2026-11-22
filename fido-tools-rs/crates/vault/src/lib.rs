//! Két mã hóa file: AES-256-GCM, khóa suy từ mật khẩu bằng PBKDF2.
//!
//! Định dạng byte tương thích hoàn toàn với `tools/vault.py`:
//! `MAGIC(9) + salt(16) + nonce(12) + ciphertext+tag`.
//! Khóa được xóa sạch khỏi RAM sau khi dùng.

use aes_gcm::{aead::Aead, Aes256Gcm, Key, KeyInit, Nonce};
use rand::RngCore;
use std::fmt;
use zeroize::Zeroize;

pub const MAGIC: &[u8; 9] = b"ESKVAULT1";
pub const SALT_LEN: usize = 16;
pub const NONCE_LEN: usize = 12;
/// Số vòng PBKDF2-SHA256, giữ đúng bản Python (đừng giảm để test nhanh).
pub const PBKDF2_ROUNDS: u32 = 600_000;

#[derive(Debug, Clone, PartialEq, Eq)]
pub enum Error {
    /// File không phải két của tool này (sai magic hoặc quá ngắn).
    BadMagic,
    /// Sai mật khẩu hoặc file bị sửa đổi (GCM xác thực hỏng).
    WrongPasswordOrTampered,
}

impl fmt::Display for Error {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            Error::BadMagic => write!(f, "file không phải két của tool này (sai magic)"),
            Error::WrongPasswordOrTampered => write!(f, "sai mật khẩu hoặc file bị sửa đổi"),
        }
    }
}

impl std::error::Error for Error {}

/// Suy khóa AES-256 từ mật khẩu. Salt phải ngẫu nhiên mỗi lần mã hóa.
pub fn derive_key(password: &[u8], salt: &[u8; SALT_LEN]) -> [u8; 32] {
    let mut key = [0u8; 32];
    pbkdf2::pbkdf2_hmac::<sha2::Sha256>(password, salt, PBKDF2_ROUNDS, &mut key);
    key
}

/// Mã hóa bản rõ thành blob két. `rng` phải là CSPRNG (ví dụ ThreadRng).
pub fn encrypt_bytes<R: RngCore + rand::CryptoRng>(
    plain: &[u8],
    password: &[u8],
    rng: &mut R,
) -> Vec<u8> {
    let mut salt = [0u8; SALT_LEN];
    let mut nonce = [0u8; NONCE_LEN];
    rng.fill_bytes(&mut salt);
    rng.fill_bytes(&mut nonce);
    let mut key = derive_key(password, &salt);
    let cipher = Aes256Gcm::new(Key::<Aes256Gcm>::from_slice(&key));
    key.zeroize();
    let body = cipher
        .encrypt(Nonce::from_slice(&nonce), plain)
        .expect("AES-GCM mã hóa không bao giờ hỏng với input hợp lệ");
    let mut blob = Vec::with_capacity(MAGIC.len() + SALT_LEN + NONCE_LEN + body.len());
    blob.extend_from_slice(MAGIC);
    blob.extend_from_slice(&salt);
    blob.extend_from_slice(&nonce);
    blob.extend_from_slice(&body);
    blob
}

/// Mở két. Mọi lỗi giải mã đều gộp thành một biến thể để khỏi rò kênh kề.
pub fn decrypt_bytes(blob: &[u8], password: &[u8]) -> Result<Vec<u8>, Error> {
    let head = MAGIC.len() + SALT_LEN + NONCE_LEN;
    if blob.len() < head || &blob[..MAGIC.len()] != MAGIC {
        return Err(Error::BadMagic);
    }
    let mut salt = [0u8; SALT_LEN];
    salt.copy_from_slice(&blob[MAGIC.len()..MAGIC.len() + SALT_LEN]);
    let mut nonce = [0u8; NONCE_LEN];
    nonce.copy_from_slice(&blob[MAGIC.len() + SALT_LEN..head]);
    let mut key = derive_key(password, &salt);
    let cipher = Aes256Gcm::new(Key::<Aes256Gcm>::from_slice(&key));
    key.zeroize();
    cipher
        .decrypt(Nonce::from_slice(&nonce), &blob[head..])
        .map_err(|_| Error::WrongPasswordOrTampered)
}

#[cfg(test)]
mod tests {
    use super::*;

    /// Một test duy nhất để chỉ tốn vài lần PBKDF2 600k vòng.
    #[test]
    fn ket_dung_sai_bi_tu_choi() {
        let mut rng = rand::rng();
        let mut plain = vec![0u8; 200];
        rng.fill_bytes(&mut plain);
        let mut password = vec![0u8; 32];
        rng.fill_bytes(&mut password);
        let blob = encrypt_bytes(&plain, &password, &mut rng);
        assert_eq!(&blob[..MAGIC.len()], MAGIC);
        assert_eq!(decrypt_bytes(&blob, &password).unwrap(), plain);
        // Hai lần mã hóa cùng đầu vào phải ra khác nhau (salt/nonce ngẫu nhiên).
        assert_ne!(encrypt_bytes(&plain, &password, &mut rng), blob);
        // Sai mật khẩu và file sửa 1 bit đều bị từ chối.
        assert_eq!(
            decrypt_bytes(&blob, b"sai"),
            Err(Error::WrongPasswordOrTampered)
        );
        let mut cut = blob.clone();
        let last = cut.len() - 1;
        cut[last] ^= 1;
        assert_eq!(
            decrypt_bytes(&cut, &password),
            Err(Error::WrongPasswordOrTampered)
        );
        // Sai magic bị từ chối.
        let mut bad = blob.clone();
        bad[0] = b'R';
        bad[1] = b'A';
        bad[2] = b'C';
        assert_eq!(decrypt_bytes(&bad, &password), Err(Error::BadMagic));
        assert_eq!(decrypt_bytes(b"ngan", &password), Err(Error::BadMagic));
    }
}
