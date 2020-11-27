# coding=utf-8
# 

import unittest2
from geneva.report import getCurrentDirectory, readExcelReport, readTxtReport \
						, readTaxlotTxtReport
from os.path import join



class TestReport(unittest2.TestCase):

	def __init__(self, *args, **kwargs):
		super(TestReport, self).__init__(*args, **kwargs)



	def testReadExcelReport(self):
		inputFile = join(getCurrentDirectory(), 'samples', 'taxlot01.xlsx')
		positions, metaData = readExcelReport(inputFile)
		self.verifyMetaData(metaData)
		self.assertEqual(38, len(positions))



	def testReadTxtReport(self):
		inputFile = join(getCurrentDirectory(), 'samples', 'taxlot01_text_tab.txt')
		positions, metaData = readTxtReport(inputFile, 'utf-8', '\t')
		self.verifyMetaData(metaData)
		


	def testReadTxtReport2(self):
		inputFile = join(getCurrentDirectory(), 'samples', 'taxlot01_text_unicode.txt')
		positions, metaData = readTxtReport(inputFile, 'utf-16', '\t')
		self.verifyMetaData(metaData)



	def testReadTaxlotTxtReport(self):
		inputFile = join(getCurrentDirectory(), 'samples', 'taxlot01_text_unicode.txt')
		positions, metaData = readTaxlotTxtReport(inputFile, 'utf-16', '\t')
		self.verifyMetaData(metaData)

		positions = list(positions)
		self.assertEqual(38, len(positions))
		self.verifyTaxlotPosition1(positions[0])
		self.verifyTaxlotPosition2(positions[13])



	def verifyMetaData(self, metaData):
		self.assertEqual('20051', metaData['Portfolio'])
		self.assertEqual('HKD', metaData['BookCurrency'])
		self.assertEqual('2020-09-30', metaData['PeriodEndDate'])
		self.assertEqual('1950-01-01', metaData['PeriodStartDate'])



	def verifyTaxlotPosition1(self, position):
		self.assertEqual('Chinese Renminbi Yuan', position['SortByDescription'])
		self.assertEqual('Cash and Equivalents', position['ThenByDescription'])
		self.assertEqual('Chinese Renminbi Yuan (CNY)', position['InvestmentDescription'])
		self.assertEqual('', position['TaxLotID'])
		self.assertEqual('', position['TaxLotDate'])
		self.assertEqual(6.91, position['Quantity'])
		self.assertEqual(1.1259, position['UnitCost'])
		self.assertEqual(0, position['AccruedInterestBook'])



	def verifyTaxlotPosition2(self, position):
		self.assertEqual('United States Dollar', position['SortByDescription'])
		self.assertEqual('Corporate Bond', position['ThenByDescription'])
		self.assertEqual('CCAMCL 4.25 04/23/25 REGS (USG21184AB52 HTM)', position['InvestmentDescription'])
		self.assertEqual('1013603', position['TaxLotID'])
		self.assertEqual('2016-03-16', position['TaxLotDate'])
		self.assertEqual(1000000, position['Quantity'])
		self.assertEqual(96.589, position['UnitCost'])
		self.assertEqual('NA', position['MarketPrice'])
		self.assertEqual(-9658.90, position['UnrealizedFXGainLossBook'])
