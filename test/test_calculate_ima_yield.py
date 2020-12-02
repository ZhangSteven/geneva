# coding=utf-8
# 

import unittest2
from geneva.report import readProfitLossTxtReport, getCurrentDirectory \
						, readCashLedgerTxtReport
from geneva.calculate_ima_yield import getTimeWeightedCapital
from toolz.functoolz import compose
from functools import partial
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
