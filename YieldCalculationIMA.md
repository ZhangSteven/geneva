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



## Positions to Include
Only gain loss due to newly established positions this year are considered, i.e., any gain loss due to existing positions are ignored.


Time weighted capital includes new cash deposit and cash income due to bond maturity.

What about:

cash withdrawal? considered as negative deposit

coupon payment? make a table first



## Calculation Methodology
Here is how to calculate realized return and total return per month, as well as time weighted capital year to date.


