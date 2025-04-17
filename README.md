# CKB IPC Test Suite

## Usage

```sh
$ pip install pyckb

# Local ckb node
$ python ipc_manage/main.py ckb_init
$ python ipc_manage/main.py ckb_pm_c

# Build and deploy
$ python ipc_manage/main.py ipc_test_build
$ python ipc_manage/main.py ipc_test_deploy

# Test
$ python ipc_manage/main.py ipc_test_call_math_add
$ python ipc_manage/main.py ipc_test_call_math_add_with_exec
$ python ipc_manage/main.py ipc_test_call_math_add_with_hex
$ python ipc_manage/main.py ipc_test_call_math_add_with_spawn
$ python ipc_manage/main.py ipc_test_call_math_add_with_type_id_args
$ python ipc_manage/main.py ipc_test_call_string_len
$ python ipc_manage/main.py ipc_test_call_syscall_load_script
$ python ipc_manage/main.py ipc_test_call_syscall_load_script_with_env
```
