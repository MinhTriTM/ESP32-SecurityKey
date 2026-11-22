//! Kiem thu vector Speck tu fixture do ban Python me sinh ra.
//!
//! Fixture `tests/fixtures/speck.json` duoc tao bang cach import `encrypt`
//! tu `tools/ml_distinguisher.py` — khong tu bia vector.

use nd_data::encrypt;

/// Doc so nguyen ke tiep tu chuoi, bat dau tai vi tri `pos`.
fn doc_so(chuoi: &[u8], pos: &mut usize) -> u16 {
    while *pos < chuoi.len() && !chuoi[*pos].is_ascii_digit() {
        *pos += 1;
    }
    let bat_dau = *pos;
    while *pos < chuoi.len() && chuoi[*pos].is_ascii_digit() {
        *pos += 1;
    }
    std::str::from_utf8(&chuoi[bat_dau..*pos])
        .unwrap()
        .parse()
        .unwrap()
}

/// Tim khoa JSON `"ten"` ke tu vi tri hien tai, tra ve vi tri sau dau hai cham.
fn tim_khoa(chuoi: &[u8], pos: &mut usize, ten: &str) {
    let mau = format!("\"{ten}\"");
    let tu = *pos;
    let tim = chuoi[tu..]
        .windows(mau.len())
        .position(|w| w == mau.as_bytes())
        .unwrap_or_else(|| panic!("khong thay khoa {ten} trong fixture"));
    *pos = tu + tim + mau.len();
    while chuoi[*pos] != b':' {
        *pos += 1;
    }
    *pos += 1;
}

#[test]
fn vector_speck_khop_ban_python() {
    let duong_dan = concat!(
        env!("CARGO_MANIFEST_DIR"),
        "/../../tests/fixtures/speck.json"
    );
    let chuoi = std::fs::read(duong_dan).expect("khong doc duoc fixture speck.json");
    // Bo qua phan "nguon" (chi la chuoi mo ta), bat dau tu mang "vectors".
    let mut pos = 0usize;
    tim_khoa(&chuoi, &mut pos, "vectors");
    let mut dem = 0;
    loop {
        // Tim vector tiep theo qua khoa "khoa"; het file thi dung.
        let con_lai = &chuoi[pos..];
        if !con_lai.windows(6).any(|w| w == b"\"khoa\"") {
            break;
        }
        tim_khoa(&chuoi, &mut pos, "khoa");
        let khoa = [
            doc_so(&chuoi, &mut pos),
            doc_so(&chuoi, &mut pos),
            doc_so(&chuoi, &mut pos),
            doc_so(&chuoi, &mut pos),
        ];
        tim_khoa(&chuoi, &mut pos, "ban_ro");
        let ban_ro = (doc_so(&chuoi, &mut pos), doc_so(&chuoi, &mut pos));
        tim_khoa(&chuoi, &mut pos, "vong");
        let vong = doc_so(&chuoi, &mut pos) as usize;
        tim_khoa(&chuoi, &mut pos, "ban_ma");
        let muon = (doc_so(&chuoi, &mut pos), doc_so(&chuoi, &mut pos));
        let duoc = encrypt(ban_ro, khoa, vong);
        assert_eq!(
            duoc, muon,
            "sai vector thu {dem}: khoa={khoa:?} pt={ban_ro:?} R={vong}"
        );
        dem += 1;
    }
    assert!(dem >= 6, "fixture phai co it nhat 6 vector, thay {dem}");
    println!("Da kiem {dem} vector Speck tu fixture Python: deu khop.");
}
