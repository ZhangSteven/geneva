# coding=utf-8
# 

import unittest2
from geneva.report import getCurrentDirectory, readExcelReport, readTxtReport \
						, readTaxlotTxtReport, readInvestmentTxtReport \
						, readProfitLossTxtReport
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
		positions, metaData = readTxtReport('utf-8', '\t', inputFile)
		self.verifyMetaData(metaData)
		


	def testReadTxtReport2(self):
		inputFile = join(getCurrentDirectory(), 'samples', 'taxlot01_text_unicode.txt')
		positions, metaData = readTxtReport('utf-16', '\t', inputFile)
		self.verifyMetaData(metaData)



	def testReadTaxlotTxtReport(self):
		inputFile = join(getCurrentDirectory(), 'samples', 'taxlot01_text_unicode.txt')
		positions, metaData = readTaxlotTxtReport('utf-16', '\t', inputFile)
		self.verifyMetaData(metaData)

		positions = list(positions)
		self.assertEqual(38, len(positions))
		self.verifyTaxlotPosition1(positions[0])
		self.verifyTaxlotPosition2(positions[13])



	def testReadInvestmentTxtReport(self):
		inputFile = join(getCurrentDirectory(), 'samples', 'investment 2020-03.txt')
		positions, metaData = readInvestmentTxtReport('utf-16', '\t', inputFile)
		self.verifyMetaData2(metaData)

		positions = list(positions)
		self.assertEqual(174, len(positions))
		self.verifyInvestmentPosition(positions[10])



	def testReadProfitLossTxtReport(self):
		inputFile = join(getCurrentDirectory(), 'samples', 'profit loss 2020-01.txt')
		positions, metaData = readProfitLossTxtReport('utf-16', '\t', inputFile)
		self.verifyMetaData3(metaData)

		positions = list(positions)
		self.assertEqual(133, len(positions))
		self.verifyProfitLossPosition(positions[0])



	def verifyMetaData(self, metaData):
		self.assertEqual('20051', metaData['Portfolio'])
		self.assertEqual('HKD', metaData['BookCurrency'])
		self.assertEqual('2020-09-30', metaData['PeriodEndDate'])
		self.assertEqual('1950-01-01', metaData['PeriodStartDate'])



	def verifyMetaData2(self, metaData):
		self.assertEqual('12XXXChinaLifeOverseasBondGroup', metaData['Portfolio'])
		self.assertEqual('HKD', metaData['BookCurrency'])
		self.assertEqual('ClosedPeriod', metaData['AccountingRunType'])
		self.assertEqual('31-Mar-20', metaData['AccountingPeriod'])



	def verifyMetaData3(self, metaData):
		self.assertEqual('12XXXChinaLifeOverseasBondGroup', metaData['Portfolio'])
		self.assertEqual('HKD', metaData['BookCurrency'])
		self.assertEqual('ClosedPeriod', metaData['AccountingRunType'])
		self.assertEqual('31-Jan-20', metaData['AccountingPeriod'])



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



	def verifyInvestmentPosition(self, position):
		self.assertEqual('United States Dollar', position['LocalCurrency'])
		self.assertEqual('US035240AR13 HTM', position['InvestID'])
		self.assertEqual(24000000, position['Quantity'])
		self.assertEqual('NA', position['LocalPrice'])
		self.assertEqual(-2442286.66, position['BookUnrealizedGainOrLoss'])
		self.assertEqual(0.001, position['Invest'])



	def verifyProfitLossPosition(self, position):
		self.assertEqual('Chinese Renminbi Yuan', position['Currency'])
		self.assertEqual('Cash and Equivalents', position['PrintGroup'])
		self.assertEqual(3335.34, position['EndingQuantity'])
		self.assertEqual('', position['BeginningLocalPrice'])
		self.assertEqual(0, position['UnrealizedPrice'])
		self.assertEqual('Chinese Renminbi Yuan', position['Description'])
		self.assertEqual(1, position['EndingLocalPrice'])
		self.assertEqual(0, position['RealizedCross'])
