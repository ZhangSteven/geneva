# coding=utf-8
# 

import unittest2
from geneva.report import readProfitLossTxtReport, getCurrentDirectory \
						, readInvestmentTxtReport
from geneva.calculate_yield import getReturnFromPositions, getNavFromPositions
from toolz.functoolz import compose
from functools import partial
from os.path import join



getImpairment = lambda: 3212689500


class TestCalculateYield(unittest2.TestCase):

	def __init__(self, *args, **kwargs):
		super(TestCalculateYield, self).__init__(*args, **kwargs)



	def testGetReturnFromPositions(self):
		inputFile = join(getCurrentDirectory(), 'samples', 'profit loss 2020-07.txt')

		positions = compose(
			lambda t: list(t[0])
		  , lambda file: readProfitLossTxtReport(file, 'utf-16', '\t')
		)(inputFile)

		realized, total = getReturnFromPositions(True, positions)
		self.assertAlmostEqual(910273720.75, realized, 2)
		self.assertAlmostEqual(975551797.10, total, 2)

		realized, total = getReturnFromPositions(False, positions)
		self.assertAlmostEqual(910888436.76, realized, 2)
		self.assertAlmostEqual(976508916.44, total, 2)



	def testGetReturnFromPositions2(self):
		inputFile = join(getCurrentDirectory(), 'samples', 'profit loss 2020-08.txt')

		positions = compose(
			lambda t: list(t[0])
		  , lambda file: readProfitLossTxtReport(file, 'utf-16', '\t')
		)(inputFile)

		realized, total = getReturnFromPositions(True, positions)
		self.assertAlmostEqual(834768238.18, realized, 2)
		self.assertAlmostEqual(893933279.75, total, 2)

		realized, total = getReturnFromPositions(False, positions)
		self.assertAlmostEqual(835110810.36, realized, 2)
		self.assertAlmostEqual(893939455.95, total, 2)



	def testGetNavFromPositions(self):
		inputFile = join(getCurrentDirectory(), 'samples', 'investment positions 2020-08.txt')

		positions = compose(
			lambda t: list(t[0])
		  , lambda file: readInvestmentTxtReport(file, 'utf-16', '\t')
		)(inputFile)

		self.assertAlmostEqual( 201234832347.59
							  , getNavFromPositions(True, False, getImpairment(), positions)
							  , 2)


		self.assertAlmostEqual( 200800408243.31
							  , getNavFromPositions(False, False, getImpairment(), positions)
							  , 2)



	def testGetNavFromPositions2(self):
		inputFile = join(getCurrentDirectory(), 'samples', 'investment positions 2020-07.txt')

		positions = compose(
			lambda t: list(t[0])
		  , lambda file: readInvestmentTxtReport(file, 'utf-16', '\t')
		)(inputFile)

		self.assertAlmostEqual( 198014238644.38
							  , getNavFromPositions(True, True, getImpairment(), positions)
							  , 2)


		self.assertAlmostEqual( 195050730381.42
							  , getNavFromPositions(False, True, getImpairment(), positions)
							  , 2)