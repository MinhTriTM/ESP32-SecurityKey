//! Script build: nối linker script của esp-hal (linkall.x).

fn main() {
    println!("cargo:rustc-link-arg=-Tlinkall.x");
    // Một số chip cần thêm hàm ROM:
    // println!("cargo:rustc-link-arg=-Trom_functions.x");
}
