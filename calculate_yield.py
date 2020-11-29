# coding=utf-8
#
# From an inveestment report, give statistics on the number of unique investments
# in each category (except cash and FX Forward).
# 

from geneva.report import readInvestmentTxtReport, readProfitLossTxtReport
from utils.utility import allEquals
from toolz.functoolz import compose
from itertools import accumulate, count
from functools import partial
from os.path import join
import logging
logger = logging.getLogger(__name__)



def getYieldFromFiles( investmentFiles, profitLossFiles
					 , lastYearEndNavWithCash, lastYearEndNavWithoutCash
					 , impairment, cutoffMonth):
	"""

	"""
	sortedPLdata = sorted( map( partial(readProfitLossTxtReport, 'utf-16', '\t')
							  , profitLossFiles)
						 , key=lambda t: t[1]['PeriodEndDate'])
	
	sortedInvdata = sorted( map( partial(readInvestmentTxtReport, 'utf-16', '\t')
							   , investmentFiles)
						  , key=lambda t: t[1]['PeriodEndDate'])

	checkMetaData( list(map(lambda t: t[1], sortedPLdata))
				 , list(map(lambda t: t[1], sortedInvdata)))

	sortedPLPositions = list(map(lambda t: list(t[0]), sortedPLdata))
	sortedInvPositionsWithCutoff = \
		list(map( lambda t: (list(t[0]), getMetadataMonth(t[1]) <= cutoffMonth)
				, sortedInvdata))

	combine = lambda m1, m2: \
		map(lambda t: (*t[0], t[1]), zip(m1, m2))

	return combine( getAccumulatedReturn(sortedPLPositions, True)
				  , getAverageNav( sortedInvPositionsWithCutoff
				  				 , True, impairment, lastYearEndNavWithCash)
				  )




# [Dictionary] metadata => [Int] month of the period end date
getMetadataMonth = lambda m: \
	int(m['PeriodEndDate'].split('-')[1])



def checkMetaData(plMetadata, invMetadata):
	"""
	[List] plMetadata, [List] invMetadata
		=> [Int] 0 if nothing goes wrong, throw exception otherwise
	"""
	showMetadata = lambda metadataList: \
		'\n'.join(map( lambda m: '{0} {1} {2} {3}'.format(m['AccountingRunType'],
							m['Portfolio'], m['BookCurrency'], m['PeriodEndDate'])
					 , metadataList))

	logger.debug('checkMetaData(): {0}'.format(showMetadata(plMetadata + invMetadata)))


	if (len(plMetadata) != len(invMetadata)):
		logger.error('checkMetaData(): length inconsistent: {0}, \
						{1}'.format(len(plMetadata), len(invMetadata)))
		raise ValueError


	if not all(map( lambda m: m['AccountingRunType'] == 'ClosedPeriod'
				  , plMetadata + invMetadata)):
		logger.error('checkMetaData(): not all are of closed period')
		raise ValueError

	if not allEquals(map(lambda m: m['Portfolio'], plMetadata + invMetadata)):
		logger.error('checkMetaData(): inconsistent portfolio')
		raise ValueError

	if not allEquals(map(lambda m: m['BookCurrency'], plMetadata + invMetadata)):
		logger.error('checkMetaData(): inconsistent book currency')
		raise ValueError

	# if there are N metadata in plMetadata, then their month forms a 
	# set {1..N}
	monthCollection = lambda metadataList: \
		set(map(getMetadataMonth, metadataList))


	if not allEquals([ monthCollection(plMetadata)
					 , monthCollection(invMetadata)
					 , set(range(1, 1 + len(plMetadata)))
					 ]):
		logger.error('checkMetaData(): month collection invalid')
		raise ValueError


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
		[ (positions of month1, withCutoff)
		, (positions of month2, withCutoff)
		...
		]
	[Bool] withCash
	[Float] impairment
	[Float] lastYearEndNav

	=> [Iterator] average Nav per month

	NOTE: the lastYearEndNav must be consistent with the withCash switch.
"""
getAverageNav = compose(
	partial(map, lambda t: t[1]/t[0])
  , partial(filter, lambda t: t[0] > 1)
  , partial(zip, count(1))
  , lambda allPositions, withCash, impairment, lastYearEndNav: \
  		accumulate( map( lambda t: getNavFromPositions(withCash, t[1], impairment, t[0])
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
	investmentFiles = [ join('samples', 'investment positions 2020-01.txt')
					  , join('samples', 'investment positions 2020-02.txt')
					  , join('samples', 'investment positions 2020-03.txt')
					  , join('samples', 'investment positions 2020-04.txt')
					  , join('samples', 'investment positions 2020-05.txt')
					  , join('samples', 'investment positions 2020-06.txt')
					  , join('samples', 'investment positions 2020-07.txt')
					  , join('samples', 'investment positions 2020-08.txt')
					  , join('samples', 'investment positions 2020-09.txt')
					  , join('samples', 'investment positions 2020-10.txt')
					  ]

	profitLossFiles = [ join('samples', 'profit loss 2020-01.txt')
					  , join('samples', 'profit loss 2020-02.txt')
					  , join('samples', 'profit loss 2020-03.txt')
					  , join('samples', 'profit loss 2020-04.txt')
					  , join('samples', 'profit loss 2020-05.txt')
					  , join('samples', 'profit loss 2020-06.txt')
					  , join('samples', 'profit loss 2020-07.txt')
					  , join('samples', 'profit loss 2020-08.txt')
					  , join('samples', 'profit loss 2020-09.txt')
					  , join('samples', 'profit loss 2020-10.txt')]

	for x in getYieldFromFiles( investmentFiles, profitLossFiles
							  , 177801674041.66, 177800934590.20
							  , 3212689500.00, 7):
		print(x)