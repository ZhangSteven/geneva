# calculate_ima_yield.py

The output looks something like below. The following output needs to be calculated in two scenarios: with cash and without cash.

Month | Accumulated Realized Return | Return Rate | Accumulated Total Return | Return Rate | Time Weighted Capital
------|-----------------------------|-------------|--------------------------|------------|------------
1 | | | | | |
2 | | | | | |
... | | | | | |
X | | | | | |

Where,

Item | Meaning
-----|---------
Accumulated Realized Return | The accumulated realized return since year beginning
Accumulated Total Return | Similar to the above, but on total return number
Time Weighted Capital | Time weighted new capital since year beginning
Return Rate | Accumulated Return / Time Weighted Capital



## Calculation Methodology

NOTE: Only gain loss due to positions established this year are considered, i.e., any gain loss due to existing positions are ignored.

### Realized Return (实现投资收益)

Component | Columns | Calculation | Report
----------|---------|-------------|-------
Interest Income (息类收入) | interest, dividend | add, for positions established this year | profit loss
Realized G/L (买卖价差) | realized price G/L, realized FX G/L, realized cross | add, for AFS positions | profit loss
Fair Value Change (公允价值变动损益) | N/A | 0, since HTM positions have not value change | N/A

Realized Return is the sum of the above 3 components.


### Time Weighted Capital (资金平均占用额)

Category | Calculation | Report
---------|-------------|-------
Deposit (Withdrawal) | Amount X (report date - cash date + 1)/365, withdrawal has negative amount | cash ledger
Maturity (Interest) | Amount X (report date - cash date)/365 | cash ledger


### Total Return (综合收益)

Component | Columns | Calculation | Report
----------|---------|-------------|-------
Fair Value Change (公允价值变动损益) | unrealized price G/L, unrealized FX G/L, unrealized cross | add, for all AFS positions | profit loss

Total Return = Realized Return of the same period + Fair Value Change



