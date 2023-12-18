import boa

def test_claim_all(batch_claimer, splitter, vesting_escrow, token, accounts, admin):
    with boa.env.prank(admin):
        splitter.set_vest(vesting_escrow.address)

    user = accounts[0]
    with boa.env.prank(admin):
        splitter.save_distribution([user], [10**18])
        splitter.finalize_distribution()

    boa.env.time_travel(366 * 86400)

    with boa.env.prank(user):
        # splitter.claim()
        batch_claimer.claim_all(user, [splitter.address])
        assert token.balanceOf(user) == 10**8 * 10**18
