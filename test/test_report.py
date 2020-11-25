# coding=utf-8
# 

import unittest2
from geneva.report import getCurrentDirectory, readExcelReport
from os.path import join



class TestReport(unittest2.TestCase):

	def __init__(self, *args, **kwargs):
		super(TestReport, self).__init__(*args, **kwargs)



	def testReadExcelReport(self):
		inputFile = join(getCurrentDirectory(), 'samples', 'taxlot01.xlsx')
		positions, metaData = readExcelReport(inputFile)
		self.assertEqual('20051', metaData['Portfolio'])
		self.assertEqual('HKD', metaData['BookCurrency'])
		self.assertEqual('2020-09-30', metaData['PeriodEndDate'])
		self.assertEqual('1950-01-01', metaData['PeriodStartDate'])



	# def verifyTrade1(self, trade):
	# 	self.assertEqual('666666', trade['Portfolio_code'])
	# 	self.assertEqual('REPO', trade['Txn_type'])
	# 	self.assertEqual('Close', trade['Txn_sub_type'])
	# 	self.assertEqual('USD', trade['Loan_ccy'])
	# 	self.assertEqual('02/03/2020', trade['Mature_date'])
	# 	self.assertEqual(1200000, trade['Col_Qty'])
	# 	self.assertEqual('SOCG-REPO', trade['Broker'])
	# 	self.assertEqual('226819', trade['Cust_ref'])
