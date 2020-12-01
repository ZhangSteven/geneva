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
Accumulated Realized Return | The accumulated realized return since year beginning.
Accumulated Total Return | Similar to the above, but on total return numbers.
Time Weighted Capital | New cash deposit 
Return Rate | Accumulated Return / Time Weighted Capital
Realized Return | 

## Positions to Include
Only include positions that are newly established this year, i.e., interest income and other gain loss due to existing positions are not considered.


新增委托额 includes new cash deposit and cash income due to bond maturity.

What about:

cash withdrawal? considered as negative deposit

coupon payment?



## Calculation Methodology
Here is how to calculate realized return per month, total return per month and time weighted capital year to date.
