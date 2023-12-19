import boa

def test_claim_all(batch_claimer, splitter, splitter_2, vesting_escrow, vesting_escrow_2, token, accounts, admin):
    splitters = [splitter, splitter_2]
    escrows = [vesting_escrow, vesting_escrow_2]

    with boa.env.prank(admin):
        for s, e in zip(splitters, escrows):
            s.set_vest(e.address)

    user = accounts[0]
    with boa.env.prank(admin):
        for s in splitters:
            s.save_distribution([user], [10**18])
            s.finalize_distribution()

    boa.env.time_travel(366 * 86400)

    with boa.env.prank(user):
        batch_claimer.claim_all(user, [s.address for s in splitters])
    assert token.balanceOf(user) == 2 * 10**8 * 10**18
