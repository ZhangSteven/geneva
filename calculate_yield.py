# coding=utf-8
#
# From an inveestment report, give statistics on the number of unique investments
# in each category (except cash and FX Forward).
# 

from geneva.report import readInvestmentTxtReport, readProfitLossTxtReport
from itertools import accumulate, count
from functools import partial
from toolz.functoolz import compose
import logging
logger = logging.getLogger(__name__)



def getYieldFromFiles( investmentFiles, profitLossFiles, lastYearEndInvestmentFile
					 , impairment, cutoffMonth):
	"""
	1. get metadata and positions;
	2. check metadata;
	3. get return and nav data;
	4. calculate return rate;
	5. output csv.
	"""

	return 0



"""
	[Iterator] allPositions, profit loss positions sorted by month, like:
		[positions of month1, positions of month2, ...]
	[Bool] withCash

	=> [Iterator] ( accumulated realized return
				  , accumulated total return
				  )
"""
getAccumulatedReturn = lambda allPositions, withCash: \
	accumulate( map( partial(getReturnFromPositions, withCash)
				   , allPositions)
			  , lambda t1, t2: (t1[0] + t2[0], t1[1] + t2[1]))



"""
	NOTE: requires Python version 3.8

	[Iterator] allPositions, investment positions sorted by month, like:
		[positions of month1, positions of month2, ...]
	[Bool] withCash
	[Int] cutoffMonth
	[Float] impairment
	[Float] lastYearEndNav

	=> [Iterator] average Nav per month
"""
getAverageNav = compose(
	partial(map, lambda t: t[1]/t[0])
  , partial(filter, lambda t: t[0] > 1)
  , partial(zip, count(1))
  , lambda allPositions, withCash, cutoffMonth, impairment, lastYearEndNav: \
  		accumulate( map( partial(getNavFromPositions, withCash, cutoffMonth, impairment)
				  	   , allPositions)
			  	  , lambda x, y: x + y
			  	  , initial=lastYearEndNav)
)



def getReturnFromPositions(withCash, posiitons):
	return (1, 2)



def getNavFromPositions(withCash, cutoffMonth, impairment, posiitons):
	return 60



def showTupleList(L):
	for t in L:
		for x in t:
			print(x, end=' ')

		print('')



# getCsvFilename = lambda metaData: \
# 	'investment types ' + metaData['Portfolio'] + ' ' + metaData['PeriodEndDate'] + '.csv'



"""
	[String] filename, [Dictionary] typeCount => [String] output csv name
"""
# writeOutputCsv = lambda filename, typeCount: \
# 	writeCsv( filename
# 			, chain( [('InvestmentType', 'UniquePositionCount')]
# 				   , typeCount.items())
# 			)




if __name__ == '__main__':
	import logging.config
	logging.config.fileConfig('logging.config', disable_existing_loggers=False)

	# import argparse
	# parser = argparse.ArgumentParser(description='Give statistics of investment types')
	# parser.add_argument( 'file', metavar='file', type=str
	# 				   , help='investment position report')


	"""
		Generate an investment position report, then:

		$python count_investment.py <file name with path>

		Example:

		$python count_investment.py samples/investment01.xlsx

	"""
	# positions, metaData = readExcelReport(parser.parse_args().file)
	# print(writeOutputCsv(getCsvFilename(metaData), count(positions)))

	showTupleList(getAccumulatedReturn(range(5), True))
	for x in getAverageNav(range(5), True, 0, 0, 120):
		print(x)