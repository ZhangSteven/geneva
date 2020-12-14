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
						, getAccumulatedFairValueChange
from toolz.functoolz import compose
from functools import partial
from itertools import accumulate
from os.path import join



class TestCalculateIMAYield(unittest2.TestCase):

	def __init__(self, *args, **kwargs):
		super(TestCalculateIMAYield, self).__init__(*args, **kwargs)


	# Test cases for when coupon is counted as internal cash flow. 
	# 
	# def testGetTimeWeightedCapital(self):
	# 	file = join(getCurrentDirectory(), 'samples', 'cash ledger 2020-01.txt')

	# 	positions, metadata = readCashLedgerTxtReport('utf-16', '\t', file)
	# 	self.assertAlmostEqual(
	# 		186332788.70
	# 	  , getTimeWeightedCapital(metadata['PeriodEndDate'], list(positions))
	# 	  , 2
	# 	)



	# def testGetAccumulatedTimeWeightedCapital(self):
	# 	files = [ join(getCurrentDirectory(), 'samples', 'cash ledger 2020-01.txt')
	# 			, join(getCurrentDirectory(), 'samples', 'cash ledger 2020-02.txt')
	# 			]

	# 	sortedCLPositions = compose(
	# 		partial(sorted, key=lambda t: t[0])
	# 	  , partial(map, lambda t: (t[1]['PeriodEndDate'], list(t[0])))
	# 	  , partial(map, partial(readCashLedgerTxtReport, 'utf-16', '\t'))
	# 	)(files)

	# 	self.assertEqual('2020-01-31', sortedCLPositions[0][0])
	# 	self.assertEqual('2020-02-29', sortedCLPositions[1][0])
	# 	L = list(getAccumulatedTimeWeightedCapital(sortedCLPositions))
	# 	self.assertEqual(2, len(L))
	# 	self.assertAlmostEqual(186332788.70, L[0], 2)
	# 	self.assertAlmostEqual(668166522.94, L[1], 2)


	def testGetAccumulatedInterestIncome(self):
		files = \
			[ join(getCurrentDirectory(), 'samples', 'daily interest 2020-01.txt')
			, join(getCurrentDirectory(), 'samples', 'daily interest 2020-02.txt')
			, join(getCurrentDirectory(), 'samples', 'daily interest 2020-03.txt')
			]

		totalInterestIncome = compose(
			list
		  , partial(map, lambda d: sum(d.values()))
		  , getAccumulatedInterestIncome
		  , partial(map, lambda t: list(t[0]))
		  , partial(map, partial(readDailyInterestAccrualDetailTxtReport, 'utf-16', '\t'))
		)(files)

		# self.assertAlmostEqual( 790089428.94, totalInterestIncome[0], 2)
		# self.assertAlmostEqual(1525060674.65, totalInterestIncome[1], 2)
		# self.assertAlmostEqual(2312411464.79, totalInterestIncome[2], 2)



	def testGetTimeWeightedCapital(self):
		file = join(getCurrentDirectory(), 'samples', 'cash ledger 2020-01.txt')

		positions, metadata = readCashLedgerTxtReport('utf-16', '\t', file)
		self.assertAlmostEqual(
			163922587.75
		  , getTimeWeightedCapital(metadata['PeriodEndDate'], list(positions))
		  , 2
		)



	def testGetAccumulatedTimeWeightedCapital(self):
		files = [ join(getCurrentDirectory(), 'samples', 'cash ledger 2020-01.txt')
				, join(getCurrentDirectory(), 'samples', 'cash ledger 2020-02.txt')
				]

		sortedCLPositions = compose(
			partial(sorted, key=lambda t: t[0])
		  , partial(map, lambda t: (t[1]['PeriodEndDate'], list(t[0])))
		  , partial(map, partial(readCashLedgerTxtReport, 'utf-16', '\t'))
		)(files)

		self.assertEqual('2020-01-31', sortedCLPositions[0][0])
		self.assertEqual('2020-02-29', sortedCLPositions[1][0])
		L = list(getAccumulatedTimeWeightedCapital(sortedCLPositions))
		self.assertEqual(2, len(L))
		self.assertAlmostEqual(163922587.75, L[0], 2)
		self.assertAlmostEqual(556735459.34, L[1], 2)



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
		  , getAccumulatedRealizedGainLoss
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
		  , getAccumulatedFairValueChange
		  , partial(map, lambda t: t[0])
		  , partial( map
				   , partial(readProfitLossSummaryWithTaxLotTxtReport, 'utf-16', '\t'))
		)(files)

		self.assertEqual(2, len(values))
		self.assertAlmostEqual(8071778.13, values[0])
		self.assertAlmostEqual(8071778.13 - 6700947.29, values[1])