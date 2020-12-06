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



## Realized Return (实现投资收益)
Realized Return is the sum of the below 3 components:

1. Interest income (息类收入) ;
2. Realized G/L (买卖价差) ;
3. Fair Value Change (公允价值变动损益) .

Component | Columns | Calculation | Filter | Report
----------|---------|-------------|--------|-------
Interest Income (息类收入) | interest, dividend | add, for tax lots established this year | for tax lots added this year | profit loss
Realized G/L (买卖价差) | realized price G/L, realized FX G/L, realized cross | add, for all (?) positions | profit loss
Fair Value Change (公允价值变动损益) | N/A | 0, since HTM positions have no fair value change | N/A



### Interest Income
The calculation here applies to new tax lots this year. New tax lots are tax lots that are not in the previous year's daily interest accrual details report. Tax lots are identified by tax lot IDs (the LotID column). We have

interest income of a tax lot during a period = accrued interest of the tax lot at end of the period - accrued interest at beginning of the period + total coupon payment book value during the same period


#### Accrued Interest
To get accrued interest of a tax lot on a certain day, use the LotSumOfEndBalanceBook value from the daily interest accrual details report for the tax lot on that day.

Item | Value
-----|------
Interest Income Start Day | 2020-01-01
Interest Income End Day | 2020-06-30
Accrued Interest Start Day | 2019-12-31
Accrued Interest End Day | 2020-06-30

Note that if we want 2020-01-01 as the start date and 2020-06-30 and the end date of interest income, it means interest income on the two dates are also included. Therefore we should use 2019-12-31 and 2020-06-30 as the period start date and end date to compute the change of LotSumOfEndBalanceBook, as shown in the above table.


#### Coupon Payment
Here is an example to illustrate how to compute coupon payment for a tax lot on a certain date.

For USM8220VAA28 HTM, it pays coupon on Feb 29th. From the daily interest accrual details report, coupon payment events have LotQuantity = 0, with LotSumOfChangeInAIBook column as coupon payment amount in book currency. Then on Feb 29th, there may be one or more coupon payment entries for this bond, define

total coupon payment on that day = sum of LotSumOfChangeInAIBook

Then, on Feb 29th, each tax lot of USM8220VAA28 HTM has:

coupon payment for the tax lot on that day = pro-rata share of total coupon payment of the tax lot

For example,

Item | Quantity | Amount
-----|----------|-------
Total Coupon | N/A | 12,000
Tax Lot 1 | 1,000 | 2,000
Tax Lot 2 | 2,000 | 4,000
Tax Lot 3 | 3,000 | 6,000

Then,

total coupon payment for a tax lot during a period = sum of coupon payment for the tax lot when payment dates fall into the period




### Questions
1. For realized G/L (买卖价差) above, is it for all positions or just positions established this year?



## Time Weighted Capital (资金平均占用额)

Category | Calculation | Report
---------|-------------|-------
Deposit (Withdrawal) | BookAmount X (report date - cash date + 1)/365, withdrawal has negative amount | cash ledger
Maturity | BookAmount X (report date - cash date)/365 | cash ledger



## Total Return (综合收益)

Component | Columns | Calculation | Report
----------|---------|-------------|-------
Fair Value Change (公允价值变动损益) | unrealized price G/L, unrealized FX G/L, unrealized cross | add, for all AFS positions | profit loss

Total Return = Realized Return of the same period + Fair Value Change



## Special Cases

1. Early redemptions (bond call) are booked as bond sales in Geneva. We need to treat them as bond maturity events.

2. Interfund transfers appear as buy/sell trades. We should ignore them in realized G/L calculation.

3. How does interfund transfers affect total G/L?
