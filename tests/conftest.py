import boa
import pytest


@pytest.fixture(scope="session")
def accounts():
    return [boa.env.generate_address() for _ in range(10)]


@pytest.fixture(scope="session")
def admin():
    return boa.env.generate_address()


@pytest.fixture(scope="session")
def token(admin):
    with boa.env.prank(admin):
        return boa.load('contracts/testing/ERC20Mock.vy', "CRV", "CRV", 18)


@pytest.fixture(scope="session")
def vesting_escrow(token, accounts, admin):
    with boa.env.prank(admin):
        escrow = boa.load('contracts/testing/VestingEscrowSimple.vy')
        t0 = boa.env.vm.patch.timestamp
        token._mint_for_testing(admin, 10**8 * 10**18)
        token.approve(escrow.address, 2**256 - 1)
        escrow.initialize(
            admin, token.address, accounts[0], 10**8 * 10**18,
            t0, t0 + 365 * 86400, False)
        return escrow


@pytest.fixture(scope="session")
def splitter(token, vesting_escrow, admin):
    with boa.env.prank(admin):
        return boa.load('contracts/VestSplitter.vy', token.address, vesting_escrow.address)
