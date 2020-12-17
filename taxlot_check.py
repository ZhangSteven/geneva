# coding=utf-8
#
# Cross check interest income per tax lot from daily interest accrual
# detail report with interest income per position from profit loss
# report.
# 

from geneva.report import readProfitLossTxtReport \
						, readDailyInterestAccrualDetailTxtReport \
						, excelFileToLines, getRawPositions
from clamc_yield_report.ima import getTaxlotInterestIncome
from utils.utility import writeCsv
from toolz.functoolz import compose
from toolz.itertoolz import groupby as groupbyToolz
from toolz.dicttoolz import valmap
from itertools import accumulate, filterfalse, chain
from functools import partial
from os.path import join
from datetime import datetime
import logging
logger = logging.getLogger(__name__)



def getInterestIncomeFromPL(profitLossFile):
	"""
	[String] profitLossFile => [Iterable] (investId, interest income)
	"""

	# handle special case "XS1505143393 HTM TEST"
	updateInvestId = lambda investId: \
		investId[:-5] if investId.endswith(' TEST') else investId


	return \
	compose(
		partial(filterfalse, lambda t: t[1] == 0)
	  , partial(map, lambda p: (updateInvestId(p['Invest']), p['Interest']))
	  , partial(filter, lambda p: 'Bond' in p['PrintGroup'])
	  , lambda t: t[0]
	  , partial(readProfitLossTxtReport, 'utf-16', '\t')
	)(profitLossFile)



def getInvestIdTaxlotMapping(dailyInterestFile):
	"""
	[String] dailyInterestFile => [Dictioanry] investId -> [Set] tax lot ids
	"""
	getInvestId = lambda rawId: \
		rawId[:16] if ' HTM ' in rawId else rawId[:12]


	return \
	compose(
		partial(valmap, lambda value: set(map(lambda t: t[1], value)))
	  , partial(groupbyToolz, lambda t: t[0])
	  , partial( map
	  		   , lambda p: ( getInvestId(p['Investment'])
	  		   			   , p['LotID']
	  		   			   )
	  		   )
	  , partial(filterfalse, lambda p: p['LotSumOfPurSoldPaidRecLocal'] > 0)
	  , lambda t: t[0]
	  , partial(readDailyInterestAccrualDetailTxtReport, 'utf-16', '\t')
	)(dailyInterestFile)



def writeComparisonCsv(month):
	"""
	[Int] month => [String] csv output

	Side effect: write csv output file showing the difference between position
	level interest income and sum of tax lot level interest income.
	"""
	toString = lambda x: '0' + str(x) if x < 10 else str(x)

	profitLossFile = join('samples', 'profit loss 2020-' + toString(month) + '.txt')
	dailyInterestFile = join('samples', 'daily interest 2020-' + toString(month) + '.txt')

	sumTaxlotInterestIncome = lambda taxlotMapping, taxLotInterestIncome, investId: \
	compose(
		sum
	  , partial(map, lambda taxlotId: taxLotInterestIncome[taxlotId])
	  , lambda investId: taxlotMapping[investId]
	)(investId)


	getTaxLotIds = lambda taxlotMapping, investId: \
		' '.join(taxlotMapping[investId])


	"""
		[Tuple] (investId, interest income) 
		=> [Tuple] (investId, interest income, interest income of all tax lots, tax lot list)
	"""
	outcomeRow = lambda taxlotMapping, taxLotInterestIncome, plEntry: \
		( plEntry[0]
		, plEntry[1]
		, sumTaxlotInterestIncome(taxlotMapping, taxLotInterestIncome, plEntry[0])
		, getTaxLotIds(taxlotMapping, plEntry[0])
		)


	"""
		[Tuple] (investId, interest income, interest income of all tax lots, tax lot list)
		=> [Tuple] ( investId, interest income, interest income of all tax lots
				   , difference between the two, tax lot list)
	"""
	addDelta = lambda t: \
		(t[0], t[1], t[2], t[1]-t[2], t[3])


	return \
	writeCsv( 'tax lot cross check 2020-' + toString(month) + '.csv'
			, chain( [('InvestId', 'Interst Income', 'Interest Income Tax Lot', 'Difference', 'Tax Lots')]
				   , map( addDelta
				   		, map( partial( outcomeRow
				   					  , getInvestIdTaxlotMapping(dailyInterestFile)
				   					  , getTaxlotInterestIncome(
											list(readDailyInterestAccrualDetailTxtReport(
													'utf-16', '\t', dailyInterestFile)[0]))
				   					  )
				   			 , getInterestIncomeFromPL(profitLossFile)))
				   )
			, delimiter=','
			)




if __name__ == '__main__':
	import logging.config
	logging.config.fileConfig('logging.config', disable_existing_loggers=False)

	for n in range(1, 12):
		print(writeComparisonCsv(n))

	# writeComparisonCsv(9)	# error