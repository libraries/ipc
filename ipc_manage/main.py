import argparse
import itertools
import lib.acdb
import json
import os
import pathlib
import pyckb
import subprocess

ckb_root = '/home/ubuntu/src/ckb'
ipc_root = os.path.dirname(os.path.dirname(__file__))
ckb = f'{ckb_root}/target/debug/ckb'
parser = argparse.ArgumentParser()
parser.add_argument('cmd', nargs='+')
args = parser.parse_args()
acdb = lib.acdb.Emerge(lib.acdb.MapDriver(f'{ipc_root}/res'))


def ckb_build():
    os.chdir(f'{ckb_root}')
    subprocess.run('cargo build', shell=True)


def ckb_init():
    os.chdir(f'{ipc_root}/devnet')
    subprocess.run(
        f'{ckb} init --chain dev --ba-arg 0x75178f34549c5fe9cd1a0c57aebd01e7ddf9249e --ba-message 0xabcd', shell=True)


def ckb_pm_c():
    os.chdir(f'{ipc_root}/devnet')
    env = os.environ.copy()
    env['PMNAME'] = 'ckbr'
    subprocess.run(f'pm c {ckb} run --indexer', env=env, shell=True)
    env['PMNAME'] = 'ckbm'
    subprocess.run(f'pm c {ckb} miner', env=env, shell=True)


def ckb_pm_k():
    subprocess.run('pm k ckbm ckbr', shell=True)


def ipc_test_build():
    os.chdir(f'{ipc_root}/ipc_test')
    subprocess.run('cargo build --release', shell=True)


def ipc_test_call_infinite_loop():
    pyckb.config.upgrade('http://127.0.0.1:8114')
    pyckb.config.current = pyckb.config.develop
    ipc_script_locator = {
        'out_point': acdb['ipc_test']['out_point'],
    }
    ipc_req = {
        'version': '0x0',
        'method_id': '0x0',
        'payload_format': 'json',
        'payload': {
            'InfiniteLoop': {},
        },
    }
    ipc_ret = pyckb.rpc.call('ipc_call', [ipc_script_locator, ipc_req])
    print(f'main: call result json={ipc_ret}')


def ipc_test_call_math_add():
    pyckb.config.upgrade('http://127.0.0.1:8114')
    pyckb.config.current = pyckb.config.develop
    ipc_script_locator = {
        'out_point': acdb['ipc_test']['out_point'],
    }
    ipc_req = {
        'version': '0x0',
        'method_id': '0x0',
        'payload_format': 'json',
        'payload': {
            'MathAdd': {'a': 2, 'b': 1},
        },
    }
    ipc_ret = pyckb.rpc.call('ipc_call', [ipc_script_locator, ipc_req])
    print(f'main: call result json={ipc_ret}')
    assert ipc_ret['payload']['MathAdd'] == 3


def ipc_test_call_math_add_with_exec():
    pyckb.config.upgrade('http://127.0.0.1:8114')
    pyckb.config.current = pyckb.config.develop
    user = pyckb.wallet.Wallet(0x01)
    cell = list(itertools.islice(user.livecell(), 1))[0]
    cell_out_point = pyckb.core.OutPoint.rpc_decode(cell['out_point'])
    cell_input = pyckb.core.CellInput(0, cell_out_point)

    tx = pyckb.core.Transaction(pyckb.core.RawTransaction(0, [], [], [], [], []), [])
    tx.raw.cell_deps.append(pyckb.core.CellDep.conf_decode(pyckb.config.current.script.secp256k1_blake160.cell_dep))
    tx.raw.cell_deps.append(pyckb.core.CellDep(pyckb.core.OutPoint.rpc_decode(acdb['ipc_test']['out_point']), 0))
    tx.raw.inputs.append(cell_input)
    tx.witnesses.append(pyckb.core.WitnessArgs(bytearray(65), None, None).molecule())

    ipc_script_locator = {
        'out_point': acdb['ipc_test_with_exec']['out_point'],
    }
    ipc_req = {
        'version': '0x0',
        'method_id': '0x0',
        'payload_format': 'json',
        'payload': {
            'MathAdd': {'a': 2, 'b': 1},
        },
    }
    ipc_env = {
        'tx': tx.rpc(),
        'script_group_type': 'lock',
        'script_hash': '0x' + user.script.hash().hex()
    }
    ipc_ret = pyckb.rpc.call('ipc_call', [ipc_script_locator, ipc_req, ipc_env])
    print(f'main: call result json={ipc_ret}')
    assert ipc_ret['payload']['MathAdd'] == 3


def ipc_test_call_math_add_with_hex():
    pyckb.config.upgrade('http://127.0.0.1:8114')
    pyckb.config.current = pyckb.config.develop
    ipc_script_locator = {
        'out_point': acdb['ipc_test']['out_point'],
    }
    ipc_req = {
        'version': '0x0',
        'method_id': '0x0',
        'payload_format': 'hex',
        'payload': '0x' + bytearray(json.dumps({
            'MathAdd': {'a': 2, 'b': 1},
        }).encode()).hex(),
    }
    ipc_ret = pyckb.rpc.call('ipc_call', [ipc_script_locator, ipc_req])
    print(f'main: call result json={ipc_ret}')
    assert json.loads(bytearray.fromhex(ipc_ret['payload'][2:]).decode())['MathAdd'] == 3


def ipc_test_call_math_add_with_spawn():
    pyckb.config.upgrade('http://127.0.0.1:8114')
    pyckb.config.current = pyckb.config.develop
    user = pyckb.wallet.Wallet(0x01)
    cell = list(itertools.islice(user.livecell(), 1))[0]
    cell_out_point = pyckb.core.OutPoint.rpc_decode(cell['out_point'])
    cell_input = pyckb.core.CellInput(0, cell_out_point)

    tx = pyckb.core.Transaction(pyckb.core.RawTransaction(0, [], [], [], [], []), [])
    tx.raw.cell_deps.append(pyckb.core.CellDep.conf_decode(pyckb.config.current.script.secp256k1_blake160.cell_dep))
    tx.raw.cell_deps.append(pyckb.core.CellDep(
        pyckb.core.OutPoint.rpc_decode(acdb['ipc_test_with_spawn']['out_point']), 0))
    tx.raw.inputs.append(cell_input)
    tx.witnesses.append(pyckb.core.WitnessArgs(bytearray(65), None, None).molecule())

    ipc_script_locator = {
        'out_point': acdb['ipc_test']['out_point'],
    }
    ipc_req = {
        'version': '0x0',
        'method_id': '0x0',
        'payload_format': 'json',
        'payload': {
            'Spawn': {'s': 'Hello'},
        },
    }
    ipc_env = {
        'tx': tx.rpc(),
        'script_group_type': 'lock',
        'script_hash': '0x' + user.script.hash().hex()
    }
    ipc_ret = pyckb.rpc.call('ipc_call', [ipc_script_locator, ipc_req, ipc_env])
    print(f'main: call result json={ipc_ret}')
    assert ipc_ret['payload']['Spawn'] == 'Hello'


def ipc_test_call_math_add_with_type_id_args():
    pyckb.config.upgrade('http://127.0.0.1:8114')
    pyckb.config.current = pyckb.config.develop
    ipc_script_locator = {
        'type_id_args': '0x' + pyckb.core.Script.rpc_decode(acdb['ipc_test']['type']).args.hex(),
    }
    ipc_req = {
        'version': '0x0',
        'method_id': '0x0',
        'payload_format': 'json',
        'payload': {
            'MathAdd': {'a': 2, 'b': 1},
        },
    }
    ipc_ret = pyckb.rpc.call('ipc_call', [ipc_script_locator, ipc_req])
    print(f'main: call result json={ipc_ret}')
    assert ipc_ret['payload']['MathAdd'] == 3


def ipc_test_call_string_len():
    pyckb.config.upgrade('http://127.0.0.1:8114')
    pyckb.config.current = pyckb.config.develop
    ipc_script_locator = {
        'out_point': acdb['ipc_test']['out_point'],
    }
    ipc_req = {
        'version': '0x0',
        'method_id': '0x0',
        'payload_format': 'json',
        'payload': {
            'StringLen': {
                's': '0' * 4096,
            },
        },
    }
    ipc_ret = pyckb.rpc.call('ipc_call', [ipc_script_locator, ipc_req])
    print(f'main: call result json={ipc_ret}')
    assert ipc_ret['payload']['StringLen'] == 4096


def ipc_test_call_syscall_load_script():
    pyckb.config.upgrade('http://127.0.0.1:8114')
    pyckb.config.current = pyckb.config.develop
    ipc_script_locator = {
        'out_point': acdb['ipc_test']['out_point'],
    }
    ipc_req = {
        'version': '0x0',
        'method_id': '0x0',
        'payload_format': 'json',
        'payload': {
            'SyscallLoadScript': {},
        },
    }
    ipc_ret = pyckb.rpc.call('ipc_call', [ipc_script_locator, ipc_req])
    result = pyckb.core.Script.molecule_decode(bytearray(ipc_ret['payload']['SyscallLoadScript']))
    print(f'main: call result script={result}')
    expect = pyckb.core.Script(pyckb.core.type_id_code_hash, pyckb.core.type_id_hash_type, bytearray(32)).hash()
    assert result.code_hash == expect


def ipc_test_call_syscall_load_script_with_env():
    pyckb.config.upgrade('http://127.0.0.1:8114')
    pyckb.config.current = pyckb.config.develop
    user = pyckb.wallet.Wallet(0x01)
    cell = list(itertools.islice(user.livecell(), 1))[0]
    cell_out_point = pyckb.core.OutPoint.rpc_decode(cell['out_point'])
    cell_input = pyckb.core.CellInput(0, cell_out_point)

    tx = pyckb.core.Transaction(pyckb.core.RawTransaction(0, [], [], [], [], []), [])
    tx.raw.cell_deps.append(pyckb.core.CellDep.conf_decode(pyckb.config.current.script.secp256k1_blake160.cell_dep))
    tx.raw.inputs.append(cell_input)
    tx.witnesses.append(pyckb.core.WitnessArgs(bytearray(65), None, None).molecule())

    ipc_script_locator = {
        'out_point': acdb['ipc_test']['out_point'],
    }
    ipc_req = {
        'version': '0x0',
        'method_id': '0x0',
        'payload_format': 'json',
        'payload': {
            'SyscallLoadScript': {},
        },
    }
    ipc_env = {
        'tx': tx.rpc(),
        'script_group_type': 'lock',
        'script_hash': '0x' + user.script.hash().hex()
    }
    ipc_ret = pyckb.rpc.call('ipc_call', [ipc_script_locator, ipc_req, ipc_env])
    result = pyckb.core.Script.molecule_decode(bytearray(ipc_ret['payload']['SyscallLoadScript']))
    print(f'main: call result script={result}')
    assert result == user.script


def ipc_test_deploy():
    pyckb.config.upgrade('http://127.0.0.1:8114')
    pyckb.config.current = pyckb.config.develop
    user = pyckb.wallet.Wallet(1)
    hole = pyckb.core.Script(
        pyckb.config.current.script.secp256k1_blake160.code_hash,
        pyckb.config.current.script.secp256k1_blake160.hash_type,
        bytearray([0] * 20)
    )
    prog = f'{ipc_root}/ipc_test/target/riscv64imac-unknown-none-elf/release/ipc_test_with_exec'
    print(f'main: deploy ipc_test_with_exec')
    txid = user.script_deploy_type_id(hole, bytearray(pathlib.Path(prog).read_bytes()))
    pyckb.rpc.wait(f'0x{txid.hex()}')
    print(f'main: deploy ipc_test_with_exec done txid={txid.hex()}')
    result = pyckb.rpc.get_transaction(f'0x{txid.hex()}')
    origin = pyckb.core.CellOutput.rpc_decode(result['transaction']['outputs'][0])
    print(f'main: deploy ipc_test_with_exec done args={origin.type.args.hex()}')
    acdb['ipc_test_with_exec'] = {
        'out_point': pyckb.core.OutPoint(txid, 0).rpc(),
        'type': origin.type.rpc(),
    }

    prog = f'{ipc_root}/ipc_test/target/riscv64imac-unknown-none-elf/release/ipc_test_with_spawn'
    print(f'main: deploy ipc_test_with_spawn')
    txid = user.script_deploy_type_id(hole, bytearray(pathlib.Path(prog).read_bytes()))
    pyckb.rpc.wait(f'0x{txid.hex()}')
    print(f'main: deploy ipc_test_with_spawn done txid={txid.hex()}')
    result = pyckb.rpc.get_transaction(f'0x{txid.hex()}')
    origin = pyckb.core.CellOutput.rpc_decode(result['transaction']['outputs'][0])
    print(f'main: deploy ipc_test_with_spawn done args={origin.type.args.hex()}')
    acdb['ipc_test_with_spawn'] = {
        'out_point': pyckb.core.OutPoint(txid, 0).rpc(),
        'type': origin.type.rpc(),
    }

    prog = f'{ipc_root}/ipc_test/target/riscv64imac-unknown-none-elf/release/ipc_test'
    print(f'main: deploy ipc_test')
    txid = user.script_deploy_type_id(hole, bytearray(pathlib.Path(prog).read_bytes()))
    pyckb.rpc.wait(f'0x{txid.hex()}')
    print(f'main: deploy ipc_test done txid={txid.hex()}')
    result = pyckb.rpc.get_transaction(f'0x{txid.hex()}')
    origin = pyckb.core.CellOutput.rpc_decode(result['transaction']['outputs'][0])
    print(f'main: deploy ipc_test done args={origin.type.args.hex()}')
    acdb['ipc_test'] = {
        'out_point': pyckb.core.OutPoint(txid, 0).rpc(),
        'type': origin.type.rpc(),
    }


os.makedirs(f'{ipc_root}/devnet', exist_ok=True)
os.makedirs(f'{ipc_root}/res', exist_ok=True)

for cmd in args.cmd:
    if cmd == 'ckb_build':
        ckb_build()
    if cmd == 'ckb_init':
        ckb_init()
    if cmd == 'ckb_pm_c':
        ckb_pm_c()
    if cmd == 'ckb_pm_k':
        ckb_pm_k()
    if cmd == 'ipc_test_build':
        ipc_test_build()
    if cmd == 'ipc_test_call_infinite_loop':
        ipc_test_call_infinite_loop()
    if cmd == 'ipc_test_call_math_add':
        ipc_test_call_math_add()
    if cmd == 'ipc_test_call_math_add_with_exec':
        ipc_test_call_math_add_with_exec()
    if cmd == 'ipc_test_call_math_add_with_spawn':
        ipc_test_call_math_add_with_spawn()
    if cmd == 'ipc_test_call_math_add_with_hex':
        ipc_test_call_math_add_with_hex()
    if cmd == 'ipc_test_call_math_add_with_type_id_args':
        ipc_test_call_math_add_with_type_id_args()
    if cmd == 'ipc_test_call_string_len':
        ipc_test_call_string_len()
    if cmd == 'ipc_test_call_syscall_load_script':
        ipc_test_call_syscall_load_script()
    if cmd == 'ipc_test_call_syscall_load_script_with_env':
        ipc_test_call_syscall_load_script_with_env()
    if cmd == 'ipc_test_deploy':
        ipc_test_deploy()
