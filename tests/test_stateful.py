import boa

from hypothesis import settings
from hypothesis.stateful import RuleBasedStateMachine, run_state_machine_as_test, rule, initialize, invariant
from hypothesis import strategies as st

from .conftest import INITIAL_AMOUNT, DISTRIBUTION_TIME


class StatefulVest(RuleBasedStateMachine):
    dist = st.lists(st.integers(min_value=1, max_value=10**5 * 10**18), min_size=1, max_size=300)
    batch_size = st.integers(min_value=1, max_value=200)
    user_f = st.floats(min_value=0, max_value=1)
    use_claim_for = st.booleans()
    time_shift = st.integers(min_value=1, max_value=365 * 86400)
    donation_amount = st.integers(min_value=0, max_value=10**7 * 10**18)

    def __init__(self):
        super().__init__()
        self.total_donated = 0
        self.has_vest = False

    @initialize(dist=dist, batch_size=batch_size)
    def initializer(self, dist, batch_size):
        self.initial_time = boa.env.vm.patch.timestamp  # Vest exists from this time already (but not necessarily set)
        self.n_users = len(dist)
        self.amounts = dist
        self.dist = dist
        dist = dist[:]
        self.users = self.many_accounts[:len(dist)]
        users = self.users[:]

        with boa.env.prank(self.admin):
            while len(users) > 0:
                batch_users = []
                batch_dist = []
                for i in range(min(batch_size, len(users))):
                    batch_users.append(users.pop())
                    batch_dist.append(dist.pop())
                self.splitter.save_distribution(batch_users, batch_dist)
            self.splitter.finalize_distribution()

    @rule()
    def set_vest(self):
        if not self.has_vest:
            with boa.env.prank(self.admin):
                self.splitter.set_vest(self.vesting_escrow.address)
            self.has_vest = True

    @rule(user_f=user_f, use_claim_for=use_claim_for)
    def claim(self, user_f, use_claim_for):
        user = self.users[int(user_f * (len(self.users) - 1))]
        if use_claim_for:
            with boa.env.prank(self.admin):
                self.splitter.claim(user)
        else:
            with boa.env.prank(user):
                self.splitter.claim()

    @rule(dt=time_shift)
    def time_travel(self, dt):
        boa.env.time_travel(dt)

    @rule(amount=donation_amount)
    def donate(self, amount):
        with boa.env.prank(self.admin):
            self.token._mint_for_testing(self.splitter.address, amount)
            self.total_donated += amount

    @invariant()
    def total_coins(self):
        in_escrow = self.token.balanceOf(self.vesting_escrow.address)
        received = sum(self.token.balanceOf(u) for u in self.users)
        in_splitter = self.token.balanceOf(self.splitter.address)
        assert in_escrow + received + in_splitter - self.total_donated == INITIAL_AMOUNT

    def teardown(self):
        # Claim all
        for u in self.users:
            with boa.env.prank(u):
                self.splitter.claim()

        dt = boa.env.vm.patch.timestamp - self.initial_time

        expected_total = self.has_vest * INITIAL_AMOUNT * min(dt, DISTRIBUTION_TIME) // DISTRIBUTION_TIME + self.total_donated
        balances = [self.token.balanceOf(u) for u in self.users]
        total_dist = sum(self.dist)

        assert self.token.balanceOf(self.splitter.address) < len(self.users)  # Rounding errors leave 1 wei per user max

        for d, balance in zip(self.dist, balances):
            assert balance == d * expected_total // total_dist


def test_stateful_vest(splitter, vesting_escrow, many_accounts, token, admin):
    StatefulVest.TestCase.settings = settings(max_examples=1000, stateful_step_count=100)
    for k, v in locals().items():
        setattr(StatefulVest, k, v)
    run_state_machine_as_test(StatefulVest)
