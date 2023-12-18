# @version 0.3.10
"""
@title BatchClaimer
@author Curve DAO
@license MIT
@notice Allows claiming from multiple splitters in one transaction for a single user.
"""

interface VestSplitter:
    def claim(user: address, use_vest: bool = True): nonpayable
    def balanceOf(user: address, use_vest: bool = True) -> uint256: view


@external
def claim_all(user: address, splitters: DynArray[address, 10], use_vest:bool = True):
    for i in range(10):
        if i >= len(splitters):
            break
        splitter: address = splitters[i]
        if splitter == empty(address):
            continue
        if VestSplitter(splitter).balanceOf(user, use_vest) == 0:
            continue
        VestSplitter(splitter).claim(user, use_vest)
