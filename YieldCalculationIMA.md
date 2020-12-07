# calculate_ima_yield.py

The output looks something like below. The following output needs to be calculated in two scenarios: with cash and without cash.

Month | Realized Return | Return Rate | Total Return | Return Rate | Time Weighted Capital
------|-----------------------------|-------------|--------------------------|------------|------------
1 | | | | | |
2 | | | | | |
... | | | | | |
X | | | | | |

Where,

Item | 对应中文 |Meaning
-----|----------|-------
Realized Return | 实现收益 | realized return since year beginning
Total Return | 综合收益 | total return since year beginning
Time Weighted Capital | 资金平均占用额 | time weighted new capital since year beginning
Return Rate | 收益率 | Return / Time Weighted Capital



## Realized Return (实现投资收益)
Realized Return is the sum of the below 3 components:

1. Interest income (息类收入) ;
2. Realized G/L (买卖价差) ;
3. Fair Value Change (公允价值变动损益) .


### Interest Income
interest income = sum of interest income of all new tax lots created during the period

A new tax lot created during the period is a tax lot that,
1. appears in the daily interest accrual details report during the period (*current period report*);
2. does not appear in daily interest accrual details report with a period end date just one day before the current period (*previous period report*).

For a tax lot,

interest income during the period = accrued interest at current period report - accrued interest at previous period report + coupon payment at current period report


#### Accrued Interest
On a certain day, the accrued interest of a tax lot is shown in the LotSumOfEndBalanceBook column of a daily interest accrual details report. The accrued interest of a tax lot during a period is the accrued interest of the tax lot on the last day the tax lot appears during that period.

For example, a tax lot appears like this in the report

Day | LotSumOfEndBalanceBook
----|-----------------------
d1 | v1
d2 | v2
...
d_N | v_N
... does not appear any more in the remaining days ... |

Then accrued interest of the tax lot is v_N.

If the tax lot does not appear in a report during some period, then accued interest is 0 for that period.


Item | Value
-----|------
Interest Income Start Day | 2020-01-01
Interest Income End Day | 2020-06-30
Accrued Interest Start Day | 2019-12-31
Accrued Interest End Day | 2020-06-30

Note that if we want 2020-01-01 as the start date and 2020-06-30 and the end date of interest income, it means interest income on the two dates are also included. Therefore we should use 2019-12-31 and 2020-06-30 as the period start date and end date to compute the change of LotSumOfEndBalanceBook, as shown in the above table.


#### Coupon Payment
Coupon payment of a tax lot during a period = sum of coupon received by the tax lot during the period

A bond can receive zero or more coupon payments during a period, similar for a tax lot. When a coupon payment happens, there will be one or more lines with column LotQuantity = 0 in the daily interest accrual details report, with LotSumOfChangeInAIBook column as the book amount of the coupon payment.

Here is an example to illustrate how to compute coupon received by a tax lot when a coupon payment happens.

For example USM8220VAA28 HTM, it pays coupon on Feb 29th. On that day, there could be one or more coupon payment entries for this bond, then

coupon payment amount on that day = sum of LotSumOfChangeInAIBook of all coupon payment lines for the bond

Then,

coupon received by a tax lot of the bond on that day = pro-rata share of total coupon payment of the tax lot

For example,

Item | Quantity | Coupon Amount
-----|----------|-------
Total Coupon | N/A | 12,000
Tax Lot 1 | 1,000 | 2,000
Tax Lot 2 | 2,000 | 4,000
Tax Lot 3 | 3,000 | 6,000


### Realized G/L
Realized G/L = realized price G/L + realized FX G/L + realized cross from the profit loss report.

enable tax lot details when generating a profit loss report, then we can get G/L numbers for a tax lot.

Two types of:

1. Sales of new tax lots during the period, except for sale trades due to interfund transfers;
2. Maturity events of new tax lots during the period.


#### Interfund transfers
An interfund transfer means transfering a bond from one portfolio to another in the same portfolio group. A transfer appears as a pair of buy and sell trades, selling from one portfolio and buying from another. The pair of trades have the same security, same trade date/settlement date, same quantity and same price. The broker of the transfer is not a real world broker, but leave as blank or dummy brokers like "BB".



## Time Weighted Capital (资金平均占用额)

Category | Calculation | Report
---------|-------------|-------
Deposit (Withdrawal) | BookAmount X (report date - cash date + 1)/365, withdrawal has negative amount | cash ledger
Maturity | BookAmount X (report date - cash date)/365 | cash ledger
*Sales* | BookAmount X (report date - settle date)/365 | cash ledger

Sales: we calculate time weighted capital in two cases:

1. Cash flow due to sales of all bonds included;
2. Sales not included.


### Early Redemption Trades
Early redemptions (bond call) are booked as bond sales in Geneva. We need to treat them as bond maturity events.



## Total Return (综合收益)
Total Return = Realized Return + Fair Value Change (公允价值变动损益)

where,

Fair Value Change = unrealized price G/L + unrealized FX G/L + unrealized cross

for newly established non-HTM positions within the period, data is from profit loss report.