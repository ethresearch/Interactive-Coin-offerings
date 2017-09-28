
class Address:
    def __init__(self,name, isActive, cap = 100, v0 = 50):
        self.name = name
        self.isActive = False

class ICOContract:
    def __init__(self, t, u):
        self.t = t # withdrawal lock
        self.u = u
        self.s = 0
        self.addresses = []

    def p(self, s): 
        # be a positive-valued, decreasing function 
        # representing the purchase power of a native token at stage s.
        pass

    @property
    def crowdsale_valuation(self):
        # V: crowdsale valuation at the present instant as follows.
        active_address_values = [ address.v for address in self.addresses if address.isActive]
        V = sum(active_address_values) if len(active_address_values)>0 else 0
        return V

    def initialization(self):
        pass

    def main_loop(self):
        self.receive_bids()
        if self.s < self.t:
            self.voluntary_withdrawal()
        self.automatic_withdrawal()
    def final_stage(self):
        pass

    def receive_bids(self):
        pass

    def voluntary_withdrawal(self):
        pass
    def automatic_withdrawal(self):
        pass

    def called_by_oracle(self):
        print("called by oracle")
        self.s +=1

    def __repr__(self):
        return f"⏲️ {self.s} V: {self.crowdsale_valuation}"

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