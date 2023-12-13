Splitter of vesting escrow (deployed by Curve DAO etc).
===========================================================

Primary purpose is for recovery from Curve/Vyper hack at the end of July 2023, however can be repurposed also.

Preparing environment
-----------------------

```
virtualenv .venv
source .venv/bin/activate
pip3 install poetry
./.venv/bin/poetry install
```

Deployment
-------------

To deploy all the splitters, run:
```
./scripts/deploy-splitter.py
```
If you want to test the deployer, just add `--fork` option. This does not require hardhat or anything installed.

To verify the deployment, put the addresses of deployment contracts into the `deploy-splitter.py` file in
`deployed_splitters` dictionary and run:
```
./scripts/deploy-splitter.py --verify --fork
```
This will check if distribution in the deployment exactly coincides with the distribution given in csv files.

Amounts to be recovered
--------------------------

Unvested DAO-owned CRV: https://etherscan.io/address/0xe3997288987E6297Ad550A69B31439504F513267
123'915'151 CRV = 78M worth

### CRV/ETH pool

Lost at today's prices (-): 9'171.4322 ETH + 32'246'173.9 CRV

Missed rewards (-): 2'579'693.91 CRV

Recovered by 0xc0ffeebabe to https://etherscan.io/address/0xc447fcaf1def19a583f97b3620627bf69c05b5fb (+): 2'880 ETH

Recovered by Addison to DAO (+): 371.198 WETH + 92,696.3 CRV

Recovered by c0ffeebabe to DAO (+): 1.0116 ETH

To vest as CRV: 5'919 ETH + 32'153'477.6 CRV + 2'579'693.91 CRV

Contracts to deploy: WETH, CRV recovery

CRV to vest: 55'544'782.73 CRV

### pETH pool

ETH left to recover: 613.53 ETH

Contracts to deploy: CRV recovery

CRV amount to vest for that: 2'157'132.57 CRV

### alETH pool

Exploited amount: 7'690.64 ETH + 8231.09 alETH ~= 15'921.6451 ETH

Note: alETH was at parity with ETH at the time of the hack

Recovered to 0xbabe: 1 alETH

Recovered to Alchemix: 5050.5 alETH + 7302.33 ETH

ETH left to recover: 3567.8151 ETH

Contracts to deploy: CRV, WETH, alETH recovery

CRV amount to vest for that: 12'544'211.6 CRV

### msETH pool

Exploited amount: 2262.38 ETH

Recovered and distributed by Metronome: 80.86%

Left to recover: 433.02 ETH

Contracts to deploy: CRV

CRV amount to vest: 1'522'470.85 CRV

### Total to vest:

71'768'597.75 CRV out of 123'915'151 CRV available in the DAO

### Deployed splitters

#### CRV/ETH

WETH: https://etherscan.io/address/0x3D7b8d296f7D8E37ce57E556DEa3dd6CB01B2F03

CRV: https://etherscan.io/address/0x8CB5416edBce99AA1cAf3e16b594F97272E7b500

#### AlETH:

alETH: https://etherscan.io/address/0x0c9da84ef2c698EBc2b17Fb59c63FAA18e367b10

WETH: https://etherscan.io/address/0x2fc945d48A4d61eC988F8CAbfFbe6F1EfE07137f

CRV: https://etherscan.io/address/0x94Fd231FBAe3d66c0E1317350D708AC189c9A5cb

#### msETH

 CRV: https://etherscan.io/address/0x72aa5fcccf0fbc5d7111ebEf5F460bBf899dacF5

#### pETH

CRV: https://etherscan.io/address/0x3f4E97042206D50Ac2d4D0Db1B8af092239E2cCe
