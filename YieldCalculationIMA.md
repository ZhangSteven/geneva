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
Realized Return is the sum of two components:

1. Interest Income (息类收入) ;
2. Realized Gain Loss (买卖价差) ;


### Interest Income
The interest income that matters is the interest income of those bought during the year, i.e., tax lots created this year. To do this, we will use the daily interest accrual detail report to get interest income of tax lots.

In the daily interest accrual detail report, each line is a record of two kinds,

Record Type | Condition | Meaning
------------|-----------|--------
Tax Lot Interest Accrual Status | LotSumOfPurSoldPaidRecLocal = 0 | status of interest accrued to a tax lot on a day
Interest Payment Event | LotSumOfPurSoldPaidRecLocal > 0 | interest payment due to bond maturity or sale of tax lot(s)

Where,

Column Name | Meaning 
------------|---------
Investment | identity of an investment to which a tax lot belongs or an interest payment event applies
Date | date of a record
LotID | tax lot ID or event ID
Textbox84 | quantity of a position that includes one or more tax lots on a day
LotQuantity | quantity of a tax lot, if the record is an interest payment event, LotQuantity is always 0
LotSumOfChangeInAIBook | accrued interest received on the day
LotSumOfEndBalanceBook | ending value of accrued interest on the day

A tax lot is uniquely identified by its tax lot id. There could be one or more interest accrual events for a tax lot during a period.

Interest income of a tax lot during a period is calculated as:

	interest income = ending value of accrued interest of the period - starting value of accrued interest of the period + interest received during the period

Where,

1. Ending value of accrued interest of the period: LotSumOfEndBalanceBook of the tax lot on the last day the tax lot appears in the period when LotQuantity > 0.

2. Starting value of accrued interest of the period: (LotSumOfEndBalanceBook - LotSumOfChangeInAIBook) of a tax lot interest accrual status record on the day the tax lot appears the first time in the period.


#### Interest Received By a Tax Lot
When an interest payment event occurs, one or more tax lots could receive interest. This is usually due to: 

1. A bond matures or is called;
2. A bond pays coupon;
3. A bond position (the whole or a part of) is sold.

When the above happens, say it's on day D0 and for bond BB, there will be one or more interest payment events which satisfy:

1. Date = D0;
2. Investment = BB.

then we have:

	total amount of interest received = sum of LotSumOfChangeInAIBook of such interest payment events

Then coupon received by a tax lot of bond BB on day D0 is the pro-rata share of the total amount of interest received based on its tax lot quantity. Refer to "Calculate tax lot interest income from daily interest accruals.xlsx" for more details.

Note that a bond can have interest payment events on multiple days during a period, so does a tax lot. Therefore, 

	interest received by a tax lot = sum of interest received by the tax lot from all such events during the period.


### Realized Gain Loss
Similar to interest income, the realized gain loss that matters is of those tax lots that

1. are created this year;
2. belong to bond positions.

We will use profit loss summary report that

1. include tax lot details;
2. with group1 = investmentType, group2 = printGroup.

Then we have:

	realized gain loss of a tax lot = realized price gain loss + realized FX gain loss

Note that we need to exclude tax lots created due to interfund transfers within the same portfolio group. An interfund transfer means transfering a position from one portfolio to another. A transfer appears as a pair of buy and sell trades, selling from one portfolio and buying from another. The pair of trades share the same security, trade date, settlement date, quantity, and price. The broker of the transfer is not a real world broker, but leave as blank or dummy brokers like "BB".



## Total Return (综合收益)
For total return, we have

	Total Return = Realized Return + Fair Value Change


### Fair Value Change (公允价值变动损益)
The fair value change means unrealized gain loss of tax lots that

1. are created this year;
2. belong to AFS bond positions.

Again, we will use the profit loss summary report generated for the realized gain loss. Then we have:

	fair value change = unrealized price gain loss + unrealized FX gain loss



## Time Weighted Capital (资金平均占用额)

Category | Calculation | Report
---------|-------------|-------
Deposit (Withdrawal) | BookAmount X (report date - cash date + 1)/365, withdrawal has negative amount | cash ledger
Maturity (Paydown) | BookAmount X (report date - cash date)/365 | cash ledger
*Sales* | BookAmount X (report date - settle date)/365 | cash ledger

Time weighted capital will be calculated in two scenarios:
1. Including cash flow from sales of any position;
2. Excluding such cash flow.


### Early Redemption Trades
Early redemptions (bond call) are booked as bond sales in Geneva. We need to treat them as bond maturity events.

We can use the trade ticket report to search for TranIDs of early redemption trades that satisfy either of the following conditions:

- The broker (field textbox119) is “Early Redem(Internal Ref.)”, or
- The broker is empty and the comments (field textbox55) contains things like: early red, early redem or something similar.
