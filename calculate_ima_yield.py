# coding=utf-8
#
# Calculate yield (IMA)
# 

from geneva.report import readCashLedgerTxtReport, readTaxlotTxtReport \
						, readDailyInterestAccrualDetailTxtReport \
						, readProfitLossSummaryWithTaxLotTxtReport \
						, readTxtReport
from geneva.calculate_yield import getFilesWithFilterFunc, moveFiles \
								, sendNotificationEmail, getProcessedDirectory
from geneva.utility import getImaDataDirectory, getUserConfigFile
# from clamc_yield_report.ima import getTaxlotInterestIncome
from geneva.constants import Constants
from steven_utils.file import getFiles
from steven_utils.utility import mergeDict, allEquals, writeCsv
from toolz.functoolz import compose
from toolz.itertoolz import groupby as groupbyToolz
from toolz.dicttoolz import valmap
from itertools import accumulate, filterfalse, chain, count
from functools import partial, reduce
from os.path import join
from datetime import datetime
import logging, configparser
logger = logging.getLogger(__name__)



def run(dataDirectory, userConfigFile):
	"""
	[String] data directory,
	[String] user config file
	"""
	logger.debug('run(): start')

	purchaseSalesFiles = list(getPurchaseSalesFiles(dataDirectory))
	cashLedgerFiles = list(getCashLedgerFiles(dataDirectory))
	profitLossSummaryFiles = list(getProfitLossSummaryFiles(dataDirectory))
	dailyInterestAccrualFiles = list(getDailyInterestAccrualFiles(dataDirectory))

	if any([ len(purchaseSalesFiles) == 0
		   , len(cashLedgerFiles) == 0
		   , len(profitLossSummaryFiles) == 0
		   , len(dailyInterestAccrualFiles) == 0]):
		logger.debug('no input files')
		return

	if len(purchaseSalesFiles) > 1:
		logger.error('too many purchase sale file: {0}'.format(len(purchaseSalesFiles)))
		return

	if not allEquals([ len(cashLedgerFiles)
					 , len(profitLossSummaryFiles)
					 , len(dailyInterestAccrualFiles)]):
		logger.error('inconsistent number of files')
		return

	status, message = handleInputFiles( purchaseSalesFiles[0], cashLedgerFiles
									  , profitLossSummaryFiles, dailyInterestAccrualFiles
									  , dataDirectory, userConfigFile)
	sendNotificationEmail('IMA Yield Calculation', status, message)
	processedDirectory = getProcessedDirectory(dataDirectory)
	moveFiles(processedDirectory, purchaseSalesFiles)
	moveFiles(processedDirectory, cashLedgerFiles)
	moveFiles(processedDirectory, profitLossSummaryFiles)
	moveFiles(processedDirectory, dailyInterestAccrualFiles)



def handleInputFiles( purchaseSalesFile, cashLedgerFiles, profitLossSummaryFiles
					, dailyInterestAccrualFiles, dataDirectory, userConfigFile):
	"""
	[List] purchase sales files,
	[List] cash ledger files,
	[List] profit loss summary files,
	[List] daily interest accrual files,
	[String] user config file
		=> [Tuple] ([Int] status, [String] message)
	"""
	logger.debug('handleInputFiles()')
	addValues = lambda d: sum(d.values())

	try:
		config = configparser.ConfigParser()
		config.read(join(dataDirectory, userConfigFile))
		outputFile = join(dataDirectory, 'ima result.csv')

		compose(
			partial(writeCsv, outputFile)
		  , partial(chain, [ ( 'interest income', 'realized gain', 'realized return rate'
		  				   	 , 'fair value change', 'total return rate', 'time weighted capital')]
		  		   )
		  , partial( map
		  		   , lambda t: ( t[0], t[1], (t[0]+t[1])/t[3]*100 if t[3] != 0 else ''
		  		   			   , t[2], (t[0]+t[1]+t[2])/t[3]*100 if t[3] != 0 else '', t[3])
		  		   )
		  , partial( map
		  		   , lambda t: (addValues(t[0]), addValues(t[1]), addValues(t[2]), t[3]))
		  , lambda t: zip(*t)
		  , getResultFromFiles

		)( purchaseSalesFile
		 , cashLedgerFiles
		 , profitLossSummaryFiles
		 , dailyInterestAccrualFiles
		 , config['Input']['userAllTaxlots']=='True'
		 , config['Input']['bondConnect']=='True'
		 )

		return (Constants.SUCCESS, 'output file:\n{0}'.format(outputFile))

	except:
		logger.exception('run():')
		return (Constants.FAILURE, '')



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
keepKeysFromDict = lambda wantedKeys, d: \
	{k: v for (k, v) in d.items() if k in wantedKeys}



def getAccumulatedValue(mappingFunc, wantedKeys, inputList):
	"""
	[Set] ([String] wantedKeys),
	[Function] Iterable -> [Dictionary] [String] key -> [Float] value
	[Iterable] inputList, whose elements are positions of from the 
		below reports, from month 1, 2...n

		1. Profit Loss summary with tax lot details;
		2. Daily interest accrual detail;

	=> [Iterable] ([Dictionary] key -> value)

	if wantedKeys parameter is None, then no filtering is done.
	"""
	return \
	compose(
		lambda values: accumulate(values, addDictValues)
	  , partial(map, partial(keepKeysFromDict, wantedKeys))
	  , partial(map, mappingFunc)
	)(inputList) \
	if wantedKeys != None else \
	compose(
		lambda values: accumulate(values, addDictValues)
	  , partial(map, mappingFunc)
	)(inputList)



def getTaxlotInterestIncome(dailyInterestPositions):
	"""
	Kicoo's simplified method of getting the interest income.
	When using this method, please also turn off the function
	adjustInterestIncome()

	[Iterable] dailyInterestPositions => [Dictionary] tax lot id -> interest income
	
	Note that both the tax lots and event lots (such as sell, mature, coupon) will
	be kept.

	This means CERCG will also be filtered out because on the coupon date, fund
	accounting will book a negative interest income.
	"""
	addup = lambda positions: \
		sum(map(lambda p: p['LotSumOfChangeInAIBook'], positions))

	return \
	compose(
		partial(valmap, addup)
	  , partial(groupbyToolz, lambda p: p['LotID'])
	  , partial(filter, lambda p: p['LotSumOfChangeInAIBook'] > 0)
	  , partial(filter, lambda p: p['LotQuantity'] > 0)
	)(dailyInterestPositions)



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
	isHTM = lambda investId: \
		' HTM' in investId

	return \
	compose(
		dict
	  , partial( map
	  		   , lambda p: ( p['TaxLotId']
	  					   , p['UnrealGLPrice_taxlot']+p['UnrealFX_taxlot'])
	  		   )
	  , partial( filter
	  		   , lambda p: 'Bond' in p['Group1'] and not isHTM(p['Invest']))
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



def getAccumulatedTimeWeightedCapital(bondConnectOnly, sortedCLPositions):
	"""
	[Bool] bondConnectOnly
	[Iterable] ([String] period end date, [List] positions of that period)
	=> [Iterable] Float (time weighted return at each period end date)

	"""

	"""
		[Iterable] cash ledger entries => [Iterable] cash ledger entries

		filter and change the entries for bond connect calculation.
	"""
	mappingFunc = compose(
		partial( map 
			   , lambda p: mergeDict(p, {'TranDescription': 'Deposit'}) \
					if p['TranDescription'] == 'Transfer' else p
			   )
	  , partial( filter
			   , lambda p: 'BOCHK_BC' in p['GroupWithinCurrency_OpeningBalDesc']
			   )
	)


	return \
	compose(
		partial(map, lambda t: getTimeWeightedCapital(t[0], t[1]))
	  , partial(map, lambda t: (t[0], list(mappingFunc(t[1])))) \
	  	if bondConnectOnly else partial(map, lambda t: t)
	  , lambda sortedCLPositions: \
	  		accumulate(sortedCLPositions, lambda t1, t2: (t2[0], t1[1] + t2[1]))
	)(sortedCLPositions)



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
	  , partial(filter, lambda p: p['TranDescription'] in ['Mature', 'Paydown', 'Sell'])
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
	[String] purchase sales report
	=> [Set] tax lot ids

	Get tax lot ids that are bought from a purchase sales report, 
	return them as a set.

	Cash ledger report can serve a similar purpose, but it does not
	include unsettled trades.
"""
getPurchasedTaxlots = lambda purchaseSalesFile: \
compose(
 	set
  , partial(map, lambda p: p['TranID'])
  , partial(filter, lambda p: p['TranType'] == 'Buy')
  , lambda t: t[0]
  , partial(readTxtReport, 'utf-16', '\t')
)(purchaseSalesFile)



"""
	[String] profit loss summary report
	=> [Set] tax lot ids

	Get tax lot ids that are bought from a purchase sales report, 
	return them as a set.

	Cash ledger report can serve a similar purpose, but it does not
	include unsettled trades.
"""
getBondConnectTaxlots = compose(
	set
  , partial(map, lambda p: p['TaxLotId'].split(':')[-1].strip())
  , partial(filter, lambda p: 'CLO BondConnect_internal ref.' in p['Group2'])
  , lambda t: t[0]
  , partial(readProfitLossSummaryWithTaxLotTxtReport, 'utf-16', '\t')
)



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
	[String] directory => [Iterable] profit loss summary files
"""
getProfitLossSummaryFiles = lambda directory: \
getFilesWithFilterFunc(
	lambda fn: fn.startswith('profit loss summary') and fn.endswith('.txt')
  , directory
)



"""
	[String] directory => [Iterable] cash ledger files
"""
getCashLedgerFiles = lambda directory: \
getFilesWithFilterFunc(
	lambda fn: fn.startswith('cash ledger') and fn.endswith('.txt')
  , directory
)



"""
	[String] directory => [Iterable] daily interest accrual files
"""
getDailyInterestAccrualFiles = lambda directory: \
getFilesWithFilterFunc(
	lambda fn: fn.startswith('daily interest') and fn.endswith('.txt')
  , directory
)



"""
	[String] directory => [Iterable] purchase sales files
"""
getPurchaseSalesFiles = lambda directory: \
getFilesWithFilterFunc(
	lambda fn: fn.startswith('purchase sales') and fn.endswith('.txt')
  , directory
)



""" make it a dummy function when using Kicoo's simplified version """
adjustInterestIncome = lambda x: x


# def adjustInterestIncome(accumulatedInterestIncome):
# 	"""
# 	[Iterable] accumulated interest income (since month 1)
# 	=> [Iterable] accumulated interest income (since month 1)

# 	When using closed period monthly daily interest accrual details
# 	report, enable this method.

# 	The point is to make interest income adjustment for the below
# 	tax lots on and after month 8:

# 	Lot 	 Adjustment
# 	1075473	 (1,555,402.64)
# 	1117941	 (408,489.58)
# 	1117942	 (691,290.07)
# 	1118109	 (408,489.58)
# 	1118110	 (408,489.58)

# 	"""
# 	adjustment = { '1075473': -1555402.64
# 				 , '1117941': -408489.58
# 				 , '1117942': -691290.07
# 				 , '1118109': -408489.58
# 				 , '1118110': -408489.58
# 				 }

# 	"""
# 	[Dictionary] tax lot id 
# 		=> interest income => [Dictionary] id -> income
# 	"""
# 	adjustDict = compose(
# 		dict
# 	  , partial( map
# 	  		   , lambda t: (t[0], t[1] + adjustment[t[0]]) \
# 	  		   		if t[0] in adjustment else t
# 	  		   )
# 	  , lambda d: d.items()
# 	)


# 	return \
# 	compose(
# 		partial(map, lambda t: adjustDict(t[1]) if t[0] > 7 else t[1])
# 	  , partial(zip, count(1))
# 	)(accumulatedInterestIncome)



def getResultFromFiles( purchaseSalesFile, cashLedgerFiles
					  , profitLossSummaryFiles, dailyInterestAccrualFiles
					  , useAllTaxlotsForRealizedGainloss
					  , bondConnectOnly):
	"""
	[String] purchaseSalesFile
	[List] cash ledger files,
	[List] profit loss summary files,
	[List] daily interest accrual files,
	[Bool] use all tax lots for realized gain computation,
	[Bool] use bond connect tax lots only

	=> ( accumulatedInterestIncome
	   , accumulatedRealizedGL
	   , accumulatedFairValueChange
	   , timeWeightedCapital
	   )
	"""
	purchasedTaxlots = getPurchasedTaxlots(purchaseSalesFile)
	bondConnectTaxlots = compose(
		partial(reduce, lambda s1, s2: s1.union(s2))
	  , partial(map, getBondConnectTaxlots)
	)(profitLossSummaryFiles)

	sortedPLdata = sorted( map( partial( readProfitLossSummaryWithTaxLotTxtReport
									   , 'utf-16', '\t')
							  , profitLossSummaryFiles)
						 , key=lambda t: t[1]['PeriodEndDate']
						 )

	sortedTaxlotPLpositions = list(map(lambda t: list(t[0]), sortedPLdata))

	accumulatedRealizedGL = compose(
		list
	  , partial(getAccumulatedRealizedGainLoss, bondConnectTaxlots) \
	  	if useAllTaxlotsForRealizedGainloss and bondConnectOnly else \
	  	partial(getAccumulatedRealizedGainLoss, None) \
	  	if useAllTaxlotsForRealizedGainloss and not bondConnectOnly else \
	  	partial(getAccumulatedRealizedGainLoss, purchasedTaxlots.intersection(bondConnectTaxlots)) \
	  	if not useAllTaxlotsForRealizedGainloss and bondConnectOnly else \
	  	partial(getAccumulatedRealizedGainLoss, purchasedTaxlots)

	)(sortedTaxlotPLpositions)

	accumulatedFairValueChange = compose(
		list
	  , partial(getAccumulatedFairValueChange, purchasedTaxlots.intersection(bondConnectTaxlots)) \
	  	if bondConnectOnly else \
	  	partial(getAccumulatedFairValueChange, purchasedTaxlots)

	)(sortedTaxlotPLpositions)


	sortedInterestData = \
		sorted( map( partial( readDailyInterestAccrualDetailTxtReport
							, 'utf-16', '\t')
				   , dailyInterestAccrualFiles)
			  , key=lambda t: t[1]['PeriodEndDate'])

	sortedDailyInterestPositions = map(lambda t: list(t[0]), sortedInterestData)

	accumulatedInterestIncome = compose(
		list
	  , adjustInterestIncome
	  , partial(getAccumulatedInterestIncome, purchasedTaxlots.intersection(bondConnectTaxlots)) \
	  	if bondConnectOnly else \
	  	partial(getAccumulatedInterestIncome, purchasedTaxlots)

	)(sortedDailyInterestPositions)


	timeWeightedCapital = compose(
		list
	  , partial(getAccumulatedTimeWeightedCapital, bondConnectOnly)
	  , partial(sorted, key=lambda t: t[0])
	  , partial(map, lambda t: (t[1]['PeriodEndDate'], list(t[0])))
	  , partial(map, partial(readCashLedgerTxtReport, 'utf-16', '\t'))
	)(cashLedgerFiles)


	return \
		accumulatedInterestIncome \
	  , accumulatedRealizedGL \
	  , accumulatedFairValueChange \
	  , timeWeightedCapital
# End of function




if __name__ == '__main__':
	import logging.config
	logging.config.fileConfig('logging.config', disable_existing_loggers=False)

	run( getImaDataDirectory()
	   , join(getImaDataDirectory(), getUserConfigFile())
	   )


	# Generate the tax lot ids in 2020 Nov accumulated interest
	# income.
	# compose(
	# 	partial(writeCsv, '2020 Nov tax lots with interest income.csv')
	#   , partial(chain, [('tax lot id', 'interest income')])
	#   , partial(filterfalse, lambda t: t[1] == 0)
	#   , lambda L: L[10].items()
	# )(accumulatedInterestIncome)


	# # Generate the wanted tax lots as of 2020 Nov
	# writeCsv( '2020 Nov tax lots.csv'
	# 		, chain( [('TaxLotID',)]
	# 			   , map(lambda s: (s,), purchasedTaxlots)))


	# compose(
	# 	partial( writeCsv
	# 		   , '2020-01 to 2020-11 tax lot income.csv')
	#   , partial(chain, [('TaxLotID', 'interest income')])
	#   , lambda d: d.items()	
	#   , partial(keepKeysFromDict, purchasedTaxlots)
	#   , partial(getTaxlotInterestIncome)
	#   , lambda t: t[0]
	#   , partial(readDailyInterestAccrualDetailTxtReport, 'utf-16', '\t')
	#   , lambda directory: \
	#   		join(directory,  'total daily interest 2020-01 to 2020-11.txt')
	#   , getInputDirectory
	# )(config)


	# compose(
	# 	print
	#   , partial(getTimeWeightedCapital, '2020-11-30')
	#   , list
	#   , lambda t: filter(lambda p: p['CashDate'] >= '2020-01-01' and p['CashDate'] <= '2020-11-30', t[0])
	#   , partial(readCashLedgerTxtReport, 'utf-16', '\t')
	#   , lambda directory: \
	#   		join(directory,  'total cash ledger 2020-01 to 2020-12.txt')
	#   , getInputDirectory
	# )(config)