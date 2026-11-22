//! nd-data: Speck32/64 + sinh dataset cho bo phan biet no-ron kieu Gohr.
//!
//! Port Rust 1-1 tu `tools/ml_distinguisher.py` cua repo me:
//! - Speck32/64 (khoi 32 bit, khoa 64 bit, ALPHA=7, BETA=2, FULL_ROUNDS=22).
//! - Chenh lech ban ro co dinh (FIXED_DX=0x0040, FIXED_DY=0x0000).
//! - Tap can bang: nua nhan 1 (ban ma that), nua nhan 0 (ngau nhien), roi tron.
//!
//! Diem khac duy nhat so voi ban Python: bo sinh so ngau nhien la ChaCha8
//! seeded (`rand_chacha`) thay cho `numpy.random.default_rng`, nen cung mot
//! seed thi ket qua xac dinh nhung khong giong bit-by-bit voi ban numpy
//! (hai thuat toan RNG khac nhau — dieu nay duoc chap nhan theo thiet ke).

use std::fs::File;
use std::io::{self, Read, Write};
use std::path::Path;

use rand::seq::SliceRandom;
use rand::Rng;
use rand::SeedableRng;
use rand_chacha::ChaCha8Rng;

// ---------------------------------------------------------------------------
// Hang so Speck32/64 (giong het ban Python)
// ---------------------------------------------------------------------------

/// Tham so xoay Speck32.
pub const ALPHA: u32 = 7;
/// Tham so xoay Speck32.
pub const BETA: u32 = 2;
/// So vong chuan cua Speck32/64.
pub const FULL_ROUNDS: usize = 22;

/// Chenh lech ban ro co dinh (kieu Gohr): dx = 0x0040, dy = 0x0000.
pub const FIXED_DX: u16 = 0x0040;
/// Chenh lech ban ro co dinh (kieu Gohr): dx = 0x0040, dy = 0x0000.
pub const FIXED_DY: u16 = 0x0000;

// ---------------------------------------------------------------------------
// Speck32/64
// ---------------------------------------------------------------------------

/// Xoay trai tu 16 bit (port cua `rotl16`).
#[inline]
pub fn rotl16(x: u16, r: u32) -> u16 {
    x.rotate_left(r)
}

/// Xoay phai tu 16 bit (port cua `rotr16`).
#[inline]
pub fn rotr16(x: u16, r: u32) -> u16 {
    x.rotate_right(r)
}

/// Mo rong khoa 64 bit (k0..k3) thanh `rounds` khoa vong (port `expand_key`).
pub fn expand_key(khoa: [u16; 4], vong: usize) -> Vec<u16> {
    let mut rk = vec![khoa[0]];
    let mut ell = vec![khoa[1], khoa[2], khoa[3]]; // l0, l1, l2
    for i in 0..vong - 1 {
        let moi_l = rotr16(ell[i], ALPHA).wrapping_add(rk[i]) ^ (i as u16);
        ell.push(moi_l);
        rk.push(rotl16(rk[i], BETA) ^ moi_l);
    }
    rk
}

/// Ma hoa 1 khoi (x, y) qua `vong` vong (port `encrypt`).
pub fn encrypt(ban_ro: (u16, u16), khoa: [u16; 4], vong: usize) -> (u16, u16) {
    let rk = expand_key(khoa, vong);
    let (mut x, mut y) = ban_ro;
    for i in 0..vong {
        x = rotr16(x, ALPHA).wrapping_add(y) ^ rk[i];
        y = rotl16(y, BETA) ^ x;
    }
    (x, y)
}

/// Giai ma 1 khoi (x, y) qua `vong` vong, nguoc voi `encrypt` (port `decrypt`).
pub fn decrypt(ban_ma: (u16, u16), khoa: [u16; 4], vong: usize) -> (u16, u16) {
    let rk = expand_key(khoa, vong);
    let (mut x, mut y) = ban_ma;
    for i in (0..vong).rev() {
        y = rotr16(x ^ y, BETA);
        x = rotl16((x ^ rk[i]).wrapping_sub(y), ALPHA);
    }
    (x, y)
}

// ---------------------------------------------------------------------------
// Dinh dang file .ndd
// ---------------------------------------------------------------------------

/// Chuoi nhan dang file .ndd (4 byte ASCII).
pub const NDD_MAGIC: [u8; 4] = *b"NDD1";
/// Phien ban dinh dang hien tai.
pub const NDD_VERSION: u16 = 1;
/// Kich thuoc header: magic(4) + version(u16) + rounds(u16) + n(u32) + seed(u64).
pub const NDD_HEADER_LEN: usize = 20;
/// Kich thuoc 1 mau: 4 tu u16 little-endian + 1 byte nhan.
pub const NDD_SAMPLE_LEN: usize = 9;

/// Header da doc tu file .ndd.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct NddHeader {
    /// Phien ban dinh dang (luon 1 o ban nay).
    pub phien_ban: u16,
    /// So vong Speck da dung de sinh.
    pub vong: u16,
    /// So mau trong file.
    pub so_mau: u32,
    /// Seed RNG da dung de sinh.
    pub seed: u64,
}

/// Mot mau dataset: cap ban ma (c0, c1) = 4 tu + nhan 0/1.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct Mau {
    /// 4 tu 16 bit: (c0.x, c0.y, c1.x, c1.y); mau nhan 0 la 4 tu ngau nhien.
    pub tu: [u16; 4],
    /// Nhan: 1 = ban ma that, 0 = ngau nhien.
    pub nhan: u8,
}

/// Doi 4 tu 16 bit thanh vector 64 bit MSB-truoc (port `words_to_bits`).
pub fn tu_thanh_bit(tu: &[u16; 4]) -> [f32; 64] {
    let mut ra = [0.0f32; 64];
    for (j, w) in tu.iter().enumerate() {
        for b in 0..16 {
            ra[j * 16 + b] = ((w >> (15 - b)) & 1) as f32;
        }
    }
    ra
}

// ---------------------------------------------------------------------------
// Sinh dataset (port `make_dataset`)
// ---------------------------------------------------------------------------

/// Sinh khoa 64 bit ngau nhien (port `random_key`).
fn khoa_ngau_nhien(rng: &mut ChaCha8Rng) -> [u16; 4] {
    [
        rng.random::<u16>(),
        rng.random::<u16>(),
        rng.random::<u16>(),
        rng.random::<u16>(),
    ]
}

/// Sinh tap can bang: nua nhan 1 (ban ma that), nua nhan 0 (ngau nhien),
/// roi tron deu — port truc tiep `make_dataset` cua ban Python.
///
/// `seed` co dinh cho ket qua xac dinh (RNG ChaCha8 seeded).
pub fn tao_dataset(vong: usize, so_mau: usize, seed: u64) -> Vec<Mau> {
    let mut rng = ChaCha8Rng::seed_from_u64(seed);
    let nua = so_mau / 2;
    let so_mau_1 = nua + (so_mau % 2); // so mau nhan 1 (lam tron len)
    let mut ra = Vec::with_capacity(so_mau);
    // Mau that: cap ban ro lech nhau (FIXED_DX, FIXED_DY), cung khoa ngau nhien.
    for _ in 0..so_mau_1 {
        let khoa = khoa_ngau_nhien(&mut rng);
        let x0 = rng.random::<u16>();
        let y0 = rng.random::<u16>();
        let c0 = encrypt((x0, y0), khoa, vong);
        let c1 = encrypt((x0 ^ FIXED_DX, y0 ^ FIXED_DY), khoa, vong);
        ra.push(Mau {
            tu: [c0.0, c0.1, c1.0, c1.1],
            nhan: 1,
        });
    }
    // Mau ngau nhien: 64 bit hoan toan ngau nhien (= 4 tu u16 ngau nhien).
    for _ in 0..(so_mau - so_mau_1) {
        ra.push(Mau {
            tu: [
                rng.random::<u16>(),
                rng.random::<u16>(),
                rng.random::<u16>(),
                rng.random::<u16>(),
            ],
            nhan: 0,
        });
    }
    ra.shuffle(&mut rng); // tron deu 2 lop (tuong duong permutation)
    ra
}

// ---------------------------------------------------------------------------
// Ghi / doc file .ndd
// ---------------------------------------------------------------------------

/// Ghi dataset ra file .ndd (xem `docs/THIET-KE.md` ve dac ta byte).
pub fn ghi_ndd(duong_dan: &Path, vong: u16, seed: u64, mau: &[Mau]) -> io::Result<()> {
    let mut f = File::create(duong_dan)?;
    let mut dem = Vec::with_capacity(NDD_HEADER_LEN + mau.len() * NDD_SAMPLE_LEN);
    dem.extend_from_slice(&NDD_MAGIC);
    dem.extend_from_slice(&NDD_VERSION.to_le_bytes());
    dem.extend_from_slice(&vong.to_le_bytes());
    dem.extend_from_slice(&(mau.len() as u32).to_le_bytes());
    dem.extend_from_slice(&seed.to_le_bytes());
    for m in mau {
        for w in m.tu {
            dem.extend_from_slice(&w.to_le_bytes());
        }
        dem.push(m.nhan);
    }
    f.write_all(&dem)?;
    Ok(())
}

/// Doc file .ndd, tra ve (header, danh sach mau). Loi neu sai magic,
/// sai phien ban, nhan khong phai 0/1, hoac do dai file khong khop.
pub fn doc_ndd(duong_dan: &Path) -> io::Result<(NddHeader, Vec<Mau>)> {
    let mut dem = Vec::new();
    File::open(duong_dan)?.read_to_end(&mut dem)?;
    if dem.len() < NDD_HEADER_LEN {
        return Err(io::Error::new(
            io::ErrorKind::InvalidData,
            "file .ndd qua ngan (thieu header)",
        ));
    }
    if dem[0..4] != NDD_MAGIC {
        return Err(io::Error::new(
            io::ErrorKind::InvalidData,
            "sai magic .ndd (mong doi 'NDD1')",
        ));
    }
    let phien_ban = u16::from_le_bytes([dem[4], dem[5]]);
    if phien_ban != NDD_VERSION {
        return Err(io::Error::new(
            io::ErrorKind::InvalidData,
            format!("phien ban .ndd khong ho tro: {phien_ban}"),
        ));
    }
    let vong = u16::from_le_bytes([dem[6], dem[7]]);
    let so_mau = u32::from_le_bytes([dem[8], dem[9], dem[10], dem[11]]);
    let seed = u64::from_le_bytes([
        dem[12], dem[13], dem[14], dem[15], dem[16], dem[17], dem[18], dem[19],
    ]);
    let muon = NDD_HEADER_LEN + (so_mau as usize) * NDD_SAMPLE_LEN;
    if dem.len() != muon {
        return Err(io::Error::new(
            io::ErrorKind::InvalidData,
            format!(
                "do dai file {} khong khop header (mong doi {})",
                dem.len(),
                muon
            ),
        ));
    }
    let mut mau = Vec::with_capacity(so_mau as usize);
    for i in 0..(so_mau as usize) {
        let b = NDD_HEADER_LEN + i * NDD_SAMPLE_LEN;
        let mut tu = [0u16; 4];
        for j in 0..4 {
            tu[j] = u16::from_le_bytes([dem[b + j * 2], dem[b + j * 2 + 1]]);
        }
        let nhan = dem[b + 8];
        if nhan > 1 {
            return Err(io::Error::new(
                io::ErrorKind::InvalidData,
                format!("nhan mau {i} khong hop le: {nhan}"),
            ));
        }
        mau.push(Mau { tu, nhan });
    }
    Ok((
        NddHeader {
            phien_ban,
            vong,
            so_mau,
            seed,
        },
        mau,
    ))
}

// ---------------------------------------------------------------------------
// Unit test
// ---------------------------------------------------------------------------

#[cfg(test)]
mod kiem_thu {
    use super::*;

    /// Round-trip ma/giai ma 200 mau voi R=5 va R=22 (port `check_roundtrip`).
    #[test]
    fn vong_di_ve_200_mau() {
        let mut rng = ChaCha8Rng::seed_from_u64(7); // seed co dinh
        for vong in [5usize, FULL_ROUNDS] {
            for _ in 0..200 {
                let khoa = khoa_ngau_nhien(&mut rng);
                let ban_ro = (rng.random::<u16>(), rng.random::<u16>());
                let ban_ma = encrypt(ban_ro, khoa, vong);
                assert_eq!(
                    decrypt(ban_ma, khoa, vong),
                    ban_ro,
                    "sai round-trip R={vong}"
                );
            }
        }
    }

    /// Round-trip ghi/doc file .ndd 200 mau voi R=5 va R=22, seed co dinh.
    #[test]
    fn vong_di_ve_file_ndd() {
        for vong in [5usize, FULL_ROUNDS] {
            let mau = tao_dataset(vong, 200, 42); // seed co dinh
            let duong_dan =
                std::env::temp_dir().join(format!("nd-kiem-thu-r{vong}-ndd-cong-ndd.ndd"));
            ghi_ndd(&duong_dan, vong as u16, 42, &mau).unwrap();
            let (dau, doc) = doc_ndd(&duong_dan).unwrap();
            std::fs::remove_file(&duong_dan).ok();
            assert_eq!(dau.vong, vong as u16);
            assert_eq!(dau.so_mau, 200);
            assert_eq!(dau.seed, 42);
            assert_eq!(doc, mau);
            // Tap phai can bang: 100 nhan 1, 100 nhan 0.
            assert_eq!(doc.iter().filter(|m| m.nhan == 1).count(), 100);
        }
    }

    /// Dac trung bit phai MSB-truoc nhu `words_to_bits`.
    #[test]
    fn bit_msb_truoc() {
        let bit = tu_thanh_bit(&[0x8001, 0x0000, 0xFFFF, 0x0000]);
        assert_eq!(
            &bit[0..16],
            &[1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0]
        );
        assert_eq!(&bit[32..48], &[1.0f32; 16]);
    }

    /// Cung seed cho cung dataset (tinh xac dinh).
    #[test]
    fn cung_seed_cung_ket_qua() {
        assert_eq!(tao_dataset(5, 50, 1), tao_dataset(5, 50, 1));
        assert_ne!(tao_dataset(5, 50, 1), tao_dataset(5, 50, 2));
    }
}
