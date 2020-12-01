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
