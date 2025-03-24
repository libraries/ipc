#![no_main]
#![no_std]

use alloc::string::{String, ToString};
use alloc::vec::Vec;
use ckb_std::ckb_types::prelude::Entity;

ckb_std::entry!(main);
ckb_std::default_alloc!();

#[ckb_script_ipc::service]
pub trait IpcTest {
    fn math_add(a: u64, b: u64) -> u64;
    fn spawn(s: String) -> String;
    fn syscall_load_script() -> Vec<u8>;
}

struct IpcTestServer {}

impl IpcTest for IpcTestServer {
    fn math_add(&mut self, a: u64, b: u64) -> u64 {
        a.checked_add(b).unwrap()
    }

    fn spawn(&mut self, s: String) -> String {
        let argc: u64 = 0;
        let argv = [];
        let mut std_fds: [u64; 2] = [0, 0];
        let mut son_fds: [u64; 3] = [0, 0, 0];
        let (r, w) = ckb_std::syscalls::pipe().unwrap();
        std_fds[0] = r;
        son_fds[1] = w;
        let (r, w) = ckb_std::syscalls::pipe().unwrap();
        std_fds[1] = w;
        son_fds[0] = r;
        let mut pid: u64 = 0;
        let mut spgs = ckb_std::syscalls::SpawnArgs {
            argc,
            argv: argv.as_ptr() as *const *const i8,
            process_id: &mut pid as *mut u64,
            inherited_fds: son_fds.as_ptr(),
        };
        ckb_std::syscalls::spawn(2, ckb_std::ckb_constants::Source::CellDep, 0, 0, &mut spgs)
            .unwrap();
        ckb_std::syscalls::write(std_fds[1], s.as_bytes()).unwrap();
        ckb_std::syscalls::close(std_fds[1]).unwrap();
        let mut buf = [0; 256];
        let buf_len = ckb_std::syscalls::read(std_fds[0], &mut buf).unwrap();
        String::from_utf8_lossy(&buf[..buf_len]).to_string()
    }

    fn syscall_load_script(&mut self) -> Vec<u8> {
        ckb_std::high_level::load_script()
            .unwrap()
            .as_bytes()
            .into()
    }
}

fn main() -> i8 {
    ckb_script_ipc_common::spawn::run_server(IpcTestServer {}.server()).unwrap();
    return 0;
}
