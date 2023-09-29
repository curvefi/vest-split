import boa


def test_set_vest(splitter, accounts, admin):
    fake_vest = accounts[0]
    not_admin = accounts[1]

    with boa.env.prank(not_admin):
        with boa.reverts("Access"):
            splitter.set_vest(fake_vest)

    with boa.env.prank(admin):
        splitter.set_vest(fake_vest)
        with boa.reverts("Vest already set"):
            splitter.set_vest(fake_vest)


def test_access(splitter, vesting_escrow, accounts, admin):
    not_admin = accounts[0]

    with boa.env.prank(admin):
        splitter.set_vest(vesting_escrow.address)

    with boa.env.prank(admin):
        with boa.reverts("Vest already set"):
            splitter.set_vest(vesting_escrow.address)

    with boa.env.prank(not_admin):
        with boa.reverts("Access"):
            splitter.save_distribution([], [])

    with boa.env.prank(admin):
        splitter.save_distribution([], [])

    with boa.env.prank(not_admin):
        with boa.reverts("Access"):
            splitter.finalize_distribution()

    with boa.env.prank(admin):
        splitter.finalize_distribution()
        with boa.reverts("Distribution is finalized already"):
            splitter.save_distribution([], [])
        assert splitter.finalized()


def test_dist(splitter, vesting_escrow, many_accounts, admin):
    with boa.env.prank(admin):
        splitter.set_vest(vesting_escrow.address)

    accounts = [many_accounts[:200], many_accounts[200:]]
    fractions = [[10**18 * i for i in range(200)], [10**18 * i for i in range(len(many_accounts) - 200)]]
    fracmap = [(a, f) for a, f in zip(accounts[0] + accounts[1], fractions[0] + fractions[1])]

    with boa.env.prank(admin):
        for aa, ff in zip(accounts, fractions):
            splitter.save_distribution(aa, ff)
        splitter.finalize_distribution()

    total_fraction = 0
    for a, f in fracmap:
        assert splitter.fractions(a) == f
        total_fraction += f
    assert total_fraction == splitter.total_fraction()


def test_vest_one(splitter, vesting_escrow, token, accounts, admin):
    with boa.env.prank(admin):
        splitter.set_vest(vesting_escrow.address)

    user = accounts[0]
    with boa.env.prank(admin):
        splitter.save_distribution([user], [10**18])
        splitter.finalize_distribution()

    boa.env.time_travel(366 * 86400)

    with boa.env.prank(user):
        splitter.claim()
        assert token.balanceOf(user) == 10**8 * 10**18


def test_vest_many(splitter, vesting_escrow, token, many_accounts, admin):
    with boa.env.prank(admin):
        splitter.set_vest(vesting_escrow.address)

    accounts = [many_accounts[:200], many_accounts[200:]]
    fractions = [[10**18 * i for i in range(200)], [10**18 * i for i in range(len(many_accounts) - 200)]]
    fracmap = [(a, f) for a, f in zip(accounts[0] + accounts[1], fractions[0] + fractions[1])]

    with boa.env.prank(admin):
        for aa, ff in zip(accounts, fractions):
            splitter.save_distribution(aa, ff)
        splitter.finalize_distribution()

    total_fraction = splitter.total_fraction()
    boa.env.time_travel(366 * 86400)

    for a, f in fracmap:
        ready_balance = splitter.balanceOf(a)
        with boa.env.prank(a):
            splitter.claim()
        expected_balance = 10**8 * 10**18 * f // total_fraction
        assert token.balanceOf(a) == expected_balance == ready_balance
