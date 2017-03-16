# coding=utf-8
# 
import configparser, os
from config_logging.file_logger import get_file_logger
from datetime import datetime


class InvalidDateFormat(Exception):
	pass



# initialize config object
if not 'config' in globals():
	config = configparser.ConfigParser()
	config.read('geneva.config')



def get_current_directory():
	"""
	Get the absolute path to the directory where this module is in.

	This piece of code comes from:

	http://stackoverflow.com/questions/3430372/how-to-get-full-path-of-current-files-directory-in-python
	"""
	return os.path.dirname(os.path.abspath(__file__))



# initialize logger
if not 'logger' in globals():
	logger = get_file_logger(os.path.join(get_current_directory(), 'geneva.log'), 
								config['logging']['log_level'])



def get_date_format():
	global config
	return config['data']['date_format']



def get_output_directory():
	global config
	if config['directory']['output'] == '':
		return get_current_directory()
	else:
		return config['directory']['output']



def to_date(date_string, fmt=get_date_format()):
	try:
		if fmt == 'yyyy-mm-dd':
			tokens = date_string.split('-')
			return datetime(int(tokens[0]), int(tokens[1]), int(tokens[2]))
		elif fmt == 'yyyy/mm/dd':
			tokens = date_string.split('/')
			return datetime(int(tokens[0]), int(tokens[1]), int(tokens[2]))
		elif fmt == 'mm/dd/yyyy':
			tokens = date_string.split('/')
			return datetime(int(tokens[2]), int(tokens[0]), int(tokens[1]))
		elif fmt == 'dd/mm/yyyy':
			tokens = date_string.split('/')
			return datetime(int(tokens[2]), int(tokens[1]), int(tokens[0]))
		else:
			logger.error('to_date(): invalid date format {0}'.format(fmt))
			raise InvalidDateFormat()

	except:
		logger.exception('to_date(): failed to convert date string {0}, fmt={1}'.format(date_string, fmt))
		raise



def to_float(float_string):
	return float(''.join(float_string.split(',')))