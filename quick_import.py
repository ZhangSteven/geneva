# coding=utf-8
#
# Provide functions to do read trade information and create an
# output file to be used for Geneva upload.
# 
# Note that the output file is in csv format, please save it as
# Excel (.xlsx) format before upload to Geneva.
# 

from geneva.report import getRawPositions, excelFileToLines
from steven_utils.utility import mergeDict, writeCsv
from steven_utils.excel import fromExcelOrdinal
from toolz.functoolz import compose
from itertools import takewhile, chain
from functools import partial
import logging
logger = logging.getLogger(__name__)



def getJournalTrades(lines):
	"""
	[Iterable] lines => [Iterable] ([Dictionary] journal trade)
	"""
	nonEmptyLine = lambda line: len(line) > 0 and line[0] != ''

	toDateTimeString = lambda x: fromExcelOrdinal(x).strftime('%Y-%m-%d')

	toStringIfFloat = lambda acc: \
		str(int(acc)) if isinstance(acc, float) else acc

	updatePosition = lambda p: \
		mergeDict( p
				 , { 'Account': toStringIfFloat(p['Account'])
				   , 'Trade Date': toDateTimeString(p['Trade Date'])
				   , 'Settlement Date': toDateTimeString(p['Settlement Date'])
				   , 'Ticket Number': toStringIfFloat(p['Ticket Number'])
				   }
				 )

	return \
	compose(
		partial(map, updatePosition)
	  , getRawPositions
	  , partial(takewhile, nonEmptyLine)
	)(lines)



def journalToQuickImport(trade):
	"""
	[Dictionary] journal trades
		=> [Dictionary] quick import entries
	"""
	def getCurrency(ticker):
		if ticker.endswith(' HK'):
			return 'HKD'
		elif ticker.endswith(' US'):
			return 'USD'
		else:
			logger.error('getCurrency(): invalid ticker: {0}'.format(ticker))
			raise ValueError


	def getLocationAccount(account):
		if account == '11490-D':
			return 'JPM'
		elif account == '13006':
			return 'BOCHK'
		else:
			logger.error('getLocationAccount(): invalid account: {0}'.format(account))
			raise ValueError


	return \
	{ 'RecordType': trade['BuySell']
	, 'RecordAction': 'New'
	, 'Portfolio': trade['Account']
	, 'Investment': trade['Ticker']
	, 'LocationAccount': getLocationAccount(trade['Account'])
	, 'Strategy': 'Default'
	, 'EventDate': trade['Trade Date']
	, 'SettleDate': trade['Settlement Date']
	, 'ActualSettleDate': trade['Settlement Date']
	, 'CounterInvestment': getCurrency(trade['Ticker'])
	, 'CounterTDateFx': ''
	, 'Quantity': trade['Quantity']
	, 'Price': trade['Price']
	, 'NetCounterAmount': 'CALC'
	, 'NetInvestmentAmount': 'CALC'
	, 'Broker': 'Journaling Entries'
	, 'PriceDenomination': getCurrency(trade['Ticker'])
	, 'TradeFX': ''
	, 'UserTranId1': trade['Ticket Number']
	}



def writeQuickImportCsv(outputFile, quickImportEntries):
	headers = \
	( 'RecordType', 'RecordAction', 'Portfolio', 'Investment'
	, 'LocationAccount', 'Strategy', 'EventDate', 'SettleDate'
	, 'ActualSettleDate', 'CounterInvestment', 'CounterTDateFx'
	, 'Quantity', 'Price', 'NetCounterAmount', 'NetInvestmentAmount'
	, 'Broker', 'PriceDenomination', 'TradeFX', 'UserTranId1'
	)

	dictToValues = lambda keys, d: map(lambda k: d[k], keys)


	return \
	writeCsv( outputFile
			, chain( [headers]
				   , map(partial(dictToValues, headers), quickImportEntries)
				   )
			, delimiter=','
			)




if __name__ == '__main__':
	import logging.config
	logging.config.fileConfig('logging.config', disable_existing_loggers=False)

	import argparse
	parser = argparse.ArgumentParser(description='Produce Geneva Quick Import Trade File')
	parser.add_argument( 'file', metavar='file', type=str
					   , help='input file')

	"""
		Put the Excel trade file in the program directory, then:

		$ python quick_import.py <file name>

		For a sample of the trade file format, see samples/11490D_13006_trades.xlsx

		Assumption: the input trades are journal trades, without any
		commission. If commission is needed, then we need another output
		template which includes commission.
	"""
	compose(
		print
	  , partial(writeQuickImportCsv, 'quick_import.csv')
	  , partial(map, journalToQuickImport)
	  , getJournalTrades
	  , excelFileToLines
	)(parser.parse_args().file)
