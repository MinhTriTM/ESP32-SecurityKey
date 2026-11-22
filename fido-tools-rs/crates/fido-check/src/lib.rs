//! Giao thức CTAPHID + CTAP2 GetInfo, tương đương `tools/fido_check.py`.
//!
//! Giữ nguyên mọi hằng số framing (gói 64 byte, report ID 0, INIT/PING/CBOR)
//! để nói chuyện được với cùng firmware. Khác bản Python ở bộ giải CBOR
//! nghiêm ngặt: chặn thân cụt, chặn lồng quá sâu, từ chối text không UTF-8,
//! không bao giờ panic với input xấu (vá 3 phát hiện fuzz ở sổ NCKH-010).

use std::collections::HashMap;
use std::fmt;

pub const FIDO_USAGE_PAGE: u16 = 0xF1D0;
pub const PACKET_SIZE: usize = 64;
pub const CID_BROADCAST: u32 = 0xFFFF_FFFF;

pub const CTAPHID_PING: u8 = 0x01;
pub const CTAPHID_MSG: u8 = 0x03;
pub const CTAPHID_INIT: u8 = 0x06;
pub const CTAPHID_CBOR: u8 = 0x10;
pub const CTAPHID_ERROR: u8 = 0x3F;

pub const CTAP2_GET_INFO: u8 = 0x04;

/// Độ sâu lồng CBOR tối đa (chặn RecursionError kiểu bản Python).
pub const CBOR_MAX_DEPTH: usize = 32;

fn hid_error_text(code: u8) -> &'static str {
    match code {
        0x01 => "lệnh sai",
        0x02 => "tham số sai",
        0x03 => "độ dài sai",
        0x04 => "thứ tự gói sai",
        0x05 => "key hết giờ",
        0x06 => "kênh bận",
        0x0A => "kênh đang khóa",
        0x0B => "CID sai",
        _ => "không rõ",
    }
}

fn ctap2_error_text(code: u8) -> &'static str {
    match code {
        0x00 => "ok",
        0x01 => "lệnh CTAP2 sai",
        0x02 => "tham số CBOR sai",
        0x03 => "độ dài sai",
        0x04 => "thứ tự sai",
        0x05 => "hết giờ",
        0x06 => "kênh bận",
        0x0A => "cần mở khóa",
        0x27 => "lệnh chưa hỗ trợ",
        _ => "không rõ",
    }
}

fn getinfo_name(key: i128) -> String {
    match key {
        0x01 => "versions".to_string(),
        0x02 => "extensions".to_string(),
        0x03 => "aaguid".to_string(),
        0x04 => "options".to_string(),
        0x05 => "maxMsgSize".to_string(),
        0x06 => "pinUvAuthProtocols".to_string(),
        0x07 => "maxCredentialCountInList".to_string(),
        0x08 => "maxCredentialIdLength".to_string(),
        0x09 => "transports".to_string(),
        0x0A => "algorithms".to_string(),
        0x0D => "minPINLength".to_string(),
        0x0E => "firmwareVersion".to_string(),
        _ => format!("0x{key:02x}"),
    }
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub enum Error {
    /// Key trả về gói CTAPHID_ERROR.
    CtapHid(u8),
    /// Lệnh CTAP2 trả về status lỗi.
    Ctap2(u8),
    /// Thiết bị không trả lời (hết giờ đọc).
    Timeout,
    /// Framing hoặc CBOR sai.
    Protocol(String),
}

impl fmt::Display for Error {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            Error::CtapHid(c) => write!(f, "lỗi CTAPHID 0x{c:02x}: {}", hid_error_text(*c)),
            Error::Ctap2(c) => write!(f, "lỗi CTAP2 0x{c:02x}: {}", ctap2_error_text(*c)),
            Error::Timeout => write!(f, "thiết bị không trả lời (hết giờ đọc)"),
            Error::Protocol(s) => write!(f, "{s}"),
        }
    }
}

impl std::error::Error for Error {}

// ---------------------------------------------------------------------------
// Framing gói CTAPHID.
// ---------------------------------------------------------------------------

/// Gói INIT: CID broadcast + CMD + độ dài 8 + nonce 8 byte.
pub fn build_init_packet(nonce: &[u8; 8]) -> [u8; PACKET_SIZE] {
    let mut pkt = [0u8; PACKET_SIZE];
    pkt[0..4].copy_from_slice(&CID_BROADCAST.to_be_bytes());
    pkt[4] = CTAPHID_INIT | 0x80;
    pkt[5..7].copy_from_slice(&8u16.to_be_bytes());
    pkt[7..15].copy_from_slice(nonce);
    pkt
}

/// Gói PING đơn (payload tối đa 57 byte). Dài hơn thì dùng `send_msg`.
pub fn build_ping_packet(cid: u32, payload: &[u8]) -> Result<[u8; PACKET_SIZE], Error> {
    if payload.len() > 57 {
        return Err(Error::Protocol(format!(
            "PING đơn chỉ chứa 57 byte, nhận {}",
            payload.len()
        )));
    }
    let mut pkt = [0u8; PACKET_SIZE];
    pkt[0..4].copy_from_slice(&cid.to_be_bytes());
    pkt[4] = CTAPHID_PING | 0x80;
    pkt[5..7].copy_from_slice(&(payload.len() as u16).to_be_bytes());
    pkt[7..7 + payload.len()].copy_from_slice(payload);
    Ok(pkt)
}

/// Cắt message thành gói mở đầu + gói nối tiếp (chưa có report ID).
pub fn fragment(cid: u32, cmd: u8, data: &[u8]) -> Result<Vec<[u8; PACKET_SIZE]>, Error> {
    if data.len() > 0xFFFF {
        return Err(Error::Protocol("message quá 64KB".to_string()));
    }
    let mut packets = Vec::new();
    let mut first = [0u8; PACKET_SIZE];
    first[0..4].copy_from_slice(&cid.to_be_bytes());
    first[4] = cmd | 0x80;
    first[5..7].copy_from_slice(&(data.len() as u16).to_be_bytes());
    let take = data.len().min(PACKET_SIZE - 7);
    first[7..7 + take].copy_from_slice(&data[..take]);
    packets.push(first);
    let (mut rest, mut seq) = (&data[take..], 0u8);
    while !rest.is_empty() {
        let mut cont = [0u8; PACKET_SIZE];
        cont[0..4].copy_from_slice(&cid.to_be_bytes());
        cont[4] = seq;
        let take = rest.len().min(PACKET_SIZE - 5);
        cont[5..5 + take].copy_from_slice(&rest[..take]);
        packets.push(cont);
        rest = &rest[take..];
        seq = seq.wrapping_add(1);
    }
    Ok(packets)
}

/// Trừu tượng thiết bị HID để key giả trong RAM dùng chung code với key thật.
pub trait Hid {
    fn write_packet(&mut self, packet_with_rid: &[u8]) -> Result<(), Error>;
    fn read_packet(&mut self, timeout_ms: i32) -> Result<Vec<u8>, Error>;
}

impl Hid for hidapi::HidDevice {
    fn write_packet(&mut self, packet_with_rid: &[u8]) -> Result<(), Error> {
        self.write(packet_with_rid)
            .map(|_| ())
            .map_err(|e| Error::Protocol(format!("lỗi HID: {e}")))
    }
    fn read_packet(&mut self, timeout_ms: i32) -> Result<Vec<u8>, Error> {
        let mut buf = [0u8; PACKET_SIZE + 1];
        let n = self
            .read_timeout(&mut buf, timeout_ms)
            .map_err(|e| Error::Protocol(format!("lỗi HID: {e}")))?;
        Ok(buf[..n].to_vec())
    }
}

/// Gửi message, tự cắt gói. Mỗi gói ghi kèm report ID 0 ở đầu.
pub fn send_msg(dev: &mut impl Hid, cid: u32, cmd: u8, data: &[u8]) -> Result<(), Error> {
    for packet in fragment(cid, cmd, data)? {
        let mut with_rid = Vec::with_capacity(PACKET_SIZE + 1);
        with_rid.push(0u8);
        with_rid.extend_from_slice(&packet);
        dev.write_packet(&with_rid)?;
    }
    Ok(())
}

/// Bóc report ID: nền tảng trả kèm (65 byte), có nền tảng không (64 byte).
fn strip_report_id(buf: &[u8]) -> Result<&[u8], Error> {
    if buf.len() == PACKET_SIZE + 1 {
        Ok(&buf[1..])
    } else if buf.len() == PACKET_SIZE {
        Ok(buf)
    } else {
        Err(Error::Protocol(format!(
            "gói HID dài lạ: {} byte",
            buf.len()
        )))
    }
}

/// Đọc message, tự ghép gói nối tiếp. Trả về (cid, cmd, data).
pub fn recv_msg(dev: &mut impl Hid, timeout_ms: i32) -> Result<(u32, u8, Vec<u8>), Error> {
    let raw = dev.read_packet(timeout_ms)?;
    if raw.is_empty() {
        return Err(Error::Timeout);
    }
    let pkt = strip_report_id(&raw)?;
    let cid = u32::from_be_bytes([pkt[0], pkt[1], pkt[2], pkt[3]]);
    let mut cmd = pkt[4];
    if cmd & 0x80 == 0 {
        return Err(Error::Protocol("gói đầu thiếu bit lệnh".to_string()));
    }
    cmd &= 0x7F;
    let bcnt = u16::from_be_bytes([pkt[5], pkt[6]]) as usize;
    let take = bcnt.min(PACKET_SIZE - 7);
    let mut data = pkt[7..7 + take].to_vec();
    if cmd == CTAPHID_ERROR {
        return Err(Error::CtapHid(data.first().copied().unwrap_or(0x00)));
    }
    let mut seq = 0u8;
    while data.len() < bcnt {
        let raw = dev.read_packet(timeout_ms)?;
        if raw.is_empty() {
            return Err(Error::Protocol(
                "gói nối không tới (hết giờ đọc)".to_string(),
            ));
        }
        let cont = strip_report_id(&raw)?;
        if u32::from_be_bytes([cont[0], cont[1], cont[2], cont[3]]) != cid {
            return Err(Error::Protocol("gói nối sai CID".to_string()));
        }
        if cont[4] != seq {
            return Err(Error::Protocol(format!(
                "gói nối sai thứ tự (muốn {seq}, thấy {})",
                cont[4]
            )));
        }
        let take = (bcnt - data.len()).min(PACKET_SIZE - 5);
        data.extend_from_slice(&cont[5..5 + take]);
        seq = seq.wrapping_add(1);
    }
    Ok((cid, cmd, data))
}

/// Kết quả bóc 17 byte trả về của INIT.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct InitResponse {
    pub nonce: [u8; 8],
    pub new_cid: u32,
    pub version: u8,
    pub capabilities: u8,
}

/// Bóc 17 byte trả về của INIT: nonce + CID mới + version + khả năng.
pub fn parse_init_response(data: &[u8]) -> Result<InitResponse, Error> {
    if data.len() < 17 {
        return Err(Error::Protocol(format!(
            "INIT trả về quá ngắn: {} byte",
            data.len()
        )));
    }
    let mut nonce = [0u8; 8];
    nonce.copy_from_slice(&data[0..8]);
    Ok(InitResponse {
        nonce,
        new_cid: u32::from_be_bytes([data[8], data[9], data[10], data[11]]),
        version: data[12],
        capabilities: data[16],
    })
}

fn hex_of(data: &[u8]) -> String {
    data.iter().map(|b| format!("{b:02x}")).collect()
}

// ---------------------------------------------------------------------------
// Giải mã CBOR tối thiểu (đủ cho GetInfo: số, bytes, text, mảng, map).
// ---------------------------------------------------------------------------

/// Giá trị CBOR. Map giữ dạng danh sách cặp để khỏi panic kiểu
/// "unhashable key" như bản Python khi key là mảng.
#[derive(Debug, Clone, PartialEq, Eq)]
pub enum Cbor {
    Int(i128),
    Bytes(Vec<u8>),
    Text(String),
    Array(Vec<Cbor>),
    Map(Vec<(Cbor, Cbor)>),
    Bool(bool),
    Null,
}

fn cbor_arg(buf: &[u8]) -> Result<(u8, u64, usize), Error> {
    let b = *buf
        .first()
        .ok_or_else(|| Error::Protocol("CBOR cụt".to_string()))?;
    let (major, info) = (b >> 5, b & 31);
    if info < 24 {
        return Ok((major, info as u64, 1));
    }
    let need = match info {
        24 => 1,
        25 => 2,
        26 => 4,
        27 => 8,
        _ => {
            return Err(Error::Protocol(
                "CBOR dùng kiểu không hỗ trợ hoặc bị cụt".to_string(),
            ))
        }
    };
    if buf.len() < 1 + need {
        return Err(Error::Protocol(
            "CBOR dùng kiểu không hỗ trợ hoặc bị cụt".to_string(),
        ));
    }
    let mut v = 0u64;
    for &x in &buf[1..1 + need] {
        v = (v << 8) | x as u64;
    }
    Ok((major, v, 1 + need))
}

/// Giải mã một giá trị CBOR. Trả về (giá trị, phần còn lại).
pub fn cbor_decode(buf: &[u8]) -> Result<(Cbor, &[u8]), Error> {
    decode_inner(buf, 0)
}

fn decode_inner(buf: &[u8], depth: usize) -> Result<(Cbor, &[u8]), Error> {
    if depth > CBOR_MAX_DEPTH {
        return Err(Error::Protocol(format!(
            "CBOR lồng quá sâu (>{CBOR_MAX_DEPTH})"
        )));
    }
    let (major, arg, hlen) = cbor_arg(buf)?;
    let rest = &buf[hlen..];
    match major {
        0 => Ok((Cbor::Int(arg as i128), rest)),
        1 => Ok((Cbor::Int(-1 - arg as i128), rest)),
        2 => {
            let n = arg as usize;
            if rest.len() < n {
                return Err(Error::Protocol("CBOR bytes cụt thân".to_string()));
            }
            Ok((Cbor::Bytes(rest[..n].to_vec()), &rest[n..]))
        }
        3 => {
            let n = arg as usize;
            if rest.len() < n {
                return Err(Error::Protocol("CBOR text cụt thân".to_string()));
            }
            let s = std::str::from_utf8(&rest[..n])
                .map_err(|_| Error::Protocol("CBOR text không phải UTF-8".to_string()))?;
            Ok((Cbor::Text(s.to_string()), &rest[n..]))
        }
        4 => {
            // Mỗi phần tử tốn ít nhất 1 byte nên số lượng không thể vượt số byte còn lại.
            if arg > rest.len() as u64 {
                return Err(Error::Protocol("CBOR mảng cụt".to_string()));
            }
            let mut items = Vec::with_capacity(arg.min(1024) as usize);
            let mut tail = rest;
            for _ in 0..arg {
                let (v, r) = decode_inner(tail, depth + 1)?;
                items.push(v);
                tail = r;
            }
            Ok((Cbor::Array(items), tail))
        }
        5 => {
            // Mỗi cặp key+value tốn ít nhất 2 byte.
            if arg > rest.len() as u64 / 2 {
                return Err(Error::Protocol("CBOR map cụt".to_string()));
            }
            let mut pairs = Vec::with_capacity((arg.min(512)) as usize);
            let mut tail = rest;
            for _ in 0..arg {
                let (k, r) = decode_inner(tail, depth + 1)?;
                let (v, r) = decode_inner(r, depth + 1)?;
                pairs.push((k, v));
                tail = r;
            }
            Ok((Cbor::Map(pairs), tail))
        }
        7 => match arg {
            20 => Ok((Cbor::Bool(false), rest)),
            21 => Ok((Cbor::Bool(true), rest)),
            22 => Ok((Cbor::Null, rest)),
            _ => Err(Error::Protocol(
                "CBOR dùng kiểu simple/float không hỗ trợ".to_string(),
            )),
        },
        _ => Err(Error::Protocol("CBOR dùng kiểu không hỗ trợ".to_string())),
    }
}

// ---------------------------------------------------------------------------
// CTAP2 GetInfo.
// ---------------------------------------------------------------------------

/// Trường GetInfo đã đặt tên. `aaguid` giữ dạng hex như bản Python.
#[derive(Debug, Clone, Default)]
pub struct GetInfo {
    pub fields: Vec<(String, Cbor)>,
}

impl GetInfo {
    pub fn get(&self, name: &str) -> Option<&Cbor> {
        self.fields.iter().find(|(n, _)| n == name).map(|(_, v)| v)
    }
}

/// Gửi authenticatorGetInfo, trả về map đã đặt tên trường.
pub fn ctap2_get_info(dev: &mut impl Hid, cid: u32) -> Result<GetInfo, Error> {
    send_msg(dev, cid, CTAPHID_CBOR, &[CTAP2_GET_INFO])?;
    let (_, cmd, data) = recv_msg(dev, 2000)?;
    if cmd != CTAPHID_CBOR {
        return Err(Error::Protocol(format!(
            "muốn CBOR mà nhận lệnh 0x{cmd:02x}"
        )));
    }
    let status = *data
        .first()
        .ok_or_else(|| Error::Protocol("CBOR trả về rỗng".to_string()))?;
    if status != 0 {
        return Err(Error::Ctap2(status));
    }
    let (info, _) = cbor_decode(&data[1..])?;
    let Cbor::Map(pairs) = info else {
        return Err(Error::Protocol("GetInfo không trả về map".to_string()));
    };
    let mut fields = Vec::new();
    for (k, v) in pairs {
        let name = match &k {
            Cbor::Int(i) => getinfo_name(*i),
            other => format!("{other:?}"),
        };
        let v = match (&k, v) {
            (Cbor::Int(3), Cbor::Bytes(b)) => Cbor::Text(hex_of(&b)),
            (_, v) => v,
        };
        fields.push((name, v));
    }
    Ok(GetInfo { fields })
}

// ---------------------------------------------------------------------------
// Key giả trong RAM để tự kiểm tra không cần phần cứng.
// ---------------------------------------------------------------------------

/// GetInfo mẫu: versions [U2F_V2, FIDO_2_0], options {rk: true}, maxMsgSize 1024.
pub const CANNED_GETINFO: &[u8] = &[
    0xA3, 0x01, 0x82, 0x66, 0x55, 0x32, 0x46, 0x5F, 0x56, 0x32, 0x68, 0x46, 0x49, 0x44, 0x4F, 0x5F,
    0x32, 0x5F, 0x30, 0x04, 0xA1, 0x62, 0x72, 0x6B, 0xF5, 0x05, 0x19, 0x04, 0x00,
];

pub const NEW_CID: u32 = 0xAABBCCDD;

/// Giả lập key FIDO: INIT cấp CID mới, PING echo, CBOR trả GetInfo mẫu.
pub struct FakeDevice {
    with_report_id: bool,
    queue: Vec<Vec<u8>>,
    pending: Vec<u8>,
    pending_cmd: u8,
    pending_cid: u32,
    pending_len: usize,
}

impl FakeDevice {
    pub fn new(with_report_id: bool) -> Self {
        FakeDevice {
            with_report_id,
            queue: Vec::new(),
            pending: Vec::new(),
            pending_cmd: 0,
            pending_cid: 0,
            pending_len: 0,
        }
    }

    fn emit(&mut self, cid: u32, cmd: u8, data: &[u8]) {
        for packet in fragment(cid, cmd, data).unwrap() {
            let mut q = Vec::with_capacity(PACKET_SIZE + 1);
            if self.with_report_id {
                q.push(0u8);
            }
            q.extend_from_slice(&packet);
            self.queue.push(q);
        }
    }

    fn answer(&mut self) {
        let data = std::mem::take(&mut self.pending);
        let cid = self.pending_cid;
        match self.pending_cmd {
            CTAPHID_INIT => {
                let mut resp = Vec::new();
                resp.extend_from_slice(data.get(..8).unwrap_or(&[]));
                resp.extend_from_slice(&NEW_CID.to_be_bytes());
                resp.extend_from_slice(&[2, 0, 0, 0, 0x05]);
                self.emit(CID_BROADCAST, CTAPHID_INIT, &resp);
            }
            CTAPHID_PING => self.emit(cid, CTAPHID_PING, &data),
            CTAPHID_CBOR if data.first() == Some(&CTAP2_GET_INFO) => {
                let mut resp = vec![0x00];
                resp.extend_from_slice(CANNED_GETINFO);
                self.emit(cid, CTAPHID_CBOR, &resp);
            }
            _ => self.emit(cid, CTAPHID_ERROR, &[0x01]),
        }
    }
}

impl Hid for FakeDevice {
    fn write_packet(&mut self, packet_with_rid: &[u8]) -> Result<(), Error> {
        if packet_with_rid.len() < 8 {
            return Err(Error::Protocol("gói ghi quá ngắn".to_string()));
        }
        let body = &packet_with_rid[1..];
        let cid = u32::from_be_bytes([body[0], body[1], body[2], body[3]]);
        if body[4] & 0x80 != 0 {
            self.pending_cid = cid;
            self.pending_cmd = body[4] & 0x7F;
            self.pending_len = u16::from_be_bytes([body[5], body[6]]) as usize;
            let take = self.pending_len.min(57).min(body.len().saturating_sub(7));
            self.pending = body[7..7 + take].to_vec();
        } else {
            let take = (self.pending_len.saturating_sub(self.pending.len()))
                .min(59)
                .min(body.len().saturating_sub(5));
            self.pending.extend_from_slice(&body[5..5 + take]);
        }
        if self.pending.len() >= self.pending_len {
            self.answer();
        }
        Ok(())
    }

    fn read_packet(&mut self, _timeout_ms: i32) -> Result<Vec<u8>, Error> {
        Ok(if self.queue.is_empty() {
            Vec::new()
        } else {
            self.queue.remove(0)
        })
    }
}

/// Lọc thiết bị FIDO theo usage page (+VID/PID tùy chọn). Tách riêng để test.
pub fn fido_matches(
    usage_page: u16,
    vid: u16,
    pid: u16,
    want_vid: Option<u16>,
    want_pid: Option<u16>,
) -> bool {
    usage_page == FIDO_USAGE_PAGE
        && want_vid.map_or(true, |v| v == vid)
        && want_pid.map_or(true, |p| p == pid)
}

#[allow(dead_code)]
fn _use_msg_const() {
    let _ = CTAPHID_MSG;
    let _ = HashMap::<u8, u8>::new();
}

// ---------------------------------------------------------------------------
// Unit test: port toàn bộ self-test của bản Python + ca siết CBOR mới.
// ---------------------------------------------------------------------------

#[cfg(test)]
mod tests {
    use super::*;

    fn hex(s: &str) -> Vec<u8> {
        (0..s.len())
            .step_by(2)
            .map(|i| u8::from_str_radix(&s[i..i + 2], 16).unwrap())
            .collect()
    }

    #[test]
    fn framing_goi_don() {
        let nonce: [u8; 8] = [0, 1, 2, 3, 4, 5, 6, 7];
        let init = build_init_packet(&nonce);
        assert_eq!(&init[0..4], b"\xff\xff\xff\xff");
        assert_eq!(init[4], CTAPHID_INIT | 0x80);
        assert_eq!(&init[5..7], b"\x00\x08");
        assert_eq!(&init[7..15], &nonce);
        assert_eq!(&init[15..], &vec![0u8; PACKET_SIZE - 15][..]);
        let ping = build_ping_packet(0x12345678, b"esp32-s3-ping-test").unwrap();
        assert_eq!(ping[4], CTAPHID_PING | 0x80);
        assert!(build_ping_packet(1, &[0u8; 58]).is_err());
    }

    #[test]
    fn cat_goi_noi_100_byte() {
        let data: Vec<u8> = (0..100u8).collect();
        let parts = fragment(0x01020304, CTAPHID_PING, &data).unwrap();
        assert_eq!(parts.len(), 2);
        assert_eq!(parts[0][4], CTAPHID_PING | 0x80);
        assert_eq!(&parts[0][5..7], &100u16.to_be_bytes());
        assert_eq!(&parts[1][0..4], &0x01020304u32.to_be_bytes());
        assert_eq!(parts[1][4], 0);
        let mut joined = parts[0][7..].to_vec();
        joined.extend_from_slice(&parts[1][5..5 + 43]);
        assert_eq!(joined, data);
    }

    #[test]
    fn boc_init_mau() {
        let mut sample: Vec<u8> = (0..8u8).collect();
        sample.extend_from_slice(&0xDEADBEEFu32.to_be_bytes());
        sample.extend_from_slice(&[2, 1, 0, 3, 0x05]);
        let parsed = parse_init_response(&sample).unwrap();
        assert_eq!(parsed.nonce, [0, 1, 2, 3, 4, 5, 6, 7]);
        assert_eq!(parsed.new_cid, 0xDEADBEEF);
        assert_eq!(parsed.version, 2);
        assert_eq!(parsed.capabilities, 0x05);
    }

    #[test]
    fn cbor_getinfo_mau_va_kieu_long() {
        let (info, rest) = cbor_decode(CANNED_GETINFO).unwrap();
        assert!(rest.is_empty());
        let Cbor::Map(pairs) = info else {
            panic!("GetInfo mẫu phải là map")
        };
        let get = |i: i128| {
            pairs
                .iter()
                .find(|(k, _)| *k == Cbor::Int(i))
                .unwrap()
                .1
                .clone()
        };
        assert_eq!(
            get(1),
            Cbor::Array(vec![
                Cbor::Text("U2F_V2".to_string()),
                Cbor::Text("FIDO_2_0".to_string())
            ])
        );
        assert_eq!(
            get(4),
            Cbor::Map(vec![(Cbor::Text("rk".to_string()), Cbor::Bool(true))])
        );
        assert_eq!(get(5), Cbor::Int(1024));
        let (nested, _) = cbor_decode(&hex("A2018202210243626974")).unwrap();
        assert_eq!(
            nested,
            Cbor::Map(vec![
                (Cbor::Int(1), Cbor::Array(vec![Cbor::Int(2), Cbor::Int(-2)])),
                (Cbor::Int(2), Cbor::Bytes(b"bit".to_vec())),
            ])
        );
        assert_eq!(cbor_decode(&hex("F5")).unwrap().0, Cbor::Bool(true));
        assert_eq!(cbor_decode(&hex("F4")).unwrap().0, Cbor::Bool(false));
        assert_eq!(cbor_decode(&hex("F6")).unwrap().0, Cbor::Null);
        assert!(cbor_decode(&hex("1904")).is_err()); // CBOR cụt
    }

    #[test]
    fn cbor_siet_moi_than_cut_va_long_sau() {
        // Vá NCKH-010: thân cụt (khai 5 byte, thực 2 byte) bị nuốt im ở bản Python.
        assert!(cbor_decode(&hex("450102")).is_err());
        assert!(cbor_decode(&hex("656162")).is_err());
        // Text không UTF-8 bị từ chối thay vì ném UnicodeDecodeError lạ.
        assert!(cbor_decode(&hex("62FFFF")).is_err());
        // Lồng quá sâu bị chặn thay vì RecursionError.
        let mut deep = vec![0x81u8; CBOR_MAX_DEPTH + 2];
        deep.push(0x00);
        assert!(cbor_decode(&deep).is_err());
        let mut ok = vec![0x81u8; 5];
        ok.push(0x00);
        assert!(cbor_decode(&ok).is_ok());
        // Map đếm nhiều hơn số byte còn lại.
        assert!(cbor_decode(&hex("A20102")).is_err());
    }

    #[test]
    fn hoi_thoai_dau_cuoi_voi_key_gia() {
        for with_rid in [true, false] {
            let mut dev = FakeDevice::new(with_rid);
            let nonce: [u8; 8] = [0, 1, 2, 3, 4, 5, 6, 7];
            send_msg(&mut dev, CID_BROADCAST, CTAPHID_INIT, &nonce).unwrap();
            let (_, cmd, data) = recv_msg(&mut dev, 2000).unwrap();
            assert_eq!(cmd, CTAPHID_INIT);
            let got = parse_init_response(&data).unwrap();
            assert_eq!(got.nonce, nonce);
            assert_eq!(got.new_cid, NEW_CID);
            let cid = got.new_cid;
            send_msg(&mut dev, cid, CTAPHID_PING, b"esp32-s3-ping-test").unwrap();
            let (_, cmd, echo) = recv_msg(&mut dev, 2000).unwrap();
            assert_eq!((cmd, echo), (CTAPHID_PING, b"esp32-s3-ping-test".to_vec()));
            let long: Vec<u8> = (0..100u8).collect();
            send_msg(&mut dev, cid, CTAPHID_PING, &long).unwrap();
            let (_, cmd, long_echo) = recv_msg(&mut dev, 2000).unwrap();
            assert_eq!((cmd, long_echo), (CTAPHID_PING, long));
            let info = ctap2_get_info(&mut dev, cid).unwrap();
            assert_eq!(
                info.get("versions"),
                Some(&Cbor::Array(vec![
                    Cbor::Text("U2F_V2".to_string()),
                    Cbor::Text("FIDO_2_0".to_string())
                ]))
            );
            assert_eq!(info.get("maxMsgSize"), Some(&Cbor::Int(1024)));
            send_msg(&mut dev, cid, 0x3E, b"").unwrap();
            assert_eq!(recv_msg(&mut dev, 2000), Err(Error::CtapHid(0x01)));
            assert_eq!(
                recv_msg(&mut FakeDevice::new(true), 2000),
                Err(Error::Timeout)
            );
        }
    }

    #[test]
    fn loc_thiet_bi_fido() {
        assert!(fido_matches(0xF1D0, 0x303A, 0x1001, None, None));
        assert!(!fido_matches(0x0001, 0x303A, 0x1001, None, None));
        assert!(fido_matches(0xF1D0, 0x303A, 0x1001, Some(0x303A), None));
        assert!(!fido_matches(0xF1D0, 0x303A, 0x1001, Some(0x046D), None));
    }
}
