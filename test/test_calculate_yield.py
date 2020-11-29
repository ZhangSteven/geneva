# coding=utf-8
# 

import unittest2
from geneva.report import readProfitLossTxtReport, getCurrentDirectory \
						, readInvestmentTxtReport
from geneva.calculate_yield import getReturnFromPositions, getNavFromPositions \
						, getResultFromFiles
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
		  , lambda file: readProfitLossTxtReport('utf-16', '\t', file)
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
		  , lambda file: readProfitLossTxtReport('utf-16', '\t', file)
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
		  , lambda file: readInvestmentTxtReport('utf-16', '\t', file)
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
		  , lambda file: readInvestmentTxtReport('utf-16', '\t', file)
		)(inputFile)

		self.assertAlmostEqual( 198014238644.38
							  , getNavFromPositions(True, True, getImpairment(), positions)
							  , 2)


		self.assertAlmostEqual( 195050730381.42
							  , getNavFromPositions(False, True, getImpairment(), positions)
							  , 2)



	def testGetResultFromFiles(self):
		# Sequence of the files does not matter
		investmentFiles = [ join(getCurrentDirectory(), 'samples', 'investment positions 2020-06.txt')
						  , join(getCurrentDirectory(), 'samples', 'investment positions 2020-07.txt')
						  , join(getCurrentDirectory(), 'samples', 'investment positions 2020-08.txt')
						  , join(getCurrentDirectory(), 'samples', 'investment positions 2020-09.txt')
						  , join(getCurrentDirectory(), 'samples', 'investment positions 2020-10.txt')
						  , join(getCurrentDirectory(), 'samples', 'investment positions 2020-01.txt')
						  , join(getCurrentDirectory(), 'samples', 'investment positions 2020-02.txt')
						  , join(getCurrentDirectory(), 'samples', 'investment positions 2020-03.txt')
						  , join(getCurrentDirectory(), 'samples', 'investment positions 2020-04.txt')
						  , join(getCurrentDirectory(), 'samples', 'investment positions 2020-05.txt')
						  ]

		profitLossFiles = [ join(getCurrentDirectory(), 'samples', 'profit loss 2020-06.txt')
						  , join(getCurrentDirectory(), 'samples', 'profit loss 2020-07.txt')
						  , join(getCurrentDirectory(), 'samples', 'profit loss 2020-08.txt')
						  , join(getCurrentDirectory(), 'samples', 'profit loss 2020-09.txt')
						  , join(getCurrentDirectory(), 'samples', 'profit loss 2020-10.txt')
						  , join(getCurrentDirectory(), 'samples', 'profit loss 2020-01.txt')
						  , join(getCurrentDirectory(), 'samples', 'profit loss 2020-02.txt')
						  , join(getCurrentDirectory(), 'samples', 'profit loss 2020-03.txt')
						  , join(getCurrentDirectory(), 'samples', 'profit loss 2020-04.txt')
						  , join(getCurrentDirectory(), 'samples', 'profit loss 2020-05.txt')
						  ]

		withCash, withoutCash = (lambda t: (list(t[0]), list(t[1])))(
			getResultFromFiles( investmentFiles
							  , profitLossFiles
							  , 177801674041.66
							  , 177800934590.20
							  , 3212689500.00, 7)
		)

		self.assertAlmostEqual(794354025.64, withCash[0][0], 2)
		self.assertAlmostEqual(467300058.59, withCash[0][2], 2)
		self.assertAlmostEqual(178862489321.83, withCash[0][4], 2)
		self.assertAlmostEqual(795081909.54, withoutCash[0][0], 2)
		self.assertAlmostEqual(468008054.89, withoutCash[0][2], 2)
		self.assertAlmostEqual(178202412228.44, withoutCash[0][4], 2)

		self.assertAlmostEqual(8836311220.42, withCash[9][0], 2)
		self.assertAlmostEqual(8228027711.85, withCash[9][2], 2)
		self.assertAlmostEqual(191878687075.53, withCash[9][4], 2)
		self.assertAlmostEqual(8833423074.48, withoutCash[9][0], 2)
		self.assertAlmostEqual(8223793885.14, withoutCash[9][2], 2)
		self.assertAlmostEqual(189813739094.29, withoutCash[9][4], 2)



	def testResultFromFilesError1(self):
		investmentFiles = [ join(getCurrentDirectory(), 'samples', 'investment positions 2020-06.txt')
						  , join(getCurrentDirectory(), 'samples', 'investment positions 2020-07.txt')
						  ]

		profitLossFiles = [ join(getCurrentDirectory(), 'samples', 'profit loss 2020-06.txt')
						  ]

		try:
			getResultFromFiles( investmentFiles
							  , profitLossFiles
							  , 177801674041.66
							  , 177800934590.20
							  , 3212689500.00, 7)
		except ValueError:
			# expected: inconsistent number of files
			pass

		else:
			self.fail('error should occur')



	def testResultFromFilesError2(self):
		investmentFiles = [ join(getCurrentDirectory(), 'samples', 'investment positions 2020-01.txt')
						  , join(getCurrentDirectory(), 'samples', 'investment positions 2020-02.txt')
						  ]

		profitLossFiles = [ join(getCurrentDirectory(), 'samples', 'profit loss 2020-01.txt')
						  , join(getCurrentDirectory(), 'samples', 'profit loss 2020-03.txt')
						  ]

		try:
			getResultFromFiles( investmentFiles
							  , profitLossFiles
							  , 177801674041.66
							  , 177800934590.20
							  , 3212689500.00, 7)
		except ValueError:
			# expected: profit loss files: Jan and Mar
			pass

		else:
			self.fail('error should occur')



	def testResultFromFilesError3(self):
		investmentFiles = [ join(getCurrentDirectory(), 'samples', 'investment positions base USD 2020-01.txt')
						  , join(getCurrentDirectory(), 'samples', 'investment positions 2020-02.txt')
						  ]

		profitLossFiles = [ join(getCurrentDirectory(), 'samples', 'profit loss 2020-01.txt')
						  , join(getCurrentDirectory(), 'samples', 'profit loss 2020-02.txt')
						  ]

		try:
			getResultFromFiles( investmentFiles
							  , profitLossFiles
							  , 177801674041.66
							  , 177800934590.20
							  , 3212689500.00, 7)
		except ValueError:
			# expected: one investment file has base USD, inconsistent
			# with others
			pass

		else:
			self.fail('error should occur')



	def testResultFromFilesError4(self):
		investmentFiles = [ join(getCurrentDirectory(), 'samples', 'investment positions no close 2020-01.txt')
						  , join(getCurrentDirectory(), 'samples', 'investment positions 2020-02.txt')
						  ]

		profitLossFiles = [ join(getCurrentDirectory(), 'samples', 'profit loss 2020-01.txt')
						  , join(getCurrentDirectory(), 'samples', 'profit loss 2020-02.txt')
						  ]

		try:
			getResultFromFiles( investmentFiles
							  , profitLossFiles
							  , 177801674041.66
							  , 177800934590.20
							  , 3212689500.00, 7)
		except ValueError:
			# expected: one investment file is no close period
			pass

		else:
			self.fail('error should occur')



	def testResultFromFilesError5(self):
		investmentFiles = [ join(getCurrentDirectory(), 'samples', '12229 investment positions 2020-01.txt')
						  , join(getCurrentDirectory(), 'samples', 'investment positions 2020-02.txt')
						  ]

		profitLossFiles = [ join(getCurrentDirectory(), 'samples', 'profit loss 2020-01.txt')
						  , join(getCurrentDirectory(), 'samples', 'profit loss 2020-02.txt')
						  ]

		try:
			getResultFromFiles( investmentFiles
							  , profitLossFiles
							  , 177801674041.66
							  , 177800934590.20
							  , 3212689500.00, 7)
		except ValueError:
			# expected: one investment file has a different portfolio
			pass

		else:
			self.fail('error should occur')