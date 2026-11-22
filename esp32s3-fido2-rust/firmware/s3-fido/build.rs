// Build script tối thiểu cho firmware mẫu.
//
// Khi build thật bằng espup, script này sẽ được thay bằng cấu hình
// chuẩn của template esp-generate (linker script, esp-config...).
// Hiện tại chỉ in target để dễ thấy log, KHÔNG can thiệp link.

fn main() {
    println!("cargo:rerun-if-changed=build.rs");
    // TODO(port): khi có toolchain Xtensa, thêm cấu hình link theo
    // template esp-generate cho ESP32-S3 (linkall.x, rom_coexist...).
}
