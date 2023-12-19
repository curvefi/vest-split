import boa

def test_claim_all(batch_claimer, splitter, splitter_2, vesting_escrow, vesting_escrow_2, token, accounts, admin):
    user = accounts[0]
    user_2 = accounts[1]
    splitters = [splitter, splitter_2]
    escrows = [vesting_escrow, vesting_escrow_2]
    distributions = [
        [10**18, 10**18],
        [10**18, 0],
    ]

    with boa.env.prank(admin):
        for _splitter, escrow, distribution in zip(splitters, escrows, distributions):
            _splitter.set_vest(escrow.address)
            _splitter.save_distribution([user, user_2], distribution)
            _splitter.finalize_distribution()

    boa.env.time_travel(366 * 86400)

    batch_claimer.claim_all(user, [s.address for s in splitters])
    assert token.balanceOf(user) == 5*10**7 * 10**18 + 10**8 * 10**18

    batch_claimer.claim_all(user_2, [s.address for s in splitters])
    assert token.balanceOf(user_2) == 5*10**7 * 10**18
