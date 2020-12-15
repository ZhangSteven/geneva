# coding=utf-8
#
# Cross interest income per tax lot with interest per position.
# 

from geneva.report import readProfitLossTxtReport \
						, readDailyInterestAccrualDetailTxtReport \
						, excelFileToLines, getRawPositions
# from clamc_yield_report.ima import getTaxlotInterestIncome
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


# 1. Get [Dictioanry] investId -> interest income; take out those without interest income (zero coupon etc.)
# 2. Get [Dictionary] investId -> [List] tax lot id; take out those event id.
# 3. Get [Dictionary] tax lot id -> [Float] interest income; take out those without interest income (events)
# 4. From (2), (3) calculate [Dictionary] investId -> interest income;
# 5. Produce csv: investId, interest income (1), interest income (4), tax lot ids.



def getInterestIncomeFromPL(profitLossFile):
	"""
	[String] profitLossFile => [Dictionary] investId -> interest income
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



def getInterestIncomeTaxLot(taxlotInterestIncomeFile):
	"""
	[String] taxlotInterestIncomeFile => [Dictionary] tax lot id -> interest income
	
	Excluding tax lot ids whose interest income = 0.
	"""
	def updateDict(d):
		d['tax lot id'] = str(int(d['tax lot id']))
		return d


	return \
	compose(
		dict
	  , partial(filterfalse, lambda t: t[1] == 0)
	  , partial( map
	  		   , lambda d: ( d['tax lot id']
	  		   			   , d['ending ai'] - d['starting ai'] + d['interest received']
	  		   			   )
	  		   )
	  , partial(map, updateDict)
	  , getRawPositions
	  , excelFileToLines
	)(taxlotInterestIncomeFile)



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



if __name__ == '__main__':
	import logging.config
	logging.config.fileConfig('logging.config', disable_existing_loggers=False)

	# profitLossFile = join('samples', 'profit loss 2020-01.txt')
	# print(list(getInterestIncomeFromPL(profitLossFile)))

	# taxlotInterestIncomeFile = join('samples', 'tax_lot_id_2020-01.xlsx')
	# taxLotInterestIncome = getInterestIncomeTaxLot(taxlotInterestIncomeFile)
	# print(len(taxLotInterestIncome))
	# print(taxLotInterestIncome)

	# dailyInterestFile = join('samples', 'daily interest 2020-01.txt')
	# taxlotMapping = getInvestIdTaxlotMapping(dailyInterestFile)
	# print(taxlotMapping)

	profitLoss = getInterestIncomeFromPL(
					join('samples', 'profit loss 2020-01.txt'))

	taxLotInterestIncome = getInterestIncomeTaxLot(
								join('samples', 'tax_lot_id_2020-01.xlsx'))

	taxlotMapping = getInvestIdTaxlotMapping(
						join('samples', 'daily interest 2020-01.txt'))

	sumTaxlotInterestIncome = lambda taxlotMapping, taxLotInterestIncome, investId: \
	compose(
		sum
	  , partial(map, lambda taxlotId: taxLotInterestIncome[taxlotId])
	  , lambda investId: taxlotMapping[investId]
	)(investId)


	getTaxLotIds = lambda taxlotMapping, investId: \
		' '.join(taxlotMapping[investId])


	outcomeRow = lambda plEntry: \
		( plEntry[0]
		, plEntry[1]
		, sumTaxlotInterestIncome(taxlotMapping, taxLotInterestIncome, plEntry[0])
		, getTaxLotIds(taxlotMapping, plEntry[0])
		)


	addDelta = lambda t: \
		(t[0], t[1], t[2], t[1]-t[2], t[3])


	writeCsv( 'tax lot cross check.csv'
			, chain( [('InvestId', 'Interst Income', 'Interest Income Tax Lot', 'Difference', 'Tax Lots')]
				   , map(addDelta, map(outcomeRow, profitLoss)))
			, delimiter=','
			)



