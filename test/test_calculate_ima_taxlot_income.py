# coding=utf-8
# 

import unittest2
from geneva.report import getCurrentDirectory \
						, readDailyInterestAccrualDetailTxtReport
from geneva.calculate_ima_yield import getTaxlotInterestIncome
from os.path import join



class TestCalculateTaxlotIncome(unittest2.TestCase):

	def __init__(self, *args, **kwargs):
		super(TestCalculateTaxlotIncome, self).__init__(*args, **kwargs)


	def testGetTaxlotInterestIncome(self):
		file = join(getCurrentDirectory(), 'samples', 'daily interest 2020-01.txt')
		positions, _ = readDailyInterestAccrualDetailTxtReport('utf-16', '\t', file)
		d = getTaxlotInterestIncome(positions)
		self.assertAlmostEqual(240897.71, d['1104216'])
		self.assertAlmostEqual(145956.02, d['1109831'])
		