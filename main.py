class EthAccount:
    def __init__(self, address, eth_balance=0):
        self.eth_balance = eth_balance
        self.address = address

    def transfer(self, to, eth):
        assert isinstance(to, EthAccount)
        assert self.eth_balance >= eth
        self.eth_balance -= eth
        to.eth_balance += eth
        print(f"➡️\t👛 {self.address}\t--->\t👛 {to.address}\t{eth:.2f} ETH")

    def __repr__(self):
        return f"👛 {self.address}\t{self.eth_balance:.2f} ETH"


class Player:
    def __init__(self, name, eth_balance):
        self.name = name
        self.accounts = []
        self.account_index = 1
        self.create_account(eth_balance)
        print(f"Here born {repr(self)}")

    @property
    def default_account(self):
        return self.accounts[0]

    def create_account(self, eth_balance):
        address = f"{self.name}_{self.account_index}"
        account = EthAccount(address, eth_balance)
        self.accounts.append(account)
        self.account_index += 1

    def __repr__(self):
        accounts_info = '\n\t'.join([repr(account)
                                     for account in self.accounts])
        return f"😁 {self.name}\n\t{accounts_info}"


class ICOAddressData:
    def __init__(self, account):
        assert isinstance(account, EthAccount)
        self.address = account.address
        self.account = account
        self.status = "inactive"
        self.balance = 0  # token balance
        self.cap = 0
        self.v = 0  # eth balance

    @property
    def isActive(self):
        return self.status == "active"

    def __repr__(self):
        face_of = {
            "active": "😁",
            "inactive": "😴",
            "used": "😥"
        }

        return f"{face_of[self.status]} {self.address}\t{self.v:.2f} ETH\t{self.balance:.2f} TKN\t{self.cap} ETH"


class ICOContract(EthAccount):

    TOKEN_PER_ETHER = 1.0

    def __init__(self, t, u, block_number):
        super().__init__("Contract")
        self.deployed_at = block_number
        self.t = t  # withdrawal lock
        self.u = u
        self.s = 0
        self.addresses = {}

    def register(self, account):
        assert account.address not in self.addresses
        address_data = ICOAddressData(account)
        self.addresses[account.address] = address_data

    @property
    def inflation_ramp(self):
        # p(s) be a positive-valued, decreasing function
        # representing the purchase power of a native token at stage s.

        # Inflation ramp: Buyers who purchase tokens early receive a discounted
        # price. The maximum bonus might be 20% (a typical amount for
        # crowdsales today). The bonus decreases smoothly down to 10% at
        # the beginning of the withdrawal lock, and then disappears to nothing
        # by the end of the crowdsale.

        if self.s <= self.t:
            discount = 0.2 - 0.1 * (self.s / self.t)
        elif self.t < self.s <= self.u:
            discount = 0.1 * ((self.u - self.s) / (self.u - self.t))
        else:
            discount = 0
        # How many token can be purchased with 1 ETH
        purchasing_power = self.TOKEN_PER_ETHER / (1.0 - discount)
        return purchasing_power

    @property
    def crowdsale_valuation(self):
        # V: crowdsale valuation at the present instant as follows.
        active_address_values = [a.v for a in self.active_addresses]
        V = sum(active_address_values) if len(active_address_values) > 0 else 0
        return V

    @property
    def active_addresses(self):
        return [address for address in self.addresses.values() if address.isActive]

    def main_loop(self):
        self.automatic_withdrawal()

    def final_stage(self):
        print('Addresses\tTo Contract\tPurchased\tPersonal Cap')
        print('---------\t-----------\t---------\t------------')
        for k, address in self.addresses.items():
            print(address)
        print(self)

    def receive_bids(self, account, eth, personal_cap):
        # 1. Any “inactive” address A may send to the crowdfund smart
        # contract:
        #   – a positive quantity of native tokens v(A) along with
        #   – a positive-valued personal cap c(A) > V .
        # 2. The smart contract then
        #   – sets the address balance b(A) = v(A) · p(s), effectively
        #     implementing the inflation ramp (Section 2), and
        #   – sets A’s status to “active.”
        assert personal_cap > self.crowdsale_valuation

        ico_address_data = self.addresses[account.address]

        account.transfer(self, eth)
        ico_address_data.v = eth

        ico_address_data.cap = personal_cap

        ico_address_data.balance = eth * self.inflation_ramp
        ico_address_data.status = "active"

        print(self)

    def voluntary_withdrawal(self, account):
        # The following only applies prior to the withdrawal lock at time t.
        # Any “active” address A may signal that it wishes to cancel its
        # bid from any previous stage. Upon such signal, the crowdfund
        # smart contract does the following:
        # 1. refunds v(A) native tokens back to A, and
        # 2. sets A’s status to “used.”
        assert self.s <= self.t

        ico_address_data = self.addresses[account.address]
        ico_address_data.balance = 0
        self.transfer(account, ico_address_data.v)
        ico_address_data.v = 0
        ico_address_data.status = "used"

    def automatic_withdrawal(self):
        while any([self.crowdsale_valuation > a.cap for a in self.active_addresses]):
            print("⚠️ V > somebody's cap")
            min_cap = min([a.cap for a in self.active_addresses])
            Bs = [a for a in self.active_addresses if a.cap == min_cap]
            print(f"{self.crowdsale_valuation: .2f} ETH raised,",
                  f"but {', '.join([b.address for b in Bs])} want capped at {min_cap: .2f} ETH")
            S = sum([Bi.v for Bi in Bs])
            if self.crowdsale_valuation - S >= min_cap:
                print("⚠️ V - S >= min_cap \tDo a full refund")
                for a in Bs:
                    print(f"💸 Refund {a.address} {a.v} eth")
                    self.transfer(a.account, a.v)
                    a.v = 0
                    a.status = "used"
            else:
                print("⚠️ V - S < min_cap \tDo a partial refund")
                q = (self.crowdsale_valuation - min_cap) / S
                for a in Bs:
                    refund = q * a.v
                    self.transfer(a.account, refund)
                    a.balance *= (1 - q)
                    a.v *= (1 - q)
            print(self)

    def called_by_oracle(self):
        if self.s < self.u:
            self.automatic_withdrawal()
        elif self.s == self.t:
            print("\n!!!! t passed: withdrawal lock activated\n")
        elif self.s == self.u:
            print("\n!!!! u passed: token sales ended\n")
            self.final_stage()

        self.s += 1

    def __repr__(self):
        return f"⏲️ {self.s}\tV: {self.crowdsale_valuation:.2f} ETH\tp: {self.inflation_ramp:.2f} TKN/ETH"


class Chain:
    def __init__(self):
        self.block_number = 0
        self.contract = None

    def mine_a_block(self):
        self.contract.called_by_oracle()
        self.block_number += 1

    def mine(self, blocks):
        for b in range(blocks):
            self.mine_a_block()
        print(f"# {self.block_number}: 🆙 mined {blocks} blocks!")


def case_1():
    c = Chain()
    a = Player("Alice", 100)
    b = Player("Bobbb", 200)
    d = Player("David", 200)
    contract = ICOContract(50, 100, c.block_number)
    for player in [a, b, d]:
        contract.register(player.default_account)
    c.contract = contract
    c.mine(10)
    contract.receive_bids(a.default_account, 30, 79)
    c.mine(20)
    contract.receive_bids(b.default_account, 30, 79)
    contract.receive_bids(d.default_account, 20, 80)
    c.mine(100)


def case_2():
    c = Chain()
    a = Player("Alice", 100)
    b = Player("Bobbb", 200)
    d = Player("David", 200)
    e = Player("Ed", 200)
    contract = ICOContract(50, 100, c.block_number)
    for player in [a, b, d, e]:
        contract.register(player.default_account)
    c.contract = contract
    c.mine(10)
    contract.receive_bids(a.default_account, 30, 79)
    c.mine(20)
    contract.receive_bids(b.default_account, 30, 79)
    contract.receive_bids(d.default_account, 20, 80)
    c.mine(5)
    contract.receive_bids(e.default_account, 100, 200)

    c.mine(100)


def case_big_whale():
    # page 11  Monotone valuation invariant
    c = Chain()
    a = Player("Alice", 100)
    b = Player("Bobbb", 200)
    w = Player("Whale 🐳", 200)
    contract = ICOContract(50, 100, c.block_number)
    for player in [a, b, w]:
        contract.register(player.default_account)
    c.contract = contract
    c.mine(10)
    contract.receive_bids(a.default_account, 30, 79)
    c.mine(20)
    contract.receive_bids(b.default_account, 30, 79)
    c.mine(5)
    contract.receive_bids(w.default_account, 50, 200)

    c.mine(100)
    print("This case shows that a rich whale can't 'pushout' bids to lower the valuation.")


def case_whale_withdrawls():
    c = Chain()
    a = Player("Alice", 100)
    b = Player("Bobbb", 200)
    w = Player("Whale 🐳", 200)
    contract = ICOContract(50, 100, c.block_number)
    for player in [a, b, w]:
        contract.register(player.default_account)
    c.contract = contract
    c.mine(10)
    contract.receive_bids(a.default_account, 30, 79)
    c.mine(20)
    contract.receive_bids(b.default_account, 30, 79)
    c.mine(5)
    contract.receive_bids(w.default_account, 50, 200)
    c.mine(1)
    contract.voluntary_withdrawal(w.default_account)
    c.mine(100)


if __name__ == "__main__":
    # case_1()
    # case_2()
    case_big_whale()
    # case_whale_withdrawls()
