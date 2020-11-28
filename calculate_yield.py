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
	Requires Python version 3.8 or above

	[Iterator] allPositions, investment positions sorted by month, like:
		[positions of month1, positions of month2, ...]
	[Bool] withCash
	[Bool] withOffset
	[Float] impairment
	[Float] lastYearEndNav

	=> [Iterator] average Nav per month

	NOTE: the lastYearEndNav must be consistent with the withCash switch.
"""
getAverageNav = compose(
	partial(map, lambda t: t[1]/t[0])
  , partial(filter, lambda t: t[0] > 1)
  , partial(zip, count(1))
  , lambda allPositions, withCash, withOffset, impairment, lastYearEndNav: \
  		accumulate( map( partial(getNavFromPositions, withCash, withOffset, impairment)
				  	   , allPositions)
			  	  , lambda x, y: x + y
			  	  , initial=lastYearEndNav)
)



def getReturnFromPositions(withCash, positions):
	"""
	[Bool] withCash, [List] positions (profit loss) 
		=> [Tuple] realized return, total return
	"""
	realized = lambda p: \
		p['Interest'] + p['Dividend'] + p['OtherIncome'] + \
		p['RealizedPrice'] + p['RealizedFX'] + p['RealizedCross']

	unrealized = lambda p: \
		p['UnrealizedPrice'] + p['UnrealizedFX'] + p['UnrealizedCross']

	total = lambda p: \
		realized(p) + unrealized(p)

	intDvd = lambda p: \
		p['Interest'] + p['Dividend'] + p['OtherIncome']

	cashPosition = lambda p: \
		p['PrintGroup'] == 'Cash and Equivalents'

	CNEnergyPosition = lambda p: \
		p['PrintGroup'] == 'Corporate Bond' and 'CERCG ' in p['Description']


	realizedReturn = sum(map(realized, positions))
	totalReturn = sum(map(total, positions))


	return \
	( realizedReturn - sum(map(intDvd, filter(cashPosition, positions))) \
		- sum(map(intDvd, filter(CNEnergyPosition, positions)))
	, totalReturn - sum(map(intDvd, filter(cashPosition, positions))) \
		- sum(map(intDvd, filter(CNEnergyPosition, positions))) \
		- sum(map(unrealized, filter(CNEnergyPosition, positions)))
	) \
	if withCash else \
	( realizedReturn - sum(map(realized, filter(cashPosition, positions))) \
		- sum(map(intDvd, filter(CNEnergyPosition, positions)))
	, totalReturn - sum(map(total, filter(cashPosition, positions))) \
		- sum(map(intDvd, filter(CNEnergyPosition, positions))) \
		- sum(map(unrealized, filter(CNEnergyPosition, positions)))
	)



def getNavFromPositions(withCash, withOffset, impairment, positions):
	"""
	[Bool] withCash,
	[Bool] withOffset (meaning whether CN Energy interest income has been
		offset in this month)
	[Float] impairment
	[List] positions (investment positions)
		=> [Float] Nav
	"""
	marketValue = lambda p: \
		p['AccruedInterest'] + p['MarketValueBook']

	accruedInterest = lambda p: \
		p['AccruedInterest']

	CNEnergyPosition = lambda p: \
		p['SortKey'] == 'Corporate Bond' and 'CERCG ' in p['Description']

	cashPosition = lambda p: \
		p['LongShortDescription'] == 'Cash Long' and p['SortKey'] == 'Cash and Equivalents'


	total = sum(map(marketValue, positions))


	return \
	total - impairment \
	if withCash & withOffset else \
	total - sum(map(accruedInterest, filter(CNEnergyPosition, positions))) - impairment \
	if withCash & (not withOffset) else \
	total - sum(map(marketValue, filter(cashPosition, positions))) - impairment \
	if (not withCash) & withOffset else \
	total - sum(map(marketValue, filter(cashPosition, positions))) \
		- sum(map(accruedInterest, filter(CNEnergyPosition, positions))) - impairment



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