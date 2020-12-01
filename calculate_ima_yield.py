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
import logging
logger = logging.getLogger(__name__)






if __name__ == '__main__':
	import logging.config
	logging.config.fileConfig('logging.config', disable_existing_loggers=False)
