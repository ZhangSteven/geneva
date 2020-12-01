# coding=utf-8
#
# From an investment report, give statistics on the number of unique investments
# in each category (except cash and FX Forward).
# 

from geneva.report import readExcelReport
from utils.utility import writeCsv
from toolz.itertoolz import groupby as groupbyToolz
from toolz.dicttoolz import valmap
from toolz.functoolz import compose
from itertools import filterfalse, chain
from functools import partial
import logging
logger = logging.getLogger(__name__)



def count(positions):
	"""
	[Iterable] positions => 
		[Dictionary] investment type -> number of unique positions in that type
	"""
	def countUnique(positions):
		"""
		[Iterator] positions => [Int] count of unique positions by their description
		"""
		return len({p['Description'] for p in positions})


	return compose(
		partial(valmap, countUnique)
	  , partial(groupbyToolz, lambda p: p['SortKey'])
	  , partial( filterfalse
	  		   , lambda p: p['SortKey'] in ['Cash and Equivalents', 'FX Forward'])
	)(positions)



getCsvFilename = lambda metaData: \
	'investment types ' + metaData['Portfolio'] + ' ' + metaData['PeriodEndDate'] + '.csv'



"""
	[String] filename, [Dictionary] typeCount => [String] output csv name
"""
writeOutputCsv = lambda filename, typeCount: \
	writeCsv( filename
			, chain( [('InvestmentType', 'UniquePositionCount')]
				   , typeCount.items())
			)




if __name__ == '__main__':
	import logging.config
	logging.config.fileConfig('logging.config', disable_existing_loggers=False)

	import argparse
	parser = argparse.ArgumentParser(description='Give statistics of investment types')
	parser.add_argument( 'file', metavar='file', type=str
					   , help='investment position report')


	"""
		Generate an investment position report, then:

		$python count_investment.py <file name with path>

		Example:

		$python count_investment.py samples/investment01.xlsx

	"""
	positions, metaData = readExcelReport(parser.parse_args().file)
	print(writeOutputCsv(getCsvFilename(metaData), count(positions)))