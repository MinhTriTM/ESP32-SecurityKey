//! s3-fido: KHUNG firmware key FIDO2 cho ESP32-S3 (mẫu, chưa build được).
//!
//! File này chỉ phác thảo cấu trúc: khởi tạo ngoại vi, định nghĩa `S3Env`
//! cài đặt `opensk::env::Env`, và vòng lặp chính. Mọi hàm đều là `todo!()`.
//!
//! TRUNG THỰC: file chưa từng được biên dịch (máy dev chưa có toolchain
//! Xtensa). Tên module/hàm của `esp-hal` dưới đây suy từ tài liệu esp-hal 1.2
//! và có thể lệch; khi port thật phải đối chiếu docs.rs/esp-hal rồi sửa.
//! Cách build xem `README.md` cạnh file này.

#![no_std]
#![no_main]

// TODO(port): kiểm tra lại từng đường import theo docs esp-hal 1.2 khi có toolchain.
use esp_hal::gpio::{Input, InputConfig, Pull};
use esp_hal::rng::Rng as HalRng;
use esp_hal::timer::timg::TimerGroup;
use opensk::api::clock::Clock;
use opensk::api::connection::{HidConnection, RecvStatus, UsbEndpoint};
use opensk::api::crypto::Crypto;
use opensk::api::customization::Customization;
#[cfg(feature = "opensk-fingerprint")]
use opensk::api::fingerprint::Fingerprint;
use opensk::api::key_store::KeyStore;
use opensk::api::persist::Persist;
use opensk::api::rng::Rng as _;
use opensk::api::user_presence::{UserPresence, UserPresenceWaitResult};
use opensk::ctap::Channel;
use opensk::env::Env;
use opensk::Ctap;

// ---------------------------------------------------------------------------
// Chân cẳng (theo hardware/wiring.md và firmware/hwtest của repo mẹ)
// ---------------------------------------------------------------------------

/// Nút BOOT: GPIO0, nhấn kéo xuống GND (dùng `INPUT_PULLUP`).
const BOOT_PIN_NUM: u8 = 0;
/// LED WS2812 trên DevKit v1.
const LED_V1_PIN_NUM: u8 = 38;
/// LED WS2812 trên DevKit v2.
const LED_V2_PIN_NUM: u8 = 48;
/// USB OTG native D-.
const USB_DM_PIN_NUM: u8 = 19;
/// USB OTG native D+.
const USB_DP_PIN_NUM: u8 = 20;

// ---------------------------------------------------------------------------
// Điểm vào firmware
// ---------------------------------------------------------------------------

#[esp_hal::main]
fn main() -> ! {
    // TODO(port): khởi tạo HAL + clock theo mẫu esp-generate cho ESP32-S3.
    // Ví dụ ý tưởng (kiểm tra lại tên API):
    //   let peripherals = esp_hal::init(esp_hal::Config::default());
    //   let timg0 = TimerGroup::new(peripherals.TIMG0);
    let _ = (BOOT_PIN_NUM, LED_V1_PIN_NUM, LED_V2_PIN_NUM);
    let _ = (USB_DM_PIN_NUM, USB_DP_PIN_NUM);

    // TODO(port): dựng S3Env từ ngoại vi thật (rng, flash, nút BOOT...).
    // let mut env = S3Env::new(...);
    // let mut ctap = Ctap::new(&mut env);

    // TODO(port): vòng lặp USB: nhận gói 64 byte -> ctap.process_packet -> gửi về.
    loop {
        todo!("vong lap USB HID chinh (xem docs/PORTING.md muc HidConnection)")
    }
}

// ---------------------------------------------------------------------------
// S3Env: môi trường opensk cho ESP32-S3
// ---------------------------------------------------------------------------

/// Môi trường opensk chạy trên ESP32-S3.
///
/// Mỗi trường là một driver cài đặt trait con của opensk.
/// Xem ánh xạ chi tiết ở `docs/PORTING.md` của repo này.
pub struct S3Env {
    // TODO(port): thêm field driver thật, ví dụ:
    // rng: S3Rng,
    // presence: S3Presence,
    // persist: S3Persist,
    // ...
}

impl Env for S3Env {
    type Rng = S3Rng;
    type UserPresence = S3Presence;
    type Persist = S3Persist;
    type KeyStore = S3KeyStore;
    type Write = S3Write;
    type Customization = S3Customization;
    type HidConnection = S3Hid;
    type Clock = S3Clock;
    type Crypto = S3Crypto;
    #[cfg(feature = "opensk-fingerprint")]
    type Fingerprint = S3Fingerprint;

    fn rng(&mut self) -> &mut Self::Rng {
        todo!("tra ve driver RNG phan cung (esp_hal::rng::Rng)")
    }

    fn user_presence(&mut self) -> &mut Self::UserPresence {
        todo!("tra ve driver nut BOOT GPIO0 + LED bao hieu")
    }

    fn persist(&mut self) -> &mut Self::Persist {
        todo!("tra ve driver key-value tren flash (esp-storage)")
    }

    fn key_store(&mut self) -> &mut Self::KeyStore {
        todo!("tra ve kho khoa (mac dinh dung Helper cua opensk neu duoc)")
    }

    fn clock(&mut self) -> &mut Self::Clock {
        todo!("tra ve dong ho (timer group cua esp-hal)")
    }

    #[cfg(feature = "opensk-fingerprint")]
    fn fingerprint(&mut self) -> &mut Self::Fingerprint {
        todo!("board khong co cam bien van tay: tra stub bao loi hoac tat feature")
    }

    fn write(&mut self) -> Self::Write {
        todo!("tra ve writer log qua USB-Serial-JTAG (esp-println)")
    }

    fn customization(&self) -> &Self::Customization {
        todo!("tra ve cau hinh hang (so key, do dai PIN, attestation...)")
    }

    fn hid_connection(&mut self) -> &mut Self::HidConnection {
        todo!("tra ve ket noi USB OTG HID 64 byte (RUI RO LON NHAT, xem PORTING.md)")
    }

    fn boots_after_soft_reset(&self) -> bool {
        todo!("doc ly do reset tu RTC/efuse: true neu la soft reset")
    }

    fn firmware_version(&self) -> Option<u64> {
        // TODO(port): trả bản firmware để hiện trong GetInfo.
        Some(1)
    }

    fn process_vendor_command(&mut self, _bytes: &[u8], _channel: Channel) -> Option<alloc::vec::Vec<u8>> {
        // Không có lệnh vendor riêng: trả None để opensk xử lý chuẩn.
        None
    }
}

// ---------------------------------------------------------------------------
// Từng driver con (khung, mỗi hàm một TODO)
// ---------------------------------------------------------------------------

/// RNG phần cứng của ESP32-S3.
pub struct S3Rng {
    // TODO(port): giữ `esp_hal::rng::Rng` ở đây.
    _giugin: (),
}

impl rand_core::RngCore for S3Rng {
    fn next_u32(&mut self) -> u32 {
        todo!("doc 4 byte tu RNG phan cung")
    }
    fn next_u64(&mut self) -> u64 {
        todo!("doc 8 byte tu RNG phan cung")
    }
    fn fill_bytes(&mut self, _dest: &mut [u8]) {
        todo!("do day dest bang RNG phan cung")
    }
    fn try_fill_bytes(&mut self, _dest: &mut [u8]) -> Result<(), rand_core::Error> {
        todo!("nhu fill_bytes nhung tra Result")
    }
}

impl rand_core::CryptoRng for S3Rng {}

impl opensk::api::rng::Rng for S3Rng {
    // Dùng `gen_uniform_u8x32` mặc định của opensk.
}

/// Xác nhận hiện diện bằng nút BOOT (GPIO0) + LED WS2812.
pub struct S3Presence {
    // TODO(port): giữ `Input` cho GPIO0 và driver RMT cho LED ở đây.
    _giugin: (),
}

impl UserPresence for S3Presence {
    fn check_init(&mut self) {
        todo!("bat LED bao dang cho nguoi dung nhan nut")
    }

    fn wait_with_timeout(
        &mut self,
        _packet: &mut [u8; 64],
        _timeout_ms: usize,
    ) -> UserPresenceWaitResult {
        todo!("doi nut BOOT, vua doi vua nhan goi USB de khong ket noi")
    }

    fn check_complete(&mut self) {
        todo!("tat LED bao cho, tro ve mau san sang")
    }
}

/// Lưu trữ key-value bền vững trên flash trong.
pub struct S3Persist {
    // TODO(port): giữ `esp_storage::FlashStorage` + bang key-value ở đây.
    _giugin: (),
}

impl Persist for S3Persist {
    fn find(&self, _key: usize) -> opensk::ctap::status_code::CtapResult<Option<alloc::vec::Vec<u8>>> {
        todo!("doc value theo key tu flash")
    }

    fn insert(&mut self, _key: usize, _value: &[u8]) -> opensk::ctap::status_code::CtapResult<()> {
        todo!("ghi value vao flash (can wear-leveling, xem PORTING.md)")
    }

    fn remove(&mut self, _key: usize) -> opensk::ctap::status_code::CtapResult<()> {
        todo!("xoa key khoi flash")
    }

    fn iter(&self) -> opensk::ctap::status_code::CtapResult<opensk::api::persist::PersistIter<'_>> {
        todo!("duyet moi key dang co")
    }
    // Các hàm còn lại (bộ đếm ký, PIN, large blob...) dùng bản mặc
    // định của opensk xây trên 4 hàm trên, trừ khi cần tối ưu riêng.
}

/// Kho khóa: bọc/mở credential, giữ PIN.
pub struct S3KeyStore {
    // TODO(port): xem opensk có cho dùng `Helper` mặc định không;
    // nếu có thì không cần struct riêng, `type KeyStore = S3Env` kiểu helper.
    _giugin: (),
}

impl KeyStore for S3KeyStore {
    fn init(&mut self) -> Result<(), opensk::api::key_store::Error> {
        todo!("khoi tao kho khoa lan dau (sinh master key...)")
    }

    fn wrap_credential(
        &mut self,
        _credential: opensk::api::key_store::CredentialSource,
    ) -> Result<alloc::vec::Vec<u8>, opensk::api::key_store::Error> {
        todo!("ma hoa credential thanh credential ID 241 byte")
    }

    fn unwrap_credential(
        &mut self,
        _bytes: &[u8],
        _rp_id_hash: &[u8],
    ) -> Result<Option<opensk::api::key_store::CredentialSource>, opensk::api::key_store::Error> {
        todo!("giai ma va kiem tra credential ID")
    }

    fn cred_random(&mut self, _has_uv: bool) -> Result<opensk::ctap::secret::Secret<[u8; 32]>, opensk::api::key_store::Error> {
        todo!("tra ve CredRandom theo trang thai UV")
    }

    fn has_pin(&mut self) -> opensk::ctap::status_code::CtapResult<bool> {
        todo!("kiem tra da dat PIN chua")
    }

    fn verify_pin_hash(&mut self, _candidate: &[u8; 16]) -> opensk::ctap::status_code::CtapResult<bool> {
        todo!("so sanh PIN hash bang cach khong ro ri thoi gian")
    }

    fn store_pin(&mut self, _pin_hash: &[u8; 16], _code_point_length: u8) -> opensk::ctap::status_code::CtapResult<()> {
        todo!("luu PIN hash + do dai PIN")
    }

    fn reset(&mut self) -> Result<(), opensk::api::key_store::Error> {
        todo!("xoa sach khoa khi CTAP reset")
    }
}

/// Ghi log debug qua USB-Serial-JTAG.
pub struct S3Write {
    // TODO(port): bọc `esp_println::Printer`.
    _giugin: (),
}

impl core::fmt::Write for S3Write {
    fn write_str(&mut self, _s: &str) -> core::fmt::Result {
        todo!("in chuoi log ra USB-Serial-JTAG")
    }
}

/// Cấu hình hãng: giới hạn key, PIN, attestation...
pub struct S3Customization {
    // TODO(port): các hằng riêng của key này.
    _giugin: (),
}

impl Customization for S3Customization {
    fn allows_pin_protocol_v1(&self) -> bool {
        todo!("true neu muon ho tro PIN protocol v1 (cu)")
    }
    fn default_cred_protect(&self) -> Option<opensk::ctap::data_formats::CredentialProtectionPolicy> {
        todo!("muc credProtect mac dinh (khuyen nghị None de de dung)")
    }
    fn default_min_pin_length(&self) -> u8 {
        // TODO(port): PIN tối thiểu, ít nhất 4, NIST khuyên 6.
        6
    }
    fn default_min_pin_length_rp_ids(&self) -> alloc::vec::Vec<alloc::string::String> {
        todo!("danh sach RP duoc doc minPinLength")
    }
    fn enforce_always_uv(&self) -> bool {
        // TODO(port): true nếu muốn bắt buộc PIN cho mọi lệnh.
        false
    }
    fn enterprise_attestation_mode(
        &self,
    ) -> Option<opensk::ctap::data_formats::EnterpriseAttestationMode> {
        // TODO(port): None = tắt enterprise attestation (riêng tư nhất).
        None
    }
    fn is_enterprise_rp_id(&self, _rp_id: &str) -> bool {
        false
    }
    fn max_msg_size(&self) -> usize {
        // TODO(port): 1024 là mặc định an toàn, tối đa 7609.
        1024
    }
    fn max_pin_retries(&self) -> u8 {
        // CTAP2 bắt tối đa 8 lần.
        8
    }
    fn use_batch_attestation(&self) -> bool {
        // TODO(port): true chỉ khi đã có hạ tầng chứng chỉ lô >= 100k key.
        false
    }
    fn use_signature_counter(&self) -> bool {
        true
    }
    fn max_cred_blob_length(&self) -> usize {
        32
    }
    fn max_credential_count_in_list(&self) -> Option<usize> {
        // TODO(port): giới hạn theo RAM còn lại.
        Some(8)
    }
    fn max_rp_ids_length(&self) -> usize {
        8
    }
    fn max_supported_resident_keys(&self) -> usize {
        // TODO(port): tính theo công thức flash ở docs opensk (P, K, S, C, I).
        25
    }
}

/// Kết nối USB OTG HID: gửi/nhận gói 64 byte. RỦI RO LỚN NHẤT của port.
pub struct S3Hid {
    // TODO(port): giữ driver USB OTG (xem PORTING.md: embassy-usb +
    // synopsys-otg, hoac stack HID tu viet tren thanh ghi OTG).
    _giugin: (),
}

impl HidConnection for S3Hid {
    fn send(&mut self, _buf: &[u8; 64], _endpoint: UsbEndpoint) -> opensk::ctap::status_code::CtapResult<()> {
        todo!("gui mot goi HID 64 byte ve host qua endpoint MainHid")
    }

    fn recv(&mut self, _buf: &mut [u8; 64], _timeout_ms: usize) -> opensk::ctap::status_code::CtapResult<RecvStatus> {
        todo!("nhan mot goi HID 64 byte, het gio thi tra RecvStatus::Timeout")
    }
}

/// Đồng hồ và hẹn giờ của key.
pub struct S3Clock {
    // TODO(port): giữ timer phần cứng (TimerGroup) ở đây.
    _giugin: (),
}

/// Hẹn giờ S3: mốc hết hạn tính bằng mili-giây từ lúc boot.
pub struct S3Timer {
    // TODO(port): lưu deadline theo tick timer phần cứng.
    _giugin: (),
}

impl Default for S3Timer {
    fn default() -> Self {
        // Hẹn giờ mặc định phải coi như đã hết hạn (theo docs opensk).
        todo!("tra ve timer da het han ngay")
    }
}

impl Clock for S3Clock {
    type Timer = S3Timer;

    fn make_timer(&mut self, _milliseconds: usize) -> S3Timer {
        todo!("tao hen gio het han sau N ms")
    }

    fn is_elapsed(&mut self, _timer: &S3Timer) -> bool {
        todo!("kiem tra hen gio da het han chua")
    }
}

/// Gom các thuật toán mật mã key cần (AES, ECDH, ECDSA, SHA, HMAC, HKDF).
pub struct S3Crypto {
    _giugin: (),
}

impl Crypto for S3Crypto {
    // TODO(port): chọn từng kiểu: ưu tiên tăng tốc phần cứng của S3
    // (AES/SHA/RSA/ECC) qua esp-hal, phần còn lại dùng RustCrypto trong
    // `software_crypto` của opensk. Xem bảng ở docs/PORTING.md.
    type Aes256 = opensk::api::crypto::software_crypto::SoftwareAes256;
    type Ecdh = opensk::api::crypto::software_crypto::SoftwareEcdhSecretKey;
    type Ecdsa = opensk::api::crypto::software_crypto::SoftwareEcdsaSecretKey;
    type Sha256 = opensk::api::crypto::software_crypto::SoftwareSha256;
    type Hmac256 = opensk::api::crypto::software_crypto::SoftwareHmac256;
    type Hkdf256 = opensk::api::crypto::software_crypto::SoftwareHkdf256;
}

/// Vân tay: board không có cảm biến nên chỉ là stub báo lỗi.
#[cfg(feature = "opensk-fingerprint")]
pub struct S3Fingerprint {
    _giugin: (),
}

#[cfg(feature = "opensk-fingerprint")]
impl Fingerprint for S3Fingerprint {
    fn prepare_enrollment(&mut self) -> opensk::ctap::status_code::CtapResult<()> {
        todo!("board khong co van tay: tra loi hoac tat feature fingerprint")
    }
    fn capture_sample(
        &mut self,
        _timeout_ms: Option<usize>,
    ) -> opensk::ctap::status_code::CtapResult<(
        opensk::api::fingerprint::Ctap2EnrollFeedback,
        usize,
        Option<alloc::vec::Vec<u8>>,
    )> {
        todo!("board khong co van tay")
    }
    fn cancel_enrollment(&mut self) -> opensk::ctap::status_code::CtapResult<()> {
        todo!("board khong co van tay")
    }
    fn remove_enrollment(&mut self, _template_id: &[u8]) -> opensk::ctap::status_code::CtapResult<()> {
        todo!("board khong co van tay")
    }
    fn check_fingerprint_init(&mut self) -> opensk::ctap::status_code::CtapResult<()> {
        todo!("board khong co van tay")
    }
    fn check_fingerprint(
        &mut self,
        _timeout_ms: usize,
    ) -> Result<(), opensk::api::fingerprint::FingerprintCheckError> {
        todo!("board khong co van tay")
    }
    fn check_fingerprint_complete(&mut self) -> opensk::ctap::status_code::CtapResult<()> {
        todo!("board khong co van tay")
    }
    fn fingerprint_kind(&self) -> opensk::api::fingerprint::FingerprintKind {
        todo!("board khong co van tay")
    }
    fn max_capture_samples_required_for_enroll(&self) -> usize {
        todo!("board khong co van tay")
    }
}

// Cần allocator cho opensk (`alloc::vec`, `alloc::string`).
// TODO(port): thêm esp-alloc với heap trong PSRAM 8MB khi build thật.
#[allow(dead_code)]
fn _can_allocator() {
    todo!("khoi tao esp-alloc truoc khi dung opensk")
}
