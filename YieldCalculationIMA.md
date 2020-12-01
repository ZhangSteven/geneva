# calculate_ima_yield.py

The output looks something like below. The following output needs to be calculated in two scenarios: with cash and without cash.

Month | Accumulated Realized Return | Return Rate | Accumulated Total Return | Return Rate | Time Weighted Capital
------|-----------------------------|-------------|--------------------------|------------|------------
1 | | | | | |
2 | | | | | |
... | | | | | |
X | | | | | |

Where,

Item | 对应中文 |Meaning
-----|----------|-------
Accumulated Realized Return | 总实现收益 | The accumulated realized return since year beginning
Accumulated Total Return | 总综合收益 | Similar to the above, but on total return number
Time Weighted Capital | 资金平均占用额 | Time weighted new capital since year beginning
Return Rate | 收益率 | Accumulated Return / Time Weighted Capital



## Calculation Methodology
Here is the way to calculate returns.


### Realized Return (实现投资收益)

Component | Columns | Calculation | Report
----------|---------|-------------|-------
Interest Income (息类收入) | interest, dividend | add, for positions established this year | profit loss
Realized G/L (买卖价差) | realized price G/L, realized FX G/L, realized cross | add, for all positions | profit loss
Fair Value Change (公允价值变动损益) | N/A | 0, since HTM positions have no fair value change | N/A

Realized Return is the sum of the above 3 components.

Assume: 

1. For interest income, there is no special case like CN Energy bought this year;
2. Profit gain loss offset for CN Energy interest income does not appear as deposit withdrawl.

#### Questions
When a bond matures, does it produces realized gain loss? If so, would we need to add those to the realized gain (买卖价差)?


### Time Weighted Capital (资金平均占用额)

Category | Calculation | Report
---------|-------------|-------
Deposit (Withdrawal) | BookAmount X (report date - cash date + 1)/365, withdrawal has negative amount | cash ledger
Maturity (Interest) | BookAmount X (report date - cash date)/365 | cash ledger

#### Questions
Does interest count in the time weighted capital?


### Total Return (综合收益)

Component | Columns | Calculation | Report
----------|---------|-------------|-------
Fair Value Change (公允价值变动损益) | unrealized price G/L, unrealized FX G/L, unrealized cross | add, for all AFS positions | profit loss

Total Return = Realized Return of the same period + Fair Value Change


### Special Cases

Some early redemptions (bond call) are booked as bond sales in Geneva. We need to treat them as maturity events. Maybe we should list the Tran IDs of such sales in a config file so that we can filter them out in the cash ledger.