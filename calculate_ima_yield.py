# coding=utf-8
#
# Calculate yield (IMA)
# 

from geneva.report import readCashLedgerTxtReport \
						, readDailyInterestAccrualDetailTxtReport
from clamc_yield_report.ima import getTaxlotInterestIncome
from utils.file import getFiles
from toolz.functoolz import compose
from itertools import accumulate, filterfalse
from functools import partial
from os.path import join
from datetime import datetime
import logging
logger = logging.getLogger(__name__)


# 1. get list of CL files;
# 2. get list (period end date, positions)
# 3. sort by period end date;
# 4. getAccumulatedTimeWeightedCapital()



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



def getTaxlotList(dailyInterestPositions):
	"""
	[Iterable] dailyInterestPositions => [Set] tax lot Ids in the positions
	
	dailyInterestPositions: positions from daily interest report
	"""
	return set(map(lambda p: p['LotID'], dailyInterestPositions))



def getValuesWithoutCertainKeys(unwantedKeys, dictList):
	"""
	[Set] unwantedKeys,
	[Iterable] dictList ([Dictionary] String -> Float)
		=> [Iterable] (Float)
	"""
	return \
	compose(
		partial(map, lambda d: sum(d.values()))
	  , partial(map, partial(removeKeysFromDict, unwantedKeys))
	)(dictList)



def getAccumulatedFairValueChange(sortedTaxlotPLpositions):
	"""
	[Iterable] sortedTaxlotPLpositions
	=> [Iterable] ([Dictionary] String -> Float)

	Where sortedTaxlotPLpositions is an iterable over positions from profit 
	loss summary report with tax lot details, with the first element being
	positions of month 1, second element being positions of month 2, etc.
	"""
	return accumulate( map( getFairValueChange
						  , sortedTaxlotPLpositions)
					 , addDictValues)



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



def getAccumulatedRealizedGainLoss(sortedTaxlotPLpositions):
	"""
	[Iterable] sortedTaxlotPLpositions
	=> [Iterable] ([Dictionary] String -> Float)

	Where sortedTaxlotPLpositions is an iterable over positions from profit 
	loss summary report with tax lot details, with the first element being
	positions of month 1, second element being positions of month 2, etc.
	"""
	return accumulate( map( getRealizedGainLoss
						  , sortedTaxlotPLpositions)
					 , addDictValues)



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
	  , partial(filterfalse, lambda p: p['TaxLotId'] == '')
	)(taxlotPLpositions)



def getAccumulatedInterestIncome(sortedDailyInterestPositions):
	"""
	[Iterable] sortedDailyInterestPositions
	=> [Iterable] ([Dictionary] String -> Float)

	sortedDailyInterestPositions is an iterable over positons of daily
	interest accrual detail report, where the first element ispositions 
	of month 1, second element being positions of month 2, etc.
	"""
	return accumulate( map( getTaxlotInterestIncome
						  , sortedDailyInterestPositions)
					 , addDictValues
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




if __name__ == '__main__':
	import logging.config
	logging.config.fileConfig('logging.config', disable_existing_loggers=False)
