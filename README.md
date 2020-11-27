# Geneva
This project aims at creating a library to read and process reports from Advent Geneva system. When we export reports from Geneva, usually we will choose the comma delimited format. If we do it manually, the following will happen:

1. An Excel window pops up to open the exported csv file;
2. We save it with an output format.

Save As Type | Output File Type | Encoding
-------------|------------------|---------
Excel Workbook | Excel (.xlsx) | N/A
Text (Tab delimited) | Text (.txt) | utf-8
Unicode text | Text (.txt) | utf-16
CSV (Comma delimited) | Text (.csv) | likely utf-8, to be confirmed



## To Do
How to read a multipart file, e.g., investment all funds 2020-09-30.txt

This file contains multiple portfolios.
