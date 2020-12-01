# calculate_yield.py

The output looks something like below. The following output needs to be calculated in two scenarios: with cash and without cash.

Month | Accumulated Realized Return | Return Rate | Accumulated Total Return | Return Rate | Average Nav
------|-----------------------------|-------------|--------------------------|------------|------------
1 | | | | | |
2 | | | | | |
... | | | | | |
X | | | | | |

Where,

Item | Meaning
-----|---------
Accumulated Realized Return | The accumulated realized return per month from year beginning to now. For the case of 2020 Mar, it means adding up the realized return of 2020 Jan, 2020 Feb and 2020 Mar.
Accumulated Total Return | Similar to the above, but on total return numbers.
Average NAV | The average of per month NAV since last year end. For the case of 2020 Mar, it means adding up NAV of 2019 Dec, 2020 Jan, 2020 Feb and 2020 Mar, then divide by 4.
Return Rate | Accumulated Return / Average NAV



## Calculation Methodology
Here is how to calculate realized return, total return and NAV per month.

Item | Columns | Adjustment |Data Source
-----|--------|--------------|-----------
Realized Return | Interest, Dividend, OtherIncome, RealizedPrice, RealizedFX, RealizedCross | adjustment01 | profit loss report
Total Return | UnrealizedPrice, UnrealizedFX, UnrealizedCross, Interest, Dividend, OtherIncome, RealizedPrice, RealizedFX, RealizedCross | adjustment02 | profit loss report
NAV | AccruedInterest, MarketValueBook | adjustment03 | investment position

The adjustments are different in two scenarios: with cash and without cash

-| With Cash | Without Cash
-|-----------|-------------
adjustment01 | interest income of cash positions + interest income of CN Energy positions | realized return of cash positions + interest income of CN Energy positions
adjustment02 | interest income of cash positions + interest income of CN Energy positions + unrealized gain loss of CN Energy positions | total return of cash positions + unrealized gain loss of CN Energy positions + interest income of CN Energy positions
adjustment03 | AccruedInterest of CN Energy positions + impairment (case 1) or impairment (case 2) | AccruedInterest and MarketValueBook of cash positions + AccruedInterest of CN Energy positions + impairment (case 1); AccruedInterest and MarketValueBook of cash positions + impairment (case 2)

Where the terms are defined as below:

1. interest income: add up Interest, Dividend, OtherIncome of a position;
2. unrealized gain loss: add up UnrealizedPrice, UnrealizedFX, UnrealizedCross of a position;
3. case 1: after the cutoff month, which is the last month fund accounting team booked offset for CN Energy interest income;
4. case 2: on or before the cutoff month;
5. impairement: a fixed number known by run time;
6. cash position: a position whose "SortKey" field equals "Cash and Equivalents" and "LongShortDescription" field equals "Cash Long";
7. CN Energy position: a position whose "Description" field contains "CERCG" and investment type is "Corporate Bond".
