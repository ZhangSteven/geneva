# coding=utf-8
# 

import unittest2
from geneva.report import getCurrentDirectory, readExcelReport, readTxtReport \
						, readTaxlotTxtReport, readInvestmentTxtReport \
						, readProfitLossTxtReport, readCashLedgerTxtReport \
						, readDailyInterestAccrualDetailTxtReport \
						, readProfitLossSummaryWithTaxLotTxtReport \
						, readMultipartInvestmentTxtReport
from steven_utils.iter import firstN
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



	def testReadCashLedgerTxtReport(self):
		inputFile = join(getCurrentDirectory(), 'samples', 'cash ledger 2020-01.txt')
		positions, metaData = readCashLedgerTxtReport('utf-16', '\t', inputFile)
		self.verifyMetaData3(metaData)

		positions = list(positions)
		self.assertEqual(66, len(positions))
		self.verifyCashLedgerPosition(positions[0])



	def testReadDailyInterestAccrualDetailTxtReport(self):
		inputFile = join(getCurrentDirectory(), 'samples', 'daily interest 2020-01.txt')
		positions, metaData = readDailyInterestAccrualDetailTxtReport(
								'utf-16', '\t', inputFile)
		self.verifyMetaData3(metaData)

		positions = list(positions)
		self.assertEqual(19641, len(positions))
		self.verifyDailyTaxlotAccrualDetailPosition(positions[2])



	def testReadProfitLossSummaryWithTaxLotTxtReport(self):
		inputFile = join(getCurrentDirectory(), 'samples', 'profit loss summary tax lot 2020-01.txt')
		positions, metaData = readProfitLossSummaryWithTaxLotTxtReport(
								'utf-16', '\t', inputFile)
		self.verifyMetaData3(metaData)

		positions = list(positions)
		self.assertEqual(713, len(positions))
		self.assertEqual('', positions[0]['TaxLotId'])
		self.assertEqual('CNY: Chinese Renminbi Yuan', positions[0]['Invest'])
		self.verifyProfitLossTaxLotPosition(positions[3])



	def testReadMultipartInvestmentTxtReport(self):
		inputFile = join(getCurrentDirectory(), 'samples', '12xxx investment multipart.txt')
		result = list(readMultipartInvestmentTxtReport('utf-16', '\t', inputFile))
		self.assertEqual(6, len(result))
		self.assertEqual( ['12229', '12366', '12549', '12550', '12630', '12734']
						, list(map(lambda t: t[1]['Portfolio'], result)))
		self.verifyInvestmentPosition2(list(result[0][0])[0])
		self.assertEqual(0, len(list(result[3][0])))
		self.verifyInvestmentPosition3(list(result[5][0])[-1])



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



	def verifyInvestmentPosition2(self, position):
		self.assertEqual('Chinese Renminbi Yuan', position['LocalCurrency'])
		self.assertEqual('CNY', position['InvestID'])
		self.assertEqual(6269303.08, position['Quantity'])
		self.assertEqual(1, position['LocalPrice'])
		self.assertEqual(65122.90, position['BookUnrealizedGainOrLoss'])
		self.assertEqual(0.0001, position['Invest'])



	def verifyInvestmentPosition3(self, position):
		self.assertEqual('United States Dollar', position['LocalCurrency'])
		self.assertEqual('US912803AY96 HTM', position['InvestID'])
		self.assertEqual(2250000, position['Quantity'])
		self.assertEqual('NA', position['LocalPrice'])
		self.assertEqual(-31172.16, position['BookUnrealizedGainOrLoss'])
		self.assertEqual(0.0002, position['Invest'])



	def verifyProfitLossPosition(self, position):
		self.assertEqual('Chinese Renminbi Yuan', position['Currency'])
		self.assertEqual('Cash and Equivalents', position['PrintGroup'])
		self.assertEqual(3335.34, position['EndingQuantity'])
		self.assertEqual('', position['BeginningLocalPrice'])
		self.assertEqual(0, position['UnrealizedPrice'])
		self.assertEqual('Chinese Renminbi Yuan', position['Description'])
		self.assertEqual(1, position['EndingLocalPrice'])
		self.assertEqual(0, position['RealizedCross'])



	def verifyCashLedgerPosition(self, position):
		self.assertEqual('Chinese Renminbi Yuan Opening Balance', position['Currency_OpeningBalDesc'])
		self.assertEqual(0, position['CurrBegBalLocal'])
		self.assertEqual('Opening Balance', position['GroupWithinCurrency_OpeningBalDesc'])
		self.assertEqual('2020-01-02', position['CashDate'])
		self.assertEqual('1109290', position['TransID'])
		self.assertEqual(0.93, position['BookAmount'])
		self.assertEqual(3730.69, position['CurrClosingBalBook'])
		self.assertEqual('Chinese Renminbi Yuan Closing Balance', position['Currency_ClosingBalDesc'])



	def verifyDailyTaxlotAccrualDetailPosition(self, position):
		self.assertEqual('Portfolio (  )', position['PortfolioInfo'])
		self.assertEqual( 'DE000LB1P2W1 HTM (LBBW 5 02/28/33 EMTN)'
						, position['Investment'])
		self.assertEqual('2020-01-02', position['Date'])
		self.assertEqual(185000000, position['Textbox84'])
		self.assertEqual('1028327', position['LotID'])
		self.assertEqual(37000000, position['LotQuantity'])
		self.assertEqual(5003864.58, position['LotSumOfEndBalanceBook'])
		self.assertEqual(5138.89, position['LotSumOfChangeAILocal'])
		self.assertEqual(637222.22, position['LotSumOfBeginBalanceLocal'])



	def verifyProfitLossTaxLotPosition(self, position):
		self.assertEqual('HK0000337607: CHINAM V5.2 PERP 1', position['Invest'])
		self.assertEqual(30000000, position['Quantity'])
		self.assertEqual(-515999.99, position['UnrealizedFXGL'])
		self.assertEqual(1005108.86, position['CouponDividend'])
		self.assertEqual('1021948', position['TaxLotId'])
		self.assertEqual(27000000, position['Qty_taxlot'])
		self.assertEqual(904597.98, position['Coupon_taxlot'])
		self.assertEqual(0, position['OtherIncome_taxlot'])
