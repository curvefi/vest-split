#!/usr/bin/env python3
import sys
import boa

NETWORK = "http://localhost:8545"

def account_load(fname):
    path = os.path.expanduser(os.path.join('~', '.brownie', 'accounts', fname + '.json'))
    with open(path, 'r') as f:
        pkey = account.decode_keyfile_json(json.load(f), getpass())
        return account.Account.from_key(pkey)

if __name__ == '__main__':
    if '--fork' in sys.argv[1:]:
        boa.env.fork(NETWORK)
        boa.env.eoa = '0xbabe61887f1de2713c6f97e567623453d3C79f67'
    else:
        boa.set_env(NetworkEnv(NETWORK))
        if not is_verify:
            boa.env.add_account(account_load('babe'))
        boa.env._fork_try_prefetch_state = False

    batch_claimer = boa.load("contracts/BatchClaimer.vy")
    print(f"Deployed the batch claimer at: {batch_claimer.address}")
