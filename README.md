# Geneva
Geneva related code base.


## geneva.py
This module contains common code to read reports from Advent Geneva. When we generate a report and export it in comma delimited format, we can choose to save it in many formats, like below:

Save As Type | Output File Type | Encoding
-------------|------------------|---------
Excel Workbook | Excel (.xlsx) | N/A
Text (Tab delimited) | Text (.txt) | utf-8
Unicode text | Text (.txt) | utf-16
CSV (Comma delimited) | Text (.csv) | likely utf-8, to be confirmed

But when Geneva generates reports in batch mode, the output format will be "Unicode text".


### To Do
Reading a multipart report.

Usually a report contains 4 parts:

(section 1: positions)
header line of postions
position 1
position 2
...
position N

<< a blank line <<

(section 2: meta data)
header line of meta data (always "ParameterName", "ParameterValue")
line 1 (each line is a pair of header and value)
line 2
...
line N

<< a blank line <<

(section 3: run time data)
header line of meta data (always "ParameterName", "ParameterValue")
line 1 (each line is a pair of header and value)
line 2
...
line N

<< a blank line <<

(section 4: error data)
header line of meta data (always "EventNumber", "ErrorMessage")
line 1 (each line is a pair of header and value)
line 2
...
line N

When a section is empty, only the header line will be there. For example, check out the samples/11490-A investment positions 2020-12.txt file.

A report can also contain a number of the above 4 sections, i.e., when it contains multiple portfolios. Therefore we need to develop functions like:

readProfitLossTxtReport()

readMultipartProfitLossTxtReport()

To make this happen, probabaly we need to change the interface to read lines instead of file.



## count_investment.py
Count the number of securities per type from an investment report. If there are multiple positions of the same security, e.g., AFS and HTM position of the same bond, it's considered as one security. Input files required:

Report | Format 
-------|-------
Investment Positions | Txt (unicode text)



## calculate_yield.py
Calculate the realized and total return (保监会口径) of a portfoio or portfoio group. Input files required:

Report | Format | Remarks
-------|--------|--------
Investment Positions | Txt (unicode text) | named as "investment positions xxx"
Profit and Loss | Txt (unicode text) | named as "profit loss xxx"

Other input parameters:

Parameter | Meaning | Where
----------|---------|--------
lastYearEndNavWithCash | Nav of last year end (with cash) | config file
lastYearEndNavWithOutCash | Nav of last year end (without cash) | config file
impairment | impairment amount of this year | config file
cutoff month | the last month fund accounting team booked offset for CN Energy interest income | command line

Note: the cutoff month must be consistent with the underlying data. For example the current cutoff month is 7 and fund account team just booked offset for CN Energy interest income in August, then we must re-generate all the reports since August and run the program again with cutoff = 8.

For the calculation methodology, see the YieldCalculation.md file.