//! nd-gen: cong cu sinh dataset .ndd tu dong lenh.
//!
//! Vi du:
//!     nd-gen --rounds 5 --samples 1000 --seed 1 --out train-R5.ndd

use std::path::PathBuf;
use std::time::Instant;

use clap::Parser;
use nd_data::{ghi_ndd, tao_dataset, FULL_ROUNDS};

/// Sinh dataset distinguisher kieu Gohr ra file .ndd.
#[derive(Parser, Debug)]
#[command(
    name = "nd-gen",
    version,
    about = "Sinh dataset .ndd (Speck32/64, seeded, xac dinh)"
)]
struct Cli {
    /// So vong Speck (1..=22).
    #[arg(long, default_value_t = 5)]
    rounds: u16,

    /// So mau can sinh.
    #[arg(long, default_value_t = 1000)]
    samples: usize,

    /// Seed RNG (ChaCha8).
    #[arg(long, default_value_t = 1)]
    seed: u64,

    /// Duong dan file .ndd dau ra.
    #[arg(long)]
    out: PathBuf,
}

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let cli = Cli::parse();
    if !(1..=(FULL_ROUNDS as u16)).contains(&cli.rounds) {
        return Err(format!("so vong phai trong [1, {FULL_ROUNDS}], nhan {}", cli.rounds).into());
    }
    if cli.samples == 0 {
        return Err("so mau phai > 0".into());
    }
    let bat_dau = Instant::now();
    let mau = tao_dataset(cli.rounds as usize, cli.samples, cli.seed);
    ghi_ndd(&cli.out, cli.rounds, cli.seed, &mau)?;
    let so_1 = mau.iter().filter(|m| m.nhan == 1).count();
    println!(
        "Da ghi {} mau ({} nhan 1, {} nhan 0) R={} seed={} -> {} ({:.2}s)",
        mau.len(),
        so_1,
        mau.len() - so_1,
        cli.rounds,
        cli.seed,
        cli.out.display(),
        bat_dau.elapsed().as_secs_f32()
    );
    Ok(())
}
