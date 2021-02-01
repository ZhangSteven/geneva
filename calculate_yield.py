# coding=utf-8
#
# Calculate portfolio yield
# 

from geneva.report import readInvestmentTxtReport, readProfitLossTxtReport \
						, getCurrentDirectory
from geneva.constants import Constants
from utils.utility import allEquals, writeCsv
from utils.file import getFiles
from toolz.functoolz import compose
from itertools import accumulate, count, chain
from functools import partial
from os.path import join
import logging
logger = logging.getLogger(__name__)



def run(dataDirectory, userConfigFile):
	"""
	[String] data directory (where user input files are stored),
	[String] user config file (where run time parameters are stored)

	 => [Tuple] ( [Int] run result
	 			, [String] message
	 			)

	run result:
	 0: there are input files, run successful
	-1: there are input files, run failed
	 1: there are no input files

	This function does not throw exceptions.
	"""
	logger.debug('run(): start')
	
	investmentFiles, profitLossFiles = \
		list(getInvestmentFiles(dataDirectory)) \
	  , list(getProfitLossFiles(dataDirectory))


	if len(investmentFiles) == 0 or len(profitLossFiles) == 0:
		return (Constants.NO_FILE, '')


	try:
		config = configparser.ConfigParser()
		config.read(userConfigFile)

		withCash, withoutCash = \
			getResultFromFiles( investmentFiles
							  , profitLossFiles
							  , float(config['Input']['lastYearEndNavWithCash'])
							  , float(config['Input']['lastYearEndNavWithOutCash'])
							  , float(config['Input']['impairment'])
							  , int(config['Input']['cutoffMonth'])
							  )

		file1 = \
			writeOutputCsv( dataDirectory, 'with cash', withCash
						  , config['Input']['lastYearEndNavWithCash']
						  , config['Input']['impairment']
						  , int(config['Input']['cutoffMonth']))

		file2 = \
			writeOutputCsv( dataDirectory, 'without cash', withoutCash
						  , config['Input']['lastYearEndNavWithOutCash']
						  , config['Input']['impairment']
						  , int(config['Input']['cutoffMonth']))

		return ( Constants.SUCCESS
			   , 'output files: {0}, {1}'.format(file1, file2))

	except:
		logger.exception('run():')
		return (Constants.FAILURE, '')



def getResultFromFiles( investmentFiles, profitLossFiles
					  , lastYearEndNavWithCash, lastYearEndNavWithoutCash
					  , impairment, cutoffMonth):
	"""
	[Iterable] list of investment position files,
	[Iterator] list of profit loss files,
	[Float] last year end Nav with cash,
	[Float] last year end Nav without cash,
	[Float] impairment,
	[Int] cutoffMonth

		=> ( result with cash
		   , result without cash)
	"""
	sortedPLdata = sorted( map( partial(readProfitLossTxtReport, 'utf-16', '\t')
							  , profitLossFiles)
						 , key=lambda t: t[1]['PeriodEndDate'])
	
	sortedInvdata = sorted( map( partial(readInvestmentTxtReport, 'utf-16', '\t')
							   , investmentFiles)
						  , key=lambda t: t[1]['PeriodEndDate'])

	checkMetaData( list(map(lambda t: t[1], sortedPLdata))
				 , list(map(lambda t: t[1], sortedInvdata)))

	return \
	getResultFromPositions( list(map(lambda t: list(t[0]), sortedPLdata))
						  , list(map( lambda t: (list(t[0]), getMetadataMonth(t[1]) <= cutoffMonth)
									, sortedInvdata))
						  , lastYearEndNavWithCash
						  , lastYearEndNavWithoutCash
						  , impairment)



def getResultFromPositions( sortedPLPositions, sortedInvPositionsWithCutoff
						  , lastYearEndNavWithCash, lastYearEndNavWithoutCash
						  , impairment):
	"""
	[List] profit loss positions sorted by month, like
		[positions of month1, positions of month2, ...]
	[List] investment positions sorted by month with cutoff parameter, like
		[(positions of month1, isCutoff), (positions of month2, isCutoff), ...]
	[Float] last year end Nav with cash,
	[Float] last year end Nav without cash,
	[Float] impairment
		=> ( result with cash
		   , result without cash)

		where result is a tuple:
		( accumulated realized return, return rate, accumulated total return
		, return rate, average nav)
	"""
	combine = compose(
		partial(map, lambda t: (t[0], t[0]/t[2]*100, t[1], t[1]/t[2]*100, t[2]))
	  , lambda m1, m2: \
			map(lambda t: (*t[0], t[1]), zip(m1, m2))
	)

	return \
	( combine( getAccumulatedReturn(sortedPLPositions, True)
		   	 , getAverageNav( sortedInvPositionsWithCutoff
				  		    , True, impairment, lastYearEndNavWithCash)
		     )

	, combine( getAccumulatedReturn(sortedPLPositions, False)
		     , getAverageNav( sortedInvPositionsWithCutoff
				  		    , False, impairment, lastYearEndNavWithoutCash)
		     )
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
		logger.error('checkMetaData(): inconsistent data length : {0}, {1}'.format(
					len(plMetadata), len(invMetadata)))
		raise ValueError


	# if not all(map( lambda m: m['AccountingRunType'] == 'ClosedPeriod'
	# 			  , plMetadata + invMetadata)):
	# 	logger.error('checkMetaData(): not all are of closed period')
	# 	raise ValueError

	if not allEquals(map(lambda m: m['AccountingRunType'], plMetadata + invMetadata)):
		logger.error('checkMetaData(): inconsistent accounting run type')
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
		logger.error('checkMetaData(): invalid month collection')
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
getAverageNav = lambda allPositions, withCash, impairment, lastYearEndNav : \
compose(
	partial(map, lambda t: (t[1] + lastYearEndNav)/(t[0] + 1))
  , partial(zip, count(1))
  , accumulate
  , partial(map, lambda t: getNavFromPositions(withCash, t[1], impairment, t[0]))
)(allPositions)



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



"""
	[Function] (String -> Bool), [String] directory => [Iterable] files
"""
getFilesWithFilterFunc = lambda filterFunc, directory: \
compose(
	partial(map, lambda fn: join(directory, fn))
  , partial(filter, filterFunc)
  , getFiles
)(directory)



"""
	[String] directory => [Iterable] investment position files
"""
getInvestmentFiles = partial(
	getFilesWithFilterFunc
  , lambda fn: fn.startswith('investment positions') and fn.endswith('.txt')
)



"""
	[String] directory => [Iterable] investment position files
"""
getProfitLossFiles = partial(
	getFilesWithFilterFunc
  , lambda fn: fn.startswith('profit loss') and fn.endswith('.txt')
)



"""
	[String] output directory
	[String] file name suffix,
	[Float] last year end nav,
	[Float] impairment,
	[Int] cutoff month, 
		=> [String] output csv name
"""
writeOutputCsv = lambda outputDirectory, suffix, data \
					, lastYearEndNav, impairment, cutoffMonth: \
	writeCsv( join(outputDirectory, 'CLO bond yield ' + suffix + '.csv')
			, chain( [( 'Month', 'Accumulated Realized Return', 'Return Rate'
					  , 'Accumulated Total Return', 'Return Rate', 'Average Nav')]
				   , map(lambda t: (t[0], *t[1]), zip(count(1), data))
				   , [()]	# empty line
				   , [('Scenario', suffix)]
				   , [('Last Year End Nav', lastYearEndNav)]
				   , [('Impairment', impairment)]
				   , [('Cutoff Month', cutoffMonth)]
				   )
			, delimiter=','
			)



if __name__ == '__main__':
	import logging.config
	logging.config.fileConfig('logging.config', disable_existing_loggers=False)

	import configparser
	config = configparser.ConfigParser()
	config.read('calculate_yield.config')

	"""
		To run the program, users must supply the data files and
		fill in data into the configure file. The data files are
		stored under the directory specified by the 'dataDirectory',
		and configure file specified by 'userConfigFile'.
	"""
	status, message = \
		run( config['Input']['dataDirectory']
		   , join( config['Input']['dataDirectory']
		   		 , config['Input']['userConfigFile']))
