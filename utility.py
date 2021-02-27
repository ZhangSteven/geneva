# coding=utf-8
#
# Calculate portfolio yield
# 

import configparser


def _loadConfig():
	config = configparser.ConfigParser()
	config.read('yield_calculation.config')
	return config



# initialized only once when this module is first imported by others
if not 'config' in globals():
	config = _loadConfig()



def getMailSender():
	global config
	return config['email']['sender']



def getMailServer():
	global config
	return config['email']['server']



def getMailTimeout():
	global config
	return float(config['email']['timeout'])



def getNotificationMailRecipients():
	global config
	return config['email']['notificationMailRecipients']



def getDataDirectory():
	global config
	return config['Input']['dataDirectory']



def getImaDataDirectory():
	global config
	return config['Input']['IMAdataDirectory']



def getUserConfigFile():
	global config
	return config['Input']['userConfigFile']
