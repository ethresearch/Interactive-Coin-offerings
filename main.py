
class Address:
    def __init__(self,name, cap = 100, v0 = 50):
        self.name = name
        self.status = "inactive"
        self.balance = 0

class ICOContract:
    def __init__(self, t, u):
        self.t = t # withdrawal lock
        self.u = u
        self.s = 0
        self.addresses = {}

    @property
    def inflation_ramp(self): 
        # be a positive-valued, decreasing function 
        # representing the purchase power of a native token at stage s.

        # Inflation ramp: Buyers who purchase tokens early receive a discounted
        # price. The maximum bonus might be 20% (a typical amount for
        # crowdsales today). The bonus decreases smoothly down to 10% at
        # the beginning of the withdrawal lock, and then disappears to nothing
        # by the end of the crowdsale.
        if self.s <= self.t:
            p = 0.8 + 0.1 * (self.s /self.t)
        elif self.t<self.s <= self.u:
            p = 0.9 + 0.1 * ((self.s - self.t)/(self.u - self.t))
        return p


    @property
    def crowdsale_valuation(self):
        # V: crowdsale valuation at the present instant as follows.
        active_address_values = [ address.v for address in self.addresses.values() if address.isActive]
        V = sum(active_address_values) if len(active_address_values)>0 else 0
        return V

    def main_loop(self):
        if self.s <= self.u:
            self.receive_bids()
        if self.s < self.t:
            self.voluntary_withdrawal()
        self.automatic_withdrawal()
    def final_stage(self):
        pass

    def receive_bids(self, address_name, eth, personal_cap):
        # 1. Any “inactive” address A may send to the crowdfund smart
        # contract:
        #   – a positive quantity of native tokens v(A) along with
        #   – a positive-valued personal cap c(A) > V .
        # 2. The smart contract then
        #   – sets the address balance b(A) = v(A) · p(s), effectively
        #     implementing the inflation ramp (Section 2), and
        #   – sets A’s status to “active.”
        assert cap > self.crowdsale_valuation

        self.addresses[address_name].balance = eth * self.inflation_ramp
        self.addresses[address_name].status = "active"


    def voluntary_withdrawal(self):
        pass
    def automatic_withdrawal(self):
        pass

    def called_by_oracle(self):
        print("called by oracle")
        self.s +=1

    def __repr__(self):
        return f"⏲️ {self.s}\tV: {self.crowdsale_valuation}\tp: {self.inflation_ramp}"

class Script:
    def __init__(self, block_number = 0):
        self.block_number = 0
        self.t = 50
        self.u = 100


    def play(self):
        while self.block_number <= 100:
            
            print("block number:", self.block_number)

            if self.block_number ==0:
                contract = ICOContract(self.t, self.u)
            elif self.block_number== int(self.t/3):
                pass
            elif 1<=self.block_number <=self.u:
                contract.called_by_oracle()
                print(contract)
            
            self.block_number +=1

if __name__ == "__main__":
    s = Script()
    s.play()