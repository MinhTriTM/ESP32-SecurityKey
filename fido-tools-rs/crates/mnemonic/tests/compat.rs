//! Khớp vector do bản Python sinh ra (oracle độc lập).
//!
//! Mỗi dòng `vectors.txt`: `<hex entropy> | <cụm từ> | <hex seed với passphrase TREZOR>`.

use esk_mnemonic::{entropy_to_mnemonic, load_wordlist, mnemonic_to_entropy, mnemonic_to_seed};
use std::path::PathBuf;

fn hex_decode(s: &str) -> Vec<u8> {
    (0..s.len())
        .step_by(2)
        .map(|i| u8::from_str_radix(&s[i..i + 2], 16).unwrap())
        .collect()
}

fn hex_of(data: &[u8]) -> String {
    data.iter().map(|b| format!("{b:02x}")).collect()
}

#[test]
fn khop_vector_cua_python() {
    let words = load_wordlist().unwrap();
    let dir = PathBuf::from(env!("CARGO_MANIFEST_DIR"))
        .join("tests")
        .join("fixtures");
    let text = std::fs::read_to_string(dir.join("vectors.txt")).unwrap();
    assert!(!text.trim().is_empty());
    for line in text.lines() {
        let parts: Vec<&str> = line.split(" | ").collect();
        assert_eq!(parts.len(), 3);
        let entropy = hex_decode(parts[0]);
        assert_eq!(entropy_to_mnemonic(&entropy, &words).unwrap(), parts[1]);
        assert_eq!(mnemonic_to_entropy(parts[1], &words).unwrap(), entropy);
        assert_eq!(hex_of(&mnemonic_to_seed(parts[1], "TREZOR")), parts[2]);
    }
}
