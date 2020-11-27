# coding=utf-8
# 

import unittest2
from geneva.report import getCurrentDirectory, readExcelReport, readTxtReport
from os.path import join



class TestReport(unittest2.TestCase):

	def __init__(self, *args, **kwargs):
		super(TestReport, self).__init__(*args, **kwargs)



	def testReadExcelReport(self):
		inputFile = join(getCurrentDirectory(), 'samples', 'taxlot01.xlsx')
		positions, metaData = readExcelReport(inputFile)
		self.verifyMetaData(metaData)
		self.assertEqual(38, len(positions))
		self.verifyTaxlotPosition(positions[0])



	def testReadTxtReport(self):
		inputFile = join(getCurrentDirectory(), 'samples', 'taxlot01_text_tab.txt')
		positions, metaData = readTxtReport(inputFile, 'utf-8', '\t')
		self.verifyMetaData(metaData)
		


	def testReadTxtReport2(self):
		inputFile = join(getCurrentDirectory(), 'samples', 'taxlot01_text_unicode.txt')
		positions, metaData = readTxtReport(inputFile, 'utf-16', '\t')
		self.verifyMetaData(metaData)



	def verifyMetaData(self, metaData):
		self.assertEqual('20051', metaData['Portfolio'])
		self.assertEqual('HKD', metaData['BookCurrency'])
		self.assertEqual('2020-09-30', metaData['PeriodEndDate'])
		self.assertEqual('1950-01-01', metaData['PeriodStartDate'])



	def verifyTaxlotPosition(self, position):
		self.assertEqual('Chinese Renminbi Yuan (CNY)', position['InvestmentDescription'])
		self.assertEqual(6.91, position['Quantity'])
		self.assertEqual(1.1259, position['UnitCost'])
