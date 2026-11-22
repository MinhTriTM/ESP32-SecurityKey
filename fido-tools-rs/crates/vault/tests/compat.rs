//! Mở được két do bản Python mã hóa (oracle độc lập).
//!
//! Fixture sinh bằng: `python tools/vault.py encrypt --in plain.txt
//! --out ket-py.bin --password-file password.txt`.

use esk_vault::decrypt_bytes;
use std::path::PathBuf;

fn fixtures() -> PathBuf {
    PathBuf::from(env!("CARGO_MANIFEST_DIR"))
        .join("tests")
        .join("fixtures")
}

#[test]
fn mo_duoc_ket_cua_python() {
    let dir = fixtures();
    let blob = std::fs::read(dir.join("ket-py.bin")).unwrap();
    let password = std::fs::read(dir.join("password.txt")).unwrap();
    let plain = std::fs::read(dir.join("plain.txt")).unwrap();
    assert_eq!(decrypt_bytes(&blob, &password).unwrap(), plain);
    // Sai mật khẩu vẫn bị từ chối.
    assert!(decrypt_bytes(&blob, b"sai").is_err());
}
