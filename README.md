# Python Interactive Coin Offerings Simulation

Trying to simulate the contract described in [this paper](https://people.cs.uchicago.edu/~teutsch/papers/ico.pdf).

Require python 3.6

## Example

```
$python main.py
Here born 😁 Alice
        👛 Alice_1       100.00 ETH
Here born 😁 Bobbb
        👛 Bobbb_1       200.00 ETH
Here born 😁 Whale 🐳
        👛 Whale 🐳_1     200.00 ETH
# 10: 🆙 mined 10 blocks!
➡️       👛 Alice_1       --->    👛 Contract      30.00 ETH
⏲️ 9     V: 30.00 ETH    p: 1.22 TKN/ETH
# 30: 🆙 mined 20 blocks!
➡️       👛 Bobbb_1       --->    👛 Contract      30.00 ETH
⏲️ 29    V: 60.00 ETH    p: 1.17 TKN/ETH
# 35: 🆙 mined 5 blocks!
➡️       👛 Whale 🐳_1     --->    👛 Contract      50.00 ETH
⏲️ 34    V: 110.00 ETH   p: 1.15 TKN/ETH
⚠️ V > somebody's cap
 110.00 ETH raised, but Alice_1, Bobbb_1 want capped at  79.00 ETH
⚠️ V - S < min_cap       Do a partial refund
➡️       👛 Contract      --->    👛 Alice_1       15.50 ETH
➡️       👛 Contract      --->    👛 Bobbb_1       15.50 ETH
⏲️ 34    V: 79.00 ETH    p: 1.15 TKN/ETH

!!!! u passed: token sales ended

Addresses       To Contract     Purchased       Personal Cap
---------       -----------     ---------       ------------
😁 Alice_1       14.50 ETH       17.73 TKN       79 ETH
😁 Bobbb_1       14.50 ETH       16.90 TKN       79 ETH
😁 Whale 🐳_1     50.00 ETH       57.60 TKN       200 ETH
⏲️ 100   V: 79.00 ETH    p: 1.00 TKN/ETH
# 135: 🆙 mined 100 blocks!
This case shows that a rich whale can't 'pushout' bids to lower the valuation.

```