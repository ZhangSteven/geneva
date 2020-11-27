# coding=utf-8
#
# Provide utility functions to read Geneva reports.
# 

from xlrd import open_workbook
from toolz.functoolz import compose
from utils.iter import pop
from utils.excel import worksheetToLines
from utils.utility import fromExcelOrdinal
from itertools import takewhile, groupby
from functools import partial
from os.path import abspath, dirname
from datetime import datetime
import codecs
import logging
logger = logging.getLogger(__name__)



"""
	[Iterable] lines => [Dictionary] meta data.

	Lines in the meta data section looks like:

	ParameterName	ParameterValue																
	AccountingCalendar	InHouse_AccountingCalendar																
	AccountingFilters																	
	...
	BookCurrency	HKD
"""
getRawMetadata = compose(
	dict
  , partial(map, lambda line: (line[0], line[1]) if len(line) > 1 else (line[0], ''))
)



"""
	[Iterator] line => [List] headers
"""
getHeadersFromLine = compose(
	list
  , partial(takewhile, lambda s: s.strip() != '')
  , partial(map, str)
)



"""
	[Iterable] lines => [List] Raw Positions

	Assume: each line is an iterator over its columns.
"""
getRawPositions = compose(
	list
  , partial(map, dict)
  , lambda t: map(partial(zip, t[0]), t[1])
  , lambda lines: (getHeadersFromLine(pop(lines)), lines)
)



"""
	[Iterator] lines => [Iterator] positions, [Dictionary] metaData

	Lines from a Geneva report are divided into sections by blank lines. 
	If the report is about a single portfolio or consolidate = group for
	a group of portfolios, then the first section is its positions and the
	second section is its meta data.

	The function groupby() returns an iterator, according to our observation
	if we consume the 3rd section (the meta data) first, then first section
	(positions) we will get nothing. So we must use 'list' to get the positions
	first, then get the meta data.
"""
readReport = compose(
	lambda group: ( getRawPositions(pop(group))
				  , getRawMetadata(pop(group))
				  )
  , partial(map, lambda el: el[1])
  , partial(filter, lambda el: el[0] == False)
  , lambda lines: groupby(lines, lambda line: len(line) == 0 or line[0] == '')
)



"""
	[String] file => [Iterable] lines
"""
excelFileToLines = lambda file: \
	worksheetToLines(open_workbook(file).sheet_by_index(0))



"""
	[String] file => [Iterator] positions, [Dictionary] metaData

	Read a Geneva report in Excel file. The report is generated as export
	in 'Comma Delimited' format then saved as Excel (xlsx).
"""
readExcelReport = compose(
	lambda t: (t[0], getExcelMetadata(t[1]))
  , readReport
  , excelFileToLines
)



toDateTimeString = lambda f: \
	fromExcelOrdinal(f).strftime('%Y-%m-%d')


toStringIfFloat = lambda x: \
	str(int(x)) if isinstance(x, float) else x


getCurrentDirectory = lambda : \
	dirname(abspath(__file__))


# [Dictioanry] d1, [Dictioanry] d2 => [Dictionary] merged d
mergeDict = lambda d1, d2: \
	{**d1, **d2}



"""
	[Dictionary] functionMap (key -> function), [Dictionary] d
		=> [Dictionary] updated d (with keys in functionMap)

	Create a copy of the input dictionary d, with certain key, value pairs
	updated for those keys in the functionMap. 
"""
updateDictionaryWithFunction = lambda functionMap, d: \
	mergeDict(d, {key: functionMap[key](d[key]) for key in functionMap})



"""
	[Dictonary] raw metadata => [Dictionary] metadata
"""
getExcelMetadata = lambda metadata: \
	updateDictionaryWithFunction(
		{ 'Portfolio': toStringIfFloat
		, 'PeriodEndDate': toDateTimeString
		, 'PeriodStartDate': toDateTimeString
		}
	  , metadata
	)



def readTxtReport(file, encoding, delimiter):
	"""
	[String] file => [Iterator] positions, [Dictionary] meta data

	Read a Geneva report in txt file. The report is generated as below:

	1. Export in 'Comma Delimited' format from Geneva;
	2. The report is opened in Excel, then save as a text format:
		Text (tab delimited), Unicode Text, Csv (comma delimited)

	This function is to read "Text (tab delimited)" format.
	"""
	def fileToLines(fn, encoding):
		with codecs.open(fn, 'r', encoding=encoding) as file:
			for line in file:
				yield line


	stringToList = lambda delimiter, line: \
		line.strip().split(delimiter)

	
	return compose(
		lambda t: (t[0], getTxtMetadata(t[1]))
	  , readReport
	  , partial(map, partial(stringToList, delimiter))
	  , fileToLines
	)(file, encoding)



def getTxtMetadata(metadata):
	"""
	[Dictionary] raw metadata => [Dictionary] metadata

	Convert certain values in the raw meta data to a better format.
	"""

	# convert mm/dd/yyyy hh:mm date string to yyyy-mm-dd
	changeDateFormat = lambda s: \
		datetime.strptime(s, '%m/%d/%Y %H:%M').strftime('%Y-%m-%d')


	return \
	updateDictionaryWithFunction(
		{ 'PeriodEndDate': changeDateFormat
		, 'PeriodStartDate': changeDateFormat
		}
	  , metadata
	)