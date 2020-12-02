# coding=utf-8
#
# Calculate yield (IMA)
# 

from geneva.report import readCashLedgerTxtReport
from utils.utility import allEquals, writeCsv
from utils.file import getFiles
from toolz.functoolz import compose
from itertools import accumulate, count, chain
from functools import partial
from os.path import join
from datetime import datetime
import logging
logger = logging.getLogger(__name__)


# 1. get list of CL files;
# 2. get list (period end date, positions)
# 3. sort by period end date;
# 4. getAccumulatedTimeWeightedCapital()


def getAccumulatedTimeWeightedCapital(sortedCLPositions):
	"""
	[Iterable] (period end date, positions of that period)
	=> [Iterable] Float (time weighted return at each period end date)

	"""
	return compose(
		partial(map, lambda t: getTimeWeightedCapital(t[0], t[1]))
	  , partial( accumulate
	  		   , lambda t1, t2: (t2[0], t1[1] + t2[1]))
	)(sortedCLPositions)



def getTimeWeightedCapital(reportDate, positions):
	"""
	[String] report date (yyyy-mm-dd),
	[Iterable] cash leger positions,
		=> [Float] time weighted capital
	"""
	stringToDate = lambda d: \
		datetime.strptime(d, '%Y-%m-%d')


	# [String] day1 (yyyy-mm-dd), [String] day2 (yyyy-mm-dd) => [Int] days
	getDaysDifference = lambda day1, day2: \
		(stringToDate(day2) - stringToDate(day1)).days


	getDays = lambda tranType, cashDate, reportDate :\
		getDaysDifference(cashDate, reportDate) if tranType in ['Interest', 'Mature'] \
		else getDaysDifference(cashDate, reportDate) + 1


	getTimeWeightAmount = lambda reportDate, p: \
		p['BookAmount'] * getDays(p['TranDescription'], p['CashDate'], reportDate)/365.0


	return \
	compose(
		sum
	  , partial(map, partial(getTimeWeightAmount, reportDate))
	  , partial( filter
	  		   , lambda p: p['TranDescription'] in ['Interest', 'Mature', 'Withdraw', 'Deposit'])
	)(positions)



if __name__ == '__main__':
	import logging.config
	logging.config.fileConfig('logging.config', disable_existing_loggers=False)
