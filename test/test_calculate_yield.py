# coding=utf-8
# 

import unittest2
from geneva.report import readProfitLossTxtReport, getCurrentDirectory
from geneva.calculate_yield import getReturnFromPositions
from toolz.functoolz import compose
from functools import partial
from os.path import join



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