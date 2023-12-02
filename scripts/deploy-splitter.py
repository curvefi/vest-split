#!/usr/bin/env python3

import boa
import json
import os
import sys
import csv

from more_itertools import chunked
from getpass import getpass
from eth_account import account
from boa.network import NetworkEnv


NETWORK = "http://localhost:8545"
WETH = "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"
CRV = "0xD533a949740bb3306d119CC777fa900bA034cd52"
title = 'ETH to recover'

# Only for example, can include any coins (e.g. msETH and alETH)
# Files are only used for ratios, not for quantities (total quantity is decided by the DAO or whoever distributes)
files_and_tokens = [
    ('crveth-reprocessed', [WETH, CRV]),
    ('aleth-reprocessed', [WETH, CRV]),
    ('mseth-reprocessed', [WETH, CRV])]


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
        boa.env.add_account(account_load('babe'))
        boa.env._fork_try_prefetch_state = False

    shares = {}
    splitters = {}
    deployed_distribution_fname = os.path.join(os.path.dirname(sys.argv[0]), 'deployed-distribution.json')

    if '--verify' not in sys.argv[1:]:
        for fname, tokens in files_and_tokens:
            shares[fname] = []
            splitters[fname] = {}

            with open(os.path.join(os.path.dirname(sys.argv[0]), fname + '.csv'), 'r') as f:
                reader = csv.reader(f)
                titles = next(reader)
                ix = titles.index(title)
                for row in reader:
                    shares[fname].append((row[1], int(float(row[ix]) * 1e18)))

            for token in tokens:
                print('Deploying splitter for %s, token %s' % (fname, token))
                splitter = boa.load('contracts/VestSplitter.vy', token)
                splitters[token] = splitter.address

                size = len(shares[fname])
                pos = 0
                for chunk in chunked(shares[fname], 200):
                    users, fractions = list(zip(*chunk))
                    splitter.save_distribution(users, fractions)
                    pos += len(chunk)
                    print('{0:.2f}%'.format(pos * 100 / size))
                print()

                splitter.finalize_distribution()

        with open(deployed_distribution_fname, 'w') as f:
            json.dump({'shares': shares, 'splitters': splitters}, f)

    print('Distributions deployed')

    # Read to verify distribution
    with open(deployed_distribution_fname, 'r') as f:
        deployed_distribution = json.load(f)
