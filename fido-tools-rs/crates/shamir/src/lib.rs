//! Chia/ghép bí mật Shamir K-trên-N trên trường GF(256).
//!
//! Định dạng file tương thích hoàn toàn với `tools/split_secret.py`:
//! dòng đầu `SHAMIR-SHARE-V1 shares=N threshold=K index=X len=L`,
//! dòng hai là dữ liệu hex (chấp nhận cả chữ hoa như bản Python).
//!
//! Khác bản Python ở chỗ siết 2 lỗi đã biết (sổ NCKH-022, NCKH-028):
//! chỉ số x ngoài 1..=255 và header thiếu khóa đều bị từ chối bằng lỗi
//! tường minh, không bao giờ cho ra bí mật sai lặng.

use std::fmt;

// ---------------------------------------------------------------------------
// Số học GF(256) với đa thức rút gọn của AES: x^8+x^4+x^3+x+1 (0x11B).
// ---------------------------------------------------------------------------

/// Nhân đôi trong GF(256).
const fn xtime(a: u8) -> u8 {
    let v = (a as u16) << 1;
    if v & 0x100 != 0 {
        (v ^ 0x11B) as u8
    } else {
        v as u8
    }
}

/// Dựng bảng log/exp từ phần tử sinh 0x03 (chu kỳ đủ 255).
/// Không dùng 0x02 vì chu kỳ của nó chỉ 51, bảng sẽ thiếu giá trị.
const fn build_tables() -> ([u8; 512], [u8; 256]) {
    let mut exp = [0u8; 512];
    let mut log = [0u8; 256];
    let mut x = 1u8;
    let mut i = 0;
    while i < 255 {
        exp[i] = x;
        log[x as usize] = i as u8;
        x = xtime(x) ^ x; // nhân với 0x03
        i += 1;
    }
    // Lặp lại để cộng chỉ số khỏi cần modulo ở đường nóng.
    while i < 512 {
        exp[i] = exp[i - 255];
        i += 1;
    }
    (exp, log)
}

const TABLES: ([u8; 512], [u8; 256]) = build_tables();

#[inline]
fn gf_mul(a: u8, b: u8) -> u8 {
    if a == 0 || b == 0 {
        return 0;
    }
    TABLES.0[TABLES.1[a as usize] as usize + TABLES.1[b as usize] as usize]
}

#[inline]
fn gf_div(a: u8, b: u8) -> u8 {
    debug_assert!(b != 0, "chia cho 0 trong GF(256)");
    if a == 0 {
        return 0;
    }
    let log = (TABLES.1[a as usize] as usize + 255 - TABLES.1[b as usize] as usize) % 255;
    TABLES.0[log]
}

/// Kiểm tra bảng và phép tính bằng vector AES (FIPS-197). Dùng cho self-test.
pub fn gf_self_check() {
    assert_eq!(gf_mul(0x53, 0xCA), 0x01, "phép nhân GF(256) sai");
    assert_eq!(gf_div(0x01, 0xCA), 0x53, "phép chia GF(256) sai");
}

/// Tính đa thức tại x theo Horner. `coeffs[0]` là hệ số tự do.
fn eval_poly(coeffs: &[u8], x: u8) -> u8 {
    let mut y = 0u8;
    for &c in coeffs.iter().rev() {
        y = gf_mul(y, x) ^ c;
    }
    y
}

// ---------------------------------------------------------------------------
// Lỗi.
// ---------------------------------------------------------------------------

/// Mọi lỗi của thư viện đều là biến thể tường minh, không panic với input xấu.
#[derive(Debug, Clone, PartialEq, Eq)]
pub enum Error {
    /// Bí mật rỗng, không có gì để chia.
    EmptySecret,
    /// Vi phạm 1 <= K <= N <= 255.
    BadParams { n: u16, k: u16 },
    /// Hai share cùng chỉ số x.
    DuplicateX(u8),
    /// Chỉ số x = 0 (không bao giờ do split sinh ra).
    ZeroX,
    /// Chỉ số x ngoài 1..=255 trong file (vá NCKH-022: bản Python cho qua
    /// rồi ghép ra rác lặng).
    XOutOfRange(i64),
    /// Các share không cùng độ dài (lẫn hai lần chia?).
    LengthMismatch,
    /// File không phải share của tool này.
    BadFormat(&'static str),
    /// Header thiếu khóa bắt buộc (vá NCKH-028: bản Python ném KeyError).
    MissingKey(&'static str),
    /// Phần dữ liệu không phải hex hợp lệ.
    BadHex,
}

impl fmt::Display for Error {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            Error::EmptySecret => write!(f, "bí mật rỗng, không có gì để chia"),
            Error::BadParams { n, k } => {
                write!(f, "cần 1 <= threshold <= shares <= 255, nhận k={k} n={n}")
            }
            Error::DuplicateX(x) => write!(f, "share trùng chỉ số x={x}, kiểm tra lại file"),
            Error::ZeroX => write!(f, "chỉ số x=0 không hợp lệ"),
            Error::XOutOfRange(x) => write!(f, "chỉ số x={x} ngoài khoảng 1..=255"),
            Error::LengthMismatch => {
                write!(f, "các share không cùng độ dài, lẫn lộn hai lần chia?")
            }
            Error::BadFormat(s) => write!(f, "file không phải share Shamir của tool này ({s})"),
            Error::MissingKey(k) => write!(f, "header thiếu khóa '{k}'"),
            Error::BadHex => write!(f, "phần dữ liệu không phải hex hợp lệ"),
        }
    }
}

impl std::error::Error for Error {}

// ---------------------------------------------------------------------------
// Chia và ghép Shamir.
// ---------------------------------------------------------------------------

/// Chia `secret` thành `n` share, cần `k` share để ghép. Chỉ số x chạy 1..=n.
pub fn split<R: rand::Rng>(
    secret: &[u8],
    n: u8,
    k: u8,
    rng: &mut R,
) -> Result<Vec<(u8, Vec<u8>)>, Error> {
    if secret.is_empty() {
        return Err(Error::EmptySecret);
    }
    if k == 0 || k > n || n == 0 {
        return Err(Error::BadParams {
            n: n as u16,
            k: k as u16,
        });
    }
    let mut out: Vec<Vec<u8>> = vec![Vec::with_capacity(secret.len()); n as usize];
    let mut coeffs = vec![0u8; k as usize];
    for &byte in secret {
        // Mỗi byte là hệ số tự do của một đa thức ngẫu nhiên bậc k-1.
        coeffs[0] = byte;
        rng.fill(&mut coeffs[1..]);
        for (i, share) in out.iter_mut().enumerate() {
            share.push(eval_poly(&coeffs, (i + 1) as u8));
        }
    }
    Ok(out
        .into_iter()
        .enumerate()
        .map(|(i, y)| ((i + 1) as u8, y))
        .collect())
}

/// Nội suy Lagrange tại x=0. Trong GF(2^8), trừ chính là xor.
fn lagrange_at_zero(xs: &[u8], ys: &[u8]) -> u8 {
    let mut total = 0u8;
    for i in 0..xs.len() {
        let (mut num, mut den) = (1u8, 1u8);
        for j in 0..xs.len() {
            if i == j {
                continue;
            }
            num = gf_mul(num, xs[j]);
            den = gf_mul(den, xs[i] ^ xs[j]);
        }
        total ^= gf_mul(ys[i], gf_div(num, den));
    }
    total
}

/// Ghép các share (x, y) thành bí mật. Mọi share phải cùng độ dài.
pub fn combine(shares: &[(u8, Vec<u8>)]) -> Result<Vec<u8>, Error> {
    if shares.is_empty() {
        return Err(Error::BadFormat("không có share nào để ghép"));
    }
    let mut seen = [false; 256];
    for (x, _) in shares {
        if *x == 0 {
            return Err(Error::ZeroX);
        }
        if seen[*x as usize] {
            return Err(Error::DuplicateX(*x));
        }
        seen[*x as usize] = true;
    }
    let len = shares[0].1.len();
    if shares.iter().any(|(_, y)| y.len() != len) {
        return Err(Error::LengthMismatch);
    }
    let xs: Vec<u8> = shares.iter().map(|(x, _)| *x).collect();
    let mut secret = Vec::with_capacity(len);
    for pos in 0..len {
        let ys: Vec<u8> = shares.iter().map(|(_, y)| y[pos]).collect();
        secret.push(lagrange_at_zero(&xs, &ys));
    }
    Ok(secret)
}

// ---------------------------------------------------------------------------
// Định dạng file share.
// ---------------------------------------------------------------------------

pub const HEADER_MAGIC: &str = "SHAMIR-SHARE-V1";

/// Một share đã bóc: (số share N, ngưỡng K, chỉ số x, dữ liệu y).
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Share {
    pub n: u8,
    pub k: u8,
    pub x: u8,
    pub y: Vec<u8>,
}

fn hex_encode(data: &[u8]) -> String {
    const HEX: &[u8; 16] = b"0123456789abcdef";
    let mut s = String::with_capacity(data.len() * 2);
    for &b in data {
        s.push(HEX[(b >> 4) as usize] as char);
        s.push(HEX[(b & 0xF) as usize] as char);
    }
    s
}

fn hex_val(c: u8) -> Option<u8> {
    match c {
        b'0'..=b'9' => Some(c - b'0'),
        b'a'..=b'f' => Some(c - b'a' + 10),
        b'A'..=b'F' => Some(c - b'A' + 10),
        _ => None,
    }
}

/// Giải hex nghiêm ngặt: độ dài chẵn, chỉ ký tự hex, không khoảng trắng.
/// Chấp nhận cả chữ hoa vì bản Python cũng chấp nhận (so sánh sau khi lower).
fn hex_decode(text: &str) -> Option<Vec<u8>> {
    let b = text.as_bytes();
    if b.len() % 2 != 0 {
        return None;
    }
    let mut out = Vec::with_capacity(b.len() / 2);
    for pair in b.chunks_exact(2) {
        out.push(hex_val(pair[0])? << 4 | hex_val(pair[1])?);
    }
    Some(out)
}

/// Gói share thành text đúng định dạng của bản Python.
pub fn format_share(n: u8, k: u8, x: u8, y: &[u8]) -> String {
    format!(
        "{HEADER_MAGIC} shares={n} threshold={k} index={x} len={}\n{}\n",
        y.len(),
        hex_encode(y)
    )
}

/// Đọc một số nguyên trong header (cho phép dấu + như `int()` của Python).
fn header_int(text: &str) -> Option<i64> {
    text.parse::<i64>().ok()
}

/// Bóc text thành share. Ném lỗi tường minh thay vì panic với mọi input xấu.
pub fn parse_share(text: &str) -> Result<Share, Error> {
    let mut lines = text.trim().split('\n');
    let head = lines.next().unwrap_or("");
    let body = lines.next().unwrap_or("");
    if lines.next().is_some() || !head.starts_with(HEADER_MAGIC) {
        return Err(Error::BadFormat("thiếu magic hoặc thừa dòng"));
    }
    let mut n = None;
    let mut k = None;
    let mut x = None;
    let mut len = None;
    for part in head.split_whitespace().skip(1) {
        let (key, val) = part
            .split_once('=')
            .ok_or(Error::BadFormat("mẩu header lạ"))?;
        let num = header_int(val).ok_or(Error::BadFormat("giá trị header không phải số"))?;
        match key {
            "shares" => n = Some(num),
            "threshold" => k = Some(num),
            "index" => x = Some(num),
            "len" => len = Some(num),
            _ => return Err(Error::BadFormat("khóa header lạ")),
        }
    }
    let n = n.ok_or(Error::MissingKey("shares"))?;
    let k = k.ok_or(Error::MissingKey("threshold"))?;
    let x = x.ok_or(Error::MissingKey("index"))?;
    let len = len.ok_or(Error::MissingKey("len"))?;
    let y = hex_decode(body.trim_end_matches('\r')).ok_or(Error::BadHex)?;
    if y.len() as i64 != len {
        return Err(Error::BadFormat("độ dài dữ liệu không khớp header"));
    }
    // Vá NCKH-022: từ chối x ngoài 1..=255 ngay khi đọc, đừng đợi tới combine.
    if !(1..=255).contains(&x) {
        return Err(Error::XOutOfRange(x));
    }
    if k < 1 || k > n || n < 1 || n > 255 {
        return Err(Error::BadParams {
            n: n as u16,
            k: k as u16,
        });
    }
    Ok(Share {
        n: n as u8,
        k: k as u8,
        x: x as u8,
        y,
    })
}

// ---------------------------------------------------------------------------
// Unit test: port toàn bộ self-test của bản Python + các ca siết mới.
// ---------------------------------------------------------------------------

#[cfg(test)]
mod tests {
    use super::*;
    use rand::{Rng, SeedableRng};

    fn rng() -> rand::rngs::StdRng {
        rand::rngs::StdRng::seed_from_u64(0xC0FFEE)
    }

    #[test]
    fn bang_gf_du_vector_aes() {
        gf_self_check();
        assert_eq!(TABLES.1[1], 0);
        assert_ne!(TABLES.1[0x53], 0);
    }

    /// Liệt kê mọi tập con K share (thay cho itertools của Python).
    fn subsets<T: Clone>(items: &[T], k: usize) -> Vec<Vec<T>> {
        fn go<T: Clone>(
            items: &[T],
            k: usize,
            start: usize,
            cur: &mut Vec<T>,
            acc: &mut Vec<Vec<T>>,
        ) {
            if cur.len() == k {
                acc.push(cur.clone());
                return;
            }
            for i in start..items.len() {
                cur.push(items[i].clone());
                go(items, k, i + 1, cur, acc);
                cur.pop();
            }
        }
        let mut acc = Vec::new();
        go(items, k, 0, &mut Vec::new(), &mut acc);
        acc
    }

    #[test]
    fn chia_ghep_dung_moi_nguong() {
        for (n, k) in [(3u8, 2u8), (5, 3), (5, 5), (8, 2)] {
            let mut r = rng();
            let secret: Vec<u8> = (0..16).map(|_| r.random()).collect();
            let shares = split(&secret, n, k, &mut r).unwrap();
            assert_eq!(
                shares.iter().map(|(x, _)| *x).collect::<Vec<_>>(),
                (1..=n).collect::<Vec<_>>()
            );
            for sub in subsets(&shares, k as usize) {
                assert_eq!(combine(&sub).unwrap(), secret, "ghép sai với n={n} k={k}");
            }
            assert_eq!(combine(&shares).unwrap(), secret); // thừa share vẫn đúng
        }
    }

    #[test]
    fn thieu_share_ra_khac() {
        let mut r = rng();
        let secret: Vec<u8> = (0..16).map(|_| r.random()).collect();
        let shares = split(&secret, 3, 2, &mut r).unwrap();
        assert_ne!(combine(&shares[..1]).unwrap(), secret);
    }

    #[test]
    fn file_hong_bi_tu_choi() {
        assert_eq!(
            parse_share(&format_share(3, 2, 1, b"abcdefgh")).unwrap().x,
            1
        );
        let bad = [
            "rác".to_string(),
            format!("{HEADER_MAGIC} shares=3\nzzzz"),
            format_share(3, 2, 1, b"abcdefgh").replace("len=8", "len=7"),
        ];
        for b in bad {
            assert!(parse_share(&b).is_err(), "đáng lẽ phải từ chối: {b:?}");
        }
    }

    #[test]
    fn trung_x_va_khac_do_dai_bi_tu_choi() {
        assert_eq!(
            combine(&[(1, b"aa".to_vec()), (1, b"bb".to_vec())]),
            Err(Error::DuplicateX(1))
        );
        assert_eq!(
            combine(&[(1, b"aa".to_vec()), (2, b"bbb".to_vec())]),
            Err(Error::LengthMismatch)
        );
    }

    #[test]
    fn siet_moi_index_am_va_qua_255() {
        // Vá NCKH-022: bản Python chấp nhận rồi ghép ra rác lặng.
        for bad_x in ["-1", "0", "256", "300"] {
            let text = format!("{HEADER_MAGIC} shares=5 threshold=3 index={bad_x} len=2\nabcd\n");
            assert!(
                matches!(parse_share(&text), Err(Error::XOutOfRange(_))),
                "x={bad_x} phải bị từ chối"
            );
        }
    }

    #[test]
    fn siet_moi_header_thieu_khoa() {
        // Vá NCKH-028: bản Python ném KeyError thay vì ValueError.
        let text = format!("{HEADER_MAGIC} shares=5 threshold=3 len=2\nabcd\n");
        assert_eq!(parse_share(&text), Err(Error::MissingKey("index")));
    }
}
