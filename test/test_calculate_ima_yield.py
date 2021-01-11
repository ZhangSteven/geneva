# coding=utf-8
# 

import unittest2
from geneva.report import readProfitLossTxtReport, getCurrentDirectory \
						, readCashLedgerTxtReport \
						, readDailyInterestAccrualDetailTxtReport \
						, readProfitLossSummaryWithTaxLotTxtReport
from geneva.calculate_ima_yield import getTimeWeightedCapital \
						, getAccumulatedTimeWeightedCapital \
						, getAccumulatedInterestIncome, getRealizedGainLoss \
						, getAccumulatedRealizedGainLoss, getFairValueChange \
						, getAccumulatedFairValueChange, getResultFromFiles
from toolz.functoolz import compose
from functools import partial
from itertools import accumulate
from os.path import join



class TestCalculateIMAYield(unittest2.TestCase):

	def __init__(self, *args, **kwargs):
		super(TestCalculateIMAYield, self).__init__(*args, **kwargs)


	# This one only works when getTaxlotInterestIncome() is imported from
	# clamc_yield_report.ima.py. When we use Kicoo's method to get interest
	# income, then this test case is no longer valid.
	# 
	# def testGetAccumulatedInterestIncome(self):
	# 	files = \
	# 		[ join(getCurrentDirectory(), 'samples', 'daily interest 2020-01.txt')
	# 		, join(getCurrentDirectory(), 'samples', 'daily interest 2020-02.txt')
	# 		, join(getCurrentDirectory(), 'samples', 'daily interest 2020-03.txt')
	# 		]

	# 	totalInterestIncome = compose(
	# 		list
	# 	  , partial(map, lambda d: sum(d.values()))
	# 	  , partial(getAccumulatedInterestIncome, None)
	# 	  , partial(map, lambda t: list(t[0]))
	# 	  , partial(map, partial(readDailyInterestAccrualDetailTxtReport, 'utf-16', '\t'))
	# 	)(files)

	# 	self.assertAlmostEqual( 811088743.30, totalInterestIncome[0], 2)
	# 	self.assertAlmostEqual(1566743855.37, totalInterestIncome[1], 2)
	# 	self.assertAlmostEqual(2375097673.68, totalInterestIncome[2], 2)



	def testGetTimeWeightedCapital(self):
		file = join(getCurrentDirectory(), 'samples', 'cash ledger 2020-01.txt')

		positions, metadata = readCashLedgerTxtReport('utf-16', '\t', file)
		self.assertAlmostEqual(
			163922587.75
		  , getTimeWeightedCapital(metadata['PeriodEndDate'], list(positions))
		  , 2
		)

		file = join(getCurrentDirectory(), 'samples', 'cash ledger 2020-03.txt')

		positions, metadata = readCashLedgerTxtReport('utf-16', '\t', file)
		self.assertAlmostEqual(
			488290764.18
		  , getTimeWeightedCapital(metadata['PeriodEndDate'], list(positions))
		  , 2
		)



	def testGetAccumulatedTimeWeightedCapital(self):
		files = [ join(getCurrentDirectory(), 'samples', 'cash ledger 2020-01.txt')
				, join(getCurrentDirectory(), 'samples', 'cash ledger 2020-02.txt')
				, join(getCurrentDirectory(), 'samples', 'cash ledger 2020-03.txt')
				]

		sortedCLPositions = compose(
			partial(sorted, key=lambda t: t[0])
		  , partial(map, lambda t: (t[1]['PeriodEndDate'], list(t[0])))
		  , partial(map, partial(readCashLedgerTxtReport, 'utf-16', '\t'))
		)(files)

		self.assertEqual('2020-01-31', sortedCLPositions[0][0])
		self.assertEqual('2020-02-29', sortedCLPositions[1][0])
		L = list(getAccumulatedTimeWeightedCapital(False, sortedCLPositions))
		self.assertEqual(3, len(L))
		self.assertAlmostEqual( 163922587.75, L[0], 2)
		self.assertAlmostEqual( 556735459.34, L[1], 2)
		self.assertAlmostEqual(1509419832.61, L[2], 2)



	def testGetRealizedGainLoss(self):
		file = join(getCurrentDirectory(), 'samples', 'profit loss summary tax lot 2020-01.txt')
		self.assertAlmostEqual( 
			5011429.88
		  , compose(
		  		lambda d: sum(d.values())
		  	  , getRealizedGainLoss
		 	  , lambda t: t[0]
		  	  , partial(readProfitLossSummaryWithTaxLotTxtReport, 'utf-16', '\t')
			)(file)
		  , 2
		)



	def testGetAccumulatedRealizedGainLoss(self):
		files = [ join(getCurrentDirectory(), 'samples', 'profit loss summary tax lot 2020-01.txt')
				, join(getCurrentDirectory(), 'samples', 'profit loss summary tax lot 2020-02.txt')
				]

		values = compose(
			list
		  , partial(map, lambda d: sum(d.values()))
		  , partial(getAccumulatedRealizedGainLoss, None)
		  , partial(map, lambda t: t[0])
		  , partial( map
				   , partial(readProfitLossSummaryWithTaxLotTxtReport, 'utf-16', '\t'))
		)(files)

		self.assertEqual(2, len(values))
		self.assertAlmostEqual(5011429.88, values[0])
		self.assertAlmostEqual(5011429.88 + 8483828.71, values[1])



	def testGetFairValueChange(self):
		file = join(getCurrentDirectory(), 'samples', 'profit loss summary tax lot 2020-01.txt')
		self.assertAlmostEqual( 
			8071778.13
		  , compose(
		  		lambda d: sum(d.values())
		  	  , getFairValueChange
		 	  , lambda t: t[0]
		  	  , partial(readProfitLossSummaryWithTaxLotTxtReport, 'utf-16', '\t')
			)(file)
		  , 2
		)



	def testGetAccumulatedFairValueChange(self):
		files = [ join(getCurrentDirectory(), 'samples', 'profit loss summary tax lot 2020-01.txt')
				, join(getCurrentDirectory(), 'samples', 'profit loss summary tax lot 2020-02.txt')
				]

		values = compose(
			list
		  , partial(map, lambda d: sum(d.values()))
		  , partial(getAccumulatedFairValueChange, None)
		  , partial(map, lambda t: t[0])
		  , partial( map
				   , partial(readProfitLossSummaryWithTaxLotTxtReport, 'utf-16', '\t'))
		)(files)

		self.assertEqual(2, len(values))
		self.assertAlmostEqual(8071778.13, values[0])
		self.assertAlmostEqual(8071778.13 - 6700947.29, values[1])



	def testGetResultFromFiles(self):
		"""
		Test overall computation, in the case that:

		1) Use all tax lots for realized gain loss;
		2) All positions are included.
		"""
		accumulatedInterestIncome, accumulatedRealizedGL, \
		accumulatedFairValueChange , timeWeightedCapital = \
			getResultFromFiles(*getFiles(), True, False)

		addValues = lambda d: sum(d.values())

		self.assertAlmostEqual( 728571487.899
							  , addValues(accumulatedInterestIncome[-1])
							  , 2)

		self.assertAlmostEqual( 762896347.08
							  , addValues(accumulatedRealizedGL[-1])
							  , 2)

		self.assertAlmostEqual( 54030490.71
							  , addValues(accumulatedFairValueChange[-1])
							  , 2)

		self.assertAlmostEqual( 29951721898.17
							  , timeWeightedCapital[-1]
							  , 2)



	def testGetResultFromFiles2(self):
		"""
		Test overall computation, in the case that:

		1) Use all tax lots for realized gain loss;
		2) Only bond connect positions are included.
		"""
		accumulatedInterestIncome, accumulatedRealizedGL, \
		accumulatedFairValueChange , timeWeightedCapital = \
			getResultFromFiles(*getFiles(), True, True)

		addValues = lambda d: sum(d.values())

		self.assertAlmostEqual( 5049819.83
							  , addValues(accumulatedInterestIncome[-1])
							  , 2)

		self.assertAlmostEqual( 0
							  , addValues(accumulatedRealizedGL[-1])
							  , 2)

		self.assertAlmostEqual( 37458712.95
							  , addValues(accumulatedFairValueChange[-1])
							  , 2)

		self.assertAlmostEqual( 230115859.79
							  , timeWeightedCapital[-1]
							  , 2)



def getFiles():
	"""
	helper function for the tests:

	[Tuple] ( purchaseSalesFile, cashLedgerFiles
			, profitLossSummaryFiles, dailyInterestAccrualFiles)
	"""
	addDirectory = lambda file: \
		join('samples', '2020 year data', file)

	cashLedgerFiles = \
	[ 'cash ledger custodian 2020-01.txt'
	, 'cash ledger custodian 2020-02.txt'
	, 'cash ledger custodian 2020-03.txt'
	, 'cash ledger custodian 2020-04.txt'
	, 'cash ledger custodian 2020-05.txt'
	, 'cash ledger custodian 2020-06.txt'
	, 'cash ledger custodian 2020-07.txt'
	, 'cash ledger custodian 2020-08.txt'
	, 'cash ledger custodian 2020-09.txt'
	, 'cash ledger custodian 2020-10.txt'
	, 'cash ledger custodian 2020-11.txt'
	, 'cash ledger custodian 2020-12.txt'
	]

	profitLossSummaryFiles = \
	[ 'profit loss summary custodian 2020-01.txt'
	, 'profit loss summary custodian 2020-02.txt'
	, 'profit loss summary custodian 2020-03.txt'
	, 'profit loss summary custodian 2020-04.txt'
	, 'profit loss summary custodian 2020-05.txt'
	, 'profit loss summary custodian 2020-06.txt'
	, 'profit loss summary custodian 2020-07.txt'
	, 'profit loss summary custodian 2020-08.txt'
	, 'profit loss summary custodian 2020-09.txt'
	, 'profit loss summary custodian 2020-10.txt'
	, 'profit loss summary custodian 2020-11.txt'
	, 'profit loss summary custodian 2020-12.txt'
	]

	dailyInterestAccrualFiles = \
	[ 'daily interest non-close 2020-01.txt'
	, 'daily interest non-close 2020-02.txt'
	, 'daily interest non-close 2020-03.txt'
	, 'daily interest non-close 2020-04.txt'
	, 'daily interest non-close 2020-05.txt'
	, 'daily interest non-close 2020-06.txt'
	, 'daily interest non-close 2020-07.txt'
	, 'daily interest non-close 2020-08.txt'
	, 'daily interest non-close 2020-09.txt'
	, 'daily interest non-close 2020-10.txt'
	, 'daily interest non-close 2020-11.txt'
	, 'daily interest non-close 2020-12.txt'
	]

	return \
	( addDirectory('purchase sales 2020-12.txt')
	, list(map(addDirectory, cashLedgerFiles))
	, list(map(addDirectory, profitLossSummaryFiles))
	, list(map(addDirectory, dailyInterestAccrualFiles))
	)
