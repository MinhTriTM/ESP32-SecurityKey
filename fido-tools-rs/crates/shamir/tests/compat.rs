//! Tương thích với share do bản Python sinh ra (oracle độc lập).
//!
//! Fixture sinh bằng: `python tools/split_secret.py split --shares 5
//! --threshold 3 --from-file secret.bin --out py-shares`.

use esk_shamir::{combine, parse_share};
use std::path::PathBuf;

fn fixtures() -> PathBuf {
    PathBuf::from(env!("CARGO_MANIFEST_DIR"))
        .join("tests")
        .join("fixtures")
}

#[test]
fn ghep_duoc_share_cua_python() {
    let dir = fixtures();
    let secret = std::fs::read(dir.join("secret.bin")).unwrap();
    let mut shares = Vec::new();
    // Chỉ dùng 3 trong 5 share (đúng ngưỡng K=3), cố tình bỏ qua share 2 và 4.
    for i in [1, 3, 5] {
        let text =
            std::fs::read_to_string(dir.join(format!("py-shares/share-{i}-of-5.txt"))).unwrap();
        let s = parse_share(&text).unwrap();
        assert_eq!((s.n, s.k), (5, 3));
        shares.push((s.x, s.y));
    }
    assert_eq!(combine(&shares).unwrap(), secret);
}
