//! sk-env: môi trường trừu tượng cho key FIDO2.
//!
//! Crate này định nghĩa các trait nhỏ mà lõi CTAP2 cần
//! (lưu trữ, sinh số ngẫu nhiên, đồng hồ, xác nhận hiện diện, HID),
//! cộng một [`FakeEnv`] chạy hoàn toàn trên RAM để test host.
//!
//! Mục đích: tách lõi logic khỏi phần cứng ESP32-S3, để test được
//! trên máy tính trước khi port sang firmware thật (xem `docs/PORTING.md`
//! và `firmware/s3-fido`).
//!
//! Thiết kế này mô phỏng lại ý tưởng của `opensk::env::Env`
//! (10 trait con: Rng, UserPresence, Persist, KeyStore, Write,
//! Customization, HidConnection, Clock, Crypto, Fingerprint),
//! nhưng rút gọn còn 5 mảnh đủ để khung host chạy được.

use std::collections::{HashMap, VecDeque};
use std::time::{Duration, Instant, SystemTime, UNIX_EPOCH};

// ---------------------------------------------------------------------------
// Các trait trừu tượng
// ---------------------------------------------------------------------------

/// Lưu trữ kiểu key-value bền vững (trên key thật là flash).
pub trait Storage {
    /// Đọc giá trị theo khóa, không có thì trả `None`.
    fn store_find(&self, khao: usize) -> Option<Vec<u8>>;
    /// Ghi đè giá trị cho khóa.
    fn store_insert(&mut self, khao: usize, giatri: &[u8]);
    /// Xóa khóa, khóa không có thì bỏ qua.
    fn store_remove(&mut self, khao: usize);
    /// Liệt kê mọi khóa đang có (để duyệt credential).
    fn store_keys(&self) -> Vec<usize>;
}

/// Nguồn số ngẫu nhiên cho key và token nhạy cảm.
pub trait SkRng {
    /// Đổ đầy `dich` bằng byte ngẫu nhiên.
    fn fill_bytes(&mut self, dich: &mut [u8]);

    /// Mảng 32 byte ngẫu nhiên (CTAP hay cần cỡ này).
    fn gen_uniform_u8x32(&mut self) -> [u8; 32] {
        let mut mang = [0u8; 32];
        self.fill_bytes(&mut mang);
        mang
    }
}

/// Đồng hồ tạo bộ định giờ hết hạn sau N mili-giây.
pub trait SkClock {
    /// Kiểu hẹn giờ của từng nền tảng.
    type Timer;

    /// Tạo hẹn giờ hết hạn sau `ms` mili-giây.
    fn make_timer(&mut self, ms: u64) -> Self::Timer;
    /// Kiểm tra hẹn giờ đã hết hạn chưa.
    fn is_elapsed(&self, hen_gio: &Self::Timer) -> bool;
}

/// Kết quả một lần chờ người dùng xác nhận hiện diện.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum PresenceOutcome {
    /// Người dùng nhấn nút đồng ý.
    Approved,
    /// Người dùng từ chối (hoặc bấm hủy).
    Declined,
    /// Hết giờ mà không có thao tác.
    Timeout,
}

/// Xác nhận hiện diện của người dùng (trên key thật là nút BOOT GPIO0).
pub trait SkPresence {
    /// Bắt đầu một lượt kiểm tra (bật LED chờ...).
    fn check_init(&mut self);
    /// Chờ quyết định của người dùng, hết `timeout_ms` thì [`PresenceOutcome::Timeout`].
    fn wait_with_timeout(&mut self, timeout_ms: u64) -> PresenceOutcome;
    /// Kết thúc lượt kiểm tra (tắt LED chờ...).
    fn check_complete(&mut self);
}

/// Kênh HID 64 byte mỗi gói (khớp `PACKET_SIZE = 64` của CTAPHID).
pub trait SkHid {
    /// Gói HID dài đúng 64 byte.
    const PACKET_SIZE: usize = 64;

    /// Gửi một gói 64 byte về host.
    fn hid_send(&mut self, goi: &[u8; 64]);
    /// Nhận một gói, hết `timeout_ms` thì trả `None`.
    fn hid_recv(&mut self, timeout_ms: u64) -> Option<[u8; 64]>;
}

/// Môi trường tổng hợp: gom 5 mảnh trên lại một chỗ.
///
/// Firmware thật sẽ cài đặt trait này bằng driver ESP32-S3,
/// còn test host dùng [`FakeEnv`] bên dưới.
pub trait SkEnv {
    type Storage: Storage;
    type Rng: SkRng;
    type Clock: SkClock;
    type Presence: SkPresence;
    type Hid: SkHid;

    fn storage(&mut self) -> &mut Self::Storage;
    fn rng(&mut self) -> &mut Self::Rng;
    fn clock(&mut self) -> &mut Self::Clock;
    fn presence(&mut self) -> &mut Self::Presence;
    fn hid(&mut self) -> &mut Self::Hid;
}

// ---------------------------------------------------------------------------
// Cài đặt giả trên RAM (FakeEnv)
// ---------------------------------------------------------------------------

/// Lưu trữ RAM bằng `HashMap`, mất dữ liệu khi tắt chương trình.
#[derive(Debug, Default)]
pub struct RamStorage {
    map: HashMap<usize, Vec<u8>>,
}

impl RamStorage {
    pub fn new() -> Self {
        Self::default()
    }
}

impl Storage for RamStorage {
    fn store_find(&self, khao: usize) -> Option<Vec<u8>> {
        self.map.get(&khao).cloned()
    }

    fn store_insert(&mut self, khao: usize, giatri: &[u8]) {
        self.map.insert(khao, giatri.to_vec());
    }

    fn store_remove(&mut self, khao: usize) {
        self.map.remove(&khao);
    }

    fn store_keys(&self) -> Vec<usize> {
        let mut khoa: Vec<usize> = self.map.keys().copied().collect();
        khoa.sort_unstable();
        khoa
    }
}

/// RNG giả bằng thuật toán xorshift64star.
///
/// Đủ cho test logic, KHÔNG dùng cho key thật
/// (key thật phải dùng RNG phần cứng của ESP32-S3).
#[derive(Debug, Clone)]
pub struct FakeRng {
    state: u64,
}

impl FakeRng {
    /// Tạo RNG với seed cho trước (để test lặp lại được).
    pub fn from_seed(seed: u64) -> Self {
        // Tránh state 0 vì xorshift sẽ kẹt mãi ở 0.
        let state = if seed == 0 {
            0x9E37_79B9_7F4A_7C15
        } else {
            seed
        };
        Self { state }
    }

    /// Tạo RNG với seed lấy từ đồng hồ hệ thống (mỗi lần chạy khác nhau).
    pub fn new() -> Self {
        let nanos = SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .map(|d| d.as_nanos() as u64)
            .unwrap_or(0x1234_5678);
        let pid = std::process::id() as u64;
        Self::from_seed(nanos ^ pid.wrapping_mul(0x9E37_79B9_7F4A_7C15))
    }

    /// Một bước xorshift64star, trả về u64 ngẫu nhiên.
    fn next_u64(&mut self) -> u64 {
        let mut x = self.state;
        x ^= x >> 12;
        x ^= x << 25;
        x ^= x >> 27;
        self.state = x;
        x.wrapping_mul(0x2545_F491_4F6C_DD1D)
    }
}

impl Default for FakeRng {
    fn default() -> Self {
        Self::new()
    }
}

impl SkRng for FakeRng {
    fn fill_bytes(&mut self, dich: &mut [u8]) {
        let mut i = 0;
        while i < dich.len() {
            let rand = self.next_u64().to_le_bytes();
            let lay = core::cmp::min(rand.len(), dich.len() - i);
            dich[i..i + lay].copy_from_slice(&rand[..lay]);
            i += lay;
        }
    }
}

/// Đồng hồ giả dùng `Instant` của máy host.
#[derive(Debug, Default)]
pub struct FakeClock {
    _rieng: (),
}

/// Hẹn giờ giả: chỉ lưu thời điểm hết hạn.
#[derive(Debug, Clone)]
pub struct FakeTimer {
    het_han: Instant,
}

impl FakeClock {
    pub fn new() -> Self {
        Self::default()
    }
}

impl SkClock for FakeClock {
    type Timer = FakeTimer;

    fn make_timer(&mut self, ms: u64) -> FakeTimer {
        FakeTimer {
            het_han: Instant::now() + Duration::from_millis(ms),
        }
    }

    fn is_elapsed(&self, hen_gio: &FakeTimer) -> bool {
        Instant::now() >= hen_gio.het_han
    }
}

/// Xác nhận hiện diện giả: test nạp sẵn quyết định vào hàng đợi.
#[derive(Debug, Default)]
pub struct FakePresence {
    hang_doi: VecDeque<bool>,
    dang_kiem_tra: bool,
}

impl FakePresence {
    pub fn new() -> Self {
        Self::default()
    }

    /// Nạp một quyết định vào hàng đợi (`true` = đồng ý, `false` = từ chối).
    pub fn push_decision(&mut self, dong_y: bool) {
        self.hang_doi.push_back(dong_y);
    }

    /// Xem còn bao nhiêu quyết định chưa dùng (để test kiểm tra).
    pub fn pending_count(&self) -> usize {
        self.hang_doi.len()
    }
}

impl SkPresence for FakePresence {
    fn check_init(&mut self) {
        self.dang_kiem_tra = true;
    }

    fn wait_with_timeout(&mut self, _timeout_ms: u64) -> PresenceOutcome {
        // Bản giả không chờ thật: có quyết định nạp sẵn thì lấy,
        // không có thì coi như hết giờ.
        match self.hang_doi.pop_front() {
            Some(true) => PresenceOutcome::Approved,
            Some(false) => PresenceOutcome::Declined,
            None => PresenceOutcome::Timeout,
        }
    }

    fn check_complete(&mut self) {
        self.dang_kiem_tra = false;
    }
}

/// HID giả: ghi log mọi gói gửi, hàng đợi cho gói nhận.
#[derive(Debug, Default)]
pub struct FakeHid {
    /// Log các gói đã gửi về host (theo thứ tự).
    da_gui: Vec<[u8; 64]>,
    /// Hàng đợi gói giả lập host gửi xuống.
    den: VecDeque<[u8; 64]>,
}

impl FakeHid {
    pub fn new() -> Self {
        Self::default()
    }

    /// Giả lập host gửi một gói xuống key (để test `hid_recv`).
    pub fn inject_incoming(&mut self, goi: [u8; 64]) {
        self.den.push_back(goi);
    }

    /// Đọc log các gói đã gửi (để test đối chiếu từng byte).
    pub fn sent_log(&self) -> &[[u8; 64]] {
        &self.da_gui
    }
}

impl SkHid for FakeHid {
    fn hid_send(&mut self, goi: &[u8; 64]) {
        self.da_gui.push(*goi);
    }

    fn hid_recv(&mut self, _timeout_ms: u64) -> Option<[u8; 64]> {
        self.den.pop_front()
    }
}

/// Môi trường giả đầy đủ trên RAM, dùng cho test host.
#[derive(Debug, Default)]
pub struct FakeEnv {
    storage: RamStorage,
    rng: FakeRng,
    clock: FakeClock,
    presence: FakePresence,
    hid: FakeHid,
}

impl FakeEnv {
    pub fn new() -> Self {
        Self {
            storage: RamStorage::new(),
            rng: FakeRng::new(),
            clock: FakeClock::new(),
            presence: FakePresence::new(),
            hid: FakeHid::new(),
        }
    }

    /// Tạo môi trường với seed RNG cố định (test lặp lại được).
    pub fn with_seed(seed: u64) -> Self {
        let mut env = Self::new();
        env.rng = FakeRng::from_seed(seed);
        env
    }
}

impl SkEnv for FakeEnv {
    type Storage = RamStorage;
    type Rng = FakeRng;
    type Clock = FakeClock;
    type Presence = FakePresence;
    type Hid = FakeHid;

    fn storage(&mut self) -> &mut RamStorage {
        &mut self.storage
    }
    fn rng(&mut self) -> &mut FakeRng {
        &mut self.rng
    }
    fn clock(&mut self) -> &mut FakeClock {
        &mut self.clock
    }
    fn presence(&mut self) -> &mut FakePresence {
        &mut self.presence
    }
    fn hid(&mut self) -> &mut FakeHid {
        &mut self.hid
    }
}

// ---------------------------------------------------------------------------
// Unit test
// ---------------------------------------------------------------------------

#[cfg(test)]
mod tests {
    use super::*;

    /// Test 1: ghi/đọc/xóa storage.
    #[test]
    fn storage_ghi_doc_xoa() {
        let mut env = FakeEnv::new();
        let kho = env.storage();

        // Chưa ghi thì đọc ra None.
        assert_eq!(kho.store_find(1), None);

        // Ghi rồi đọc lại đúng từng byte.
        kho.store_insert(1, &[10, 20, 30]);
        assert_eq!(kho.store_find(1), Some(vec![10, 20, 30]));

        // Ghi đè khóa cũ.
        kho.store_insert(1, &[99]);
        assert_eq!(kho.store_find(1), Some(vec![99]));

        // Ghi thêm khóa khác, liệt kê đủ cả hai.
        kho.store_insert(7, b"khoa-phu");
        assert_eq!(kho.store_keys(), vec![1, 7]);

        // Xóa thì mất, xóa khóa không có cũng không lỗi.
        kho.store_remove(1);
        assert_eq!(kho.store_find(1), None);
        kho.store_remove(999);
        assert_eq!(kho.store_keys(), vec![7]);
    }

    /// Test 2: hai lần sinh RNG phải khác nhau, và seed cố định lặp lại được.
    #[test]
    fn rng_hai_lan_khac_nhau() {
        let mut env = FakeEnv::new();
        let a = env.rng().gen_uniform_u8x32();
        let b = env.rng().gen_uniform_u8x32();
        assert_ne!(a, b, "hai lần sinh liên tiếp không được trùng nhau");

        let mut buf = [0u8; 100];
        env.rng().fill_bytes(&mut buf);
        // 100 byte ngẫu nhiên không thể toàn 0.
        assert!(buf.iter().any(|&x| x != 0));

        // Cùng seed thì dãy đầu tiên giống nhau (để test lặp lại).
        let mut r1 = FakeRng::from_seed(42);
        let mut r2 = FakeRng::from_seed(42);
        assert_eq!(r1.gen_uniform_u8x32(), r2.gen_uniform_u8x32());
    }

    /// Test 3: hàng đợi presence (đồng ý / từ chối / hết giờ).
    #[test]
    fn presence_hang_doi() {
        let mut env = FakeEnv::new();

        // Chưa nạp quyết định thì hết giờ.
        env.presence().check_init();
        assert_eq!(
            env.presence().wait_with_timeout(1000),
            PresenceOutcome::Timeout
        );
        env.presence().check_complete();

        // Nạp hai quyết định, lấy ra đúng thứ tự.
        env.presence().push_decision(true);
        env.presence().push_decision(false);
        assert_eq!(env.presence().pending_count(), 2);

        env.presence().check_init();
        assert_eq!(
            env.presence().wait_with_timeout(1000),
            PresenceOutcome::Approved
        );
        assert_eq!(
            env.presence().wait_with_timeout(1000),
            PresenceOutcome::Declined
        );
        // Hết hàng đợi thì lại hết giờ.
        assert_eq!(
            env.presence().wait_with_timeout(1000),
            PresenceOutcome::Timeout
        );
        env.presence().check_complete();
        assert_eq!(env.presence().pending_count(), 0);
    }

    /// Test 4: log gói HID gửi/nhận.
    #[test]
    fn hid_log_goi() {
        let mut env = FakeEnv::new();

        // Chưa có gói đến thì nhận ra None.
        assert_eq!(env.hid().hid_recv(100), None);

        // Giả lập host gửi gói 64 byte, key nhận đúng từng byte.
        let mut vao = [0u8; 64];
        vao[0..4].copy_from_slice(&[1, 2, 3, 4]);
        env.hid().inject_incoming(vao);
        assert_eq!(env.hid().hid_recv(100), Some(vao));

        // Key gửi hai gói, log giữ đúng thứ tự và nội dung.
        let mut ra1 = [0u8; 64];
        ra1[4] = 0x86; // ví dụ byte lệnh CTAPHID_INIT trả về
        let mut ra2 = [0u8; 64];
        ra2[0] = 0xFF;
        env.hid().hid_send(&ra1);
        env.hid().hid_send(&ra2);
        assert_eq!(env.hid().sent_log(), &[ra1, ra2]);
    }

    /// Test phụ: đồng hồ hết hạn đúng (0ms hết ngay, 1 giờ thì chưa).
    #[test]
    fn clock_het_han() {
        let mut env = FakeEnv::new();
        let ngay = env.clock().make_timer(0);
        assert!(env.clock().is_elapsed(&ngay));
        let lau = env.clock().make_timer(3_600_000);
        assert!(!env.clock().is_elapsed(&lau));
    }
}
