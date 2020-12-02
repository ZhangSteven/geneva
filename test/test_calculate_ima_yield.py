# coding=utf-8
# 

import unittest2
from geneva.report import readProfitLossTxtReport, getCurrentDirectory \
						, readCashLedgerTxtReport
from geneva.calculate_ima_yield import getTimeWeightedCapital \
						, getAccumulatedTimeWeightedCapital
from toolz.functoolz import compose
from functools import partial
from itertools import accumulate
from os.path import join



class TestCalculateIMAYield(unittest2.TestCase):

	def __init__(self, *args, **kwargs):
		super(TestCalculateIMAYield, self).__init__(*args, **kwargs)



	def testGetTimeWeightedCapital(self):
		file = join(getCurrentDirectory(), 'samples', 'cash ledger 2020-01.txt')

		positions, metadata = readCashLedgerTxtReport('utf-16', '\t', file)
		self.assertAlmostEqual(
			186332788.70
		  , getTimeWeightedCapital(metadata['PeriodEndDate'], positions)
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
		self.assertAlmostEqual(186332788.70, L[0], 2)
		self.assertAlmostEqual(668166522.94, L[1], 2)
