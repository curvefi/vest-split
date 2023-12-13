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
./scripts/deploy-splitter.py --verify
```
This will check if distribution in the deployment exactly coincides with the distribution given in csv files.
