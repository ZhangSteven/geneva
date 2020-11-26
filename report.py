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
import logging
logger = logging.getLogger(__name__)



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
				  , getMetadata(pop(group))
				  )
  , partial(map, lambda el: el[1])
  , partial(filter, lambda el: el[0] == False)
  , lambda lines: groupby(lines, lambda line: len(line) == 0 or line[0] == '')
)



"""
	[String] file => [Iterable] lines

	Read a Geneva report in Excel file. The report is generated as export
	in 'Comma Delimited' format then saved as Excel (xlsx).
"""
excelFileToLines = lambda file: \
	worksheetToLines(open_workbook(file).sheet_by_index(0))



"""
	[String] file => [Iterator] positions, [Dictionary] metaData

	Read Geneva report (csv saved as Excel), returns two things

	1) meta data;
	2) raw positions;
"""
readExcelReport = compose(
	readReport
  , excelFileToLines
)



toDateTimeString = lambda f: \
	fromExcelOrdinal(f).strftime('%Y-%m-%d')


toStringIfFloat = lambda x: \
	str(int(x)) if isinstance(x, float) else x


getCurrentDirectory = lambda : \
	dirname(abspath(__file__))



def getMetadata(lines):
	"""
	[Iterable] lines => [Dictionary] meta data.

	"""
	updateFields = { 'Portfolio': toStringIfFloat
				   , 'PeriodEndDate': toDateTimeString
				   , 'PeriodStartDate': toDateTimeString
				   }

	d = dict(map( lambda line: (line[0], line[1]) if len(line) > 1 else (line[0], '')
				, lines))

	for key in d:
		if key in updateFields:
			d[key] = updateFields[key](d[key])

	return d



def getRawPositions(lines):
	"""
	[Iterable] lines => [List] Raw Positions

	Assume: each line is an iterator over its columns.
	"""
	getHeadersFromLine = compose(
		list
	  , partial(takewhile, lambda s: s.strip() != '')
	  , partial(map, str)
	)

	return \
	compose(
		list
	  , partial(map, dict)
	  , lambda t: map(partial(zip, t[0]), t[1])
	  , lambda lines: (getHeadersFromLine(pop(lines)), lines)
	)(lines)