# coding=utf-8
#
# Calculate yield (IMA)
# 

from geneva.report import readCashLedgerTxtReport, readTaxlotTxtReport \
						, readDailyInterestAccrualDetailTxtReport \
						, readProfitLossSummaryWithTaxLotTxtReport
from geneva.calculate_yield import getFilesWithFilterFunc
from clamc_yield_report.ima import getTaxlotInterestIncome
from utils.file import getFiles
from utils.utility import writeCsv
from toolz.functoolz import compose
from itertools import accumulate, filterfalse, chain, count
from functools import partial
from os.path import join
from datetime import datetime
import logging
logger = logging.getLogger(__name__)



"""
	[Dictionary] d1 (String -> Float)
	[Dictionary] d2 (String -> Float)
		=> [Dictionary] d (String -> Float)
"""
addDictValues = lambda d1, d2: \
	{key: d1.get(key, 0) + d2.get(key, 0) for key in set(d1.keys()).union(set(d2.keys()))}



"""
	[Set] unwanted keys, [Dictionary] d
		=> [Dictioanry] d without those keys
"""
removeKeysFromDict = lambda unwantedKeys, d: \
	{k: v for (k, v) in d.items() if not k in unwantedKeys}



def getAccumulatedValue(mappingFunc, unwantedKeys, inputList):
	"""
	[Set] ([String] unwantedKeys),
	[Function] Iterable -> [Dictionary] [String] key -> [Float] value
	[Iterable] inputList, whose elements are positions of from the 
		below reports, from month 1, 2...n

		1. Profit Loss summary with tax lot details;
		2. Daily interest accrual detail;

	=> [Iterable] ([Dictionary] key -> value)
	"""
	return \
	compose(
		lambda values: accumulate(values, addDictValues)
	  , partial(map, partial(removeKeysFromDict, unwantedKeys))
	  , partial(map, mappingFunc)
	)(inputList)



def getFairValueChange(taxlotPLpositions):
	"""
	[Iterable] sortedTaxlotPLpositions
	=> [Iterable] ([Dictionary] String -> Float)

	taxlotPLpositions: positions from profit loss summary report with
	tax lot details.

	Output a dictionary mapping tax lot Id -> unrealized gain loss of the
	tax lot.

	Note cash lots (tax lot id = '') are ignored.
	"""
	return \
	compose(
		dict
	  , partial( map
	  		   , lambda p: ( p['TaxLotId']
	  					   , p['UnrealGLPrice_taxlot']+p['UnrealFX_taxlot'])
	  		   )
	  , partial( filter
	  		   , lambda p: 'Bond' in p['Group1'] and not p['Group2'] == 'Held to Maturity')
	)(taxlotPLpositions)



"""
	[Set] unwanted tax lot Ids
	[Iterable] sortedTaxlotPLpositions
	=> [Iterable] ([Dictionary] tax lot id -> accumulated fair value change)

	Where sortedTaxlotPLpositions is an iterable over positions from profit 
	loss summary report with tax lot details, with the first element being
	positions of month 1, second element being positions of month 2, etc.
"""
getAccumulatedFairValueChange = partial(
	getAccumulatedValue
  , getFairValueChange
)



def getRealizedGainLoss(taxlotPLpositions):
	"""
	[Iterable] taxlotPLpositions => [Dictionary] (String -> Float)

	taxlotPLpositions: positions from profit loss summary report with
	tax lot details.

	Output a dictionary mapping tax lot Id -> realized gain loss of the
	tax lot.

	Note cash lots (tax lot id = '') are ignored.
	"""
	return \
	compose(
		dict
	  , partial( map
	  		   , lambda p: ( p['TaxLotId']
	  					   , p['RealGLPrice_taxlot']+p['RealFX_taxlot'])
	  		   )
	  , partial(filter, lambda p: 'Bond' in p['Group1'])
	)(taxlotPLpositions)



"""
	[Set] unwanted tax lots,
	[Iterable] sortedTaxlotPLpositions
	=> [Iterable] ([Dictionary] tax lot id -> accumulated realized return)

	Where sortedTaxlotPLpositions is an iterable over positions from profit 
	loss summary report with tax lot details, with the first element being
	positions of month 1, second element being positions of month 2, etc.
"""
getAccumulatedRealizedGainLoss = partial(
	getAccumulatedValue
  , getRealizedGainLoss
)



"""
	[Set] unwanted tax lots,
	[Iterable] sortedDailyInterestPositions
	=> [Iterable] ([Dictionary] tax lot id -> accmulated interest income)

	sortedDailyInterestPositions is an iterable over positons of daily
	interest accrual detail report, where the first element ispositions 
	of month 1, second element being positions of month 2, etc.
"""
getAccumulatedInterestIncome = partial(
	getAccumulatedValue
  , getTaxlotInterestIncome
)



def getAccumulatedTimeWeightedCapital(sortedCLPositions):
	"""
	[Iterable] ([String] period end date, [List] positions of that period)
	=> [Iterable] Float (time weighted return at each period end date)

	"""
	return map( lambda t: getTimeWeightedCapital(t[0], t[1])
			  , accumulate( sortedCLPositions
	  		   			  , lambda t1, t2: (t2[0], t1[1] + t2[1])))



def getTimeWeightedCapital(reportDate, positions):
	"""
	[String] report date (yyyy-mm-dd),
	[List] cash leger positions,
		=> [Float] time weighted capital
	"""
	stringToDate = lambda d: \
		datetime.strptime(d, '%Y-%m-%d')


	# [String] day1 (yyyy-mm-dd), [String] day2 (yyyy-mm-dd) => [Int] days
	getDaysDifference = lambda day1, day2: \
		(stringToDate(day2) - stringToDate(day1)).days


	"""
		[String] report date (yyyy-mm-dd),
		[Iterable cash ledger positions
			=> [Float] time weighted capital

		Calculate time weighted capital for internal cash flow, i.e., bond mature
	"""
	getTimeWeightAmountInternalCF = lambda reportDate, positions: \
	compose(
		sum
	  , partial( map
	  		   , lambda p: p['BookAmount'] * getDaysDifference(p['CashDate'], reportDate)/365.0)
	  , partial(filter, lambda p: p['TranDescription'] == 'Mature')
	)(positions)


	"""
		[String] report date (yyyy-mm-dd),
		[Iterable cash ledger positions
			=> [Float] time weighted capital

		Calculate time weighted capital for external cash flow, i.e., deposit
		and withdrawal
	"""
	getTimeWeightAmountExternalCF = lambda reportDate, positions: \
	compose(
		sum
	  , partial( map
	  		   , lambda p: p['BookAmount'] * (getDaysDifference(p['CashDate'], reportDate) + 1)/365.0)
	  , partial(filter, lambda p: p['TranDescription'] in ['Deposit', 'Withdraw'])
	)(positions)


	return getTimeWeightAmountInternalCF(reportDate, positions) \
		 + getTimeWeightAmountExternalCF(reportDate, positions)



"""
	[Configure Object] config 
		=> [Set] tax lots that belong to CN Energy Bond
"""
getCNEnergyTaxlots = lambda config: \
	set(map(lambda s: s.strip(), config['DefaultBond']['taxlots'].split(',')))



"""
	[Configure Object] config
		=> [String] input directory
"""
getInputDirectory = lambda config: \
	config['Input']['dataDirectory']



"""
	[Config Object] config, [String] tax lot appraisal report
	=> [Set] tax lot ids

	Combine tax lot ids (non cash) that appear in the tax lot appraisal
	report and those from the config object, return them as a set.
"""
getUnwantedTaxLots = lambda config, lastYearTaxLotAppraisalFile: \
compose(
	lambda s: getCNEnergyTaxlots(config).union(s)
  , set
  , partial(filterfalse, lambda el: el == '')
  , partial(map, lambda p: p['TaxLotID'])
  , lambda t: t[0]
  , partial(readTaxlotTxtReport, 'utf-16', '\t')
)(lastYearTaxLotAppraisalFile)



"""
	[Iterable] dailyInterestPositions => [Set] tax lot Ids in the positions
	
	dailyInterestPositions: positions from daily interest report
"""
getTaxlotList = lambda dailyInterestPositions: \
	set(map(lambda p: p['LotID'], dailyInterestPositions))



getAccumulatedRealizedGainLossFromFiles = compose(
	list
  , partial(map, lambda d: sum(d.values()))
  , partial(getAccumulatedRealizedGainLoss, set())
  , partial(map, lambda t: t[0])
  , partial( map
		   , partial(readProfitLossSummaryWithTaxLotTxtReport, 'utf-16', '\t'))
)



"""
	[Configure Object] config => [Iterable] profit loss summary files
"""
getProfitLossSummaryFiles = lambda config: \
getFilesWithFilterFunc(
	lambda fn: fn.startswith('profit loss summary tax lot') and fn.endswith('.txt')
  , getInputDirectory(config)
)



"""
	[Configure Object] config => [Iterable] profit loss summary files
"""
getCashLedgerFiles = lambda config: \
getFilesWithFilterFunc(
	lambda fn: fn.startswith('cash ledger') and fn.endswith('.txt')
  , getInputDirectory(config)
)



"""
	[String] directory => [Iterable] profit loss summary files
"""
getDailyInterestAccrualFiles = lambda config: \
getFilesWithFilterFunc(
	lambda fn: fn.startswith('daily interest') and fn.endswith('.txt')
  , getInputDirectory(config)
)



def adjustInterestIncome(accumulatedInterestIncome):
	"""
	[Iterable] accumulated interest income (since month 1)
	=> [Iterable] accumulated interest income (since month 1)

	The point is to make interest income adjustment for the below
	tax lots on and after month 8:

	Lot 	 Adjustment
	1075473	 (1,555,402.64)
	1117941	 (408,489.58)
	1117942	 (691,290.07)
	1118109	 (408,489.58)
	1118110	 (408,489.58)

	"""
	adjustment = { '1075473': -1555402.64
				 , '1117941': -408489.58
				 , '1117942': -691290.07
				 , '1118109': -408489.58
				 , '1118110': -408489.58
				 }

	# [Dictionary] tax lot id => interest income => [Dictionary] id -> income
	adjustDict = compose(
		dict
	  , partial( map
	  		   , lambda t: (t[0], t[1] + adjustment[t[0]]) \
	  		   		if t[0] in adjustment else t
	  		   )
	  , lambda d: d.items()
	)


	return \
	compose(
		partial(map, lambda t: adjustDict(t[1]) if t[0] > 7 else t[1])
	  , partial(zip, count(1))
	)(accumulatedInterestIncome)




if __name__ == '__main__':
	import logging.config
	logging.config.fileConfig('logging.config', disable_existing_loggers=False)

	import configparser
	config = configparser.ConfigParser()
	config.read('calculate_ima_yield.config')

	lastYearTaxLotAppraisalFile = join('samples', '12xxx tax lot 2019-12-31.txt')
	unwantedTaxLots = getUnwantedTaxLots(config, lastYearTaxLotAppraisalFile)
	# print(unwantedTaxLots)

	sortedPLdata = sorted( map( partial( readProfitLossSummaryWithTaxLotTxtReport
									   , 'utf-16', '\t')
							  , getProfitLossSummaryFiles(config))
						 , key=lambda t: t[1]['PeriodEndDate'])

	sortedTaxlotPLpositions = list(map(lambda t: list(t[0]), sortedPLdata))

	accumulatedRealizedGL = compose(
		list
	  , partial(getAccumulatedRealizedGainLoss, unwantedTaxLots)
	)(sortedTaxlotPLpositions)

	accumulatedFairValueChange = compose(
		list
	  , partial(getAccumulatedFairValueChange, unwantedTaxLots)
	)(sortedTaxlotPLpositions)


	sortedInterestData = \
		sorted( map( partial( readDailyInterestAccrualDetailTxtReport
							, 'utf-16', '\t')
				   , getDailyInterestAccrualFiles(config))
			  , key=lambda t: t[1]['PeriodEndDate'])

	sortedDailyInterestPositions = map(lambda t: list(t[0]), sortedInterestData)

	accumulatedInterestIncome = compose(
		list
	  , adjustInterestIncome
	  , partial(getAccumulatedInterestIncome, unwantedTaxLots)
	)(sortedDailyInterestPositions)


	timeWeightedCapital = compose(
		list
	  , getAccumulatedTimeWeightedCapital
	  , partial(sorted, key=lambda t: t[0])
	  , partial(map, lambda t: (t[1]['PeriodEndDate'], list(t[0])))
	  , partial(map, partial(readCashLedgerTxtReport, 'utf-16', '\t'))
	  , getCashLedgerFiles
	)(config)


	addValues = lambda d: sum(d.values())
	compose(
		partial(writeCsv, 'ima result.csv')
	  , partial(chain, [('interest income', 'realized gain', 'fair value change', 'time weighted capital')])
	  , partial( map
	  		   , lambda t: (addValues(t[0]), addValues(t[1]), addValues(t[2]), t[3]))
	  , lambda: zip( accumulatedInterestIncome
	  			   , accumulatedRealizedGL
	  			   , accumulatedFairValueChange
	  			   , timeWeightedCapital)
	)()