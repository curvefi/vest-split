import boa

from hypothesis import settings
from hypothesis.stateful import RuleBasedStateMachine, run_state_machine_as_test, rule, initialize
from hypothesis import strategies as st


class StatefulVest(RuleBasedStateMachine):
    dist = st.lists(st.integers(min_value=1, max_value=10**5 * 10**18), min_size=1, max_size=300)
    batch_size = st.integers(min_value=1, max_value=200)
    user_f = st.floats(min_value=0, max_value=1)
    use_claim_for = st.booleans()
    time_shift = st.integers(min_value=1, max_value=365 * 86400)
    donation_amount = st.integers(min_value=0, max_value=10**7 * 10**18)

    @initialize(dist=dist, batch_size=batch_size)
    def initializer(self, dist, batch_size):
        self.n_users = len(dist)
        self.amounts = dist
        self.dist = dist
        dist = dist[:]
        self.users = self.many_accounts[:len(dist)]
        users = self.users[:]

        with boa.env.prank(self.admin):
            batch_users = []
            batch_dist = []
            for i in range(min(batch_size, len(users))):
                batch_users.append(users.pop())
                batch_dist.append(dist.pop())
            self.splitter.save_distribution(batch_users, batch_dist)
            self.splitter.finalize_distribution()

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


def test_stateful_vest(splitter, vesting_escrow, many_accounts, token, admin):
    StatefulVest.TestCase.settings = settings(max_examples=10, stateful_step_count=10)
    for k, v in locals().items():
        setattr(StatefulVest, k, v)
    run_state_machine_as_test(StatefulVest)
