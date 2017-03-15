# coding=utf-8
# 
# Reading a simple csv file.



from geneva.utility import logger, to_date, to_float
import csv



def read_content():
	with open('samples\\csv_sample1.csv', newline='', encoding='ascii') as f:
		reader = csv.reader(f)
		for row in reader:
			print(row)



def read_content2():
	with open('samples\\csv_sample1.csv', newline='', encoding='ascii') as f:
		reader = csv.DictReader(f)
		for row in reader:
			for key in row:
				print('{0}: {1}'.format(key, row[key]))




def read_content3():
	with open('samples\\csv_sample1.csv', newline='', encoding='ascii') as f:
		reader = csv.DictReader(f)
		content = []
		for row in reader:
			for key in row:
				if key == 'Date':
					row[key] = to_date(row[key])
				elif key in ['Quantity', 'Price']:
					row[key] = to_float(row[key])

			content.append(row)

		return content



def read_taxlot(csvfile):
	"""
	Read the tax lot report, separator is tab.
	"""
	reader = csv.DictReader(csvfile, delimiter='\t', restval='')
	content = []
	i = 1
	for row in reader:
		logger.debug('read_taxlot(): reading record {0}'.format(i))
		if row['SortByDescription'] == '' and row['ThenByDescription'] == '':
			logger.debug('read_taxlot(): it\'s a blank line')
			break	# it's a blank line

		for key in row:
			if key in ['Quantity', 'OriginalFace', 'UnitCost', 'CostBook', 
						'MarketValueBook', 'UnrealizedPriceGainLossBook', 
						'UnrealizedFXGainLossBook', 'AccruedAmortBook', 
						'AccruedInterestBook']:
	
				row[key] = to_float(row[key])

			elif key == 'MarketPrice':
				try:
					row[key] = to_float(row[key])
				except:
					logger.warning('market price is not available for record {0}'.format(i))
		
		content.append(row)
		i = i + 1
	# end of for

	return content



def show(content):
	for record in content:
		for key in record:
			print('{0}: {1}'.format(key, record[key]))




if __name__ == '__main__':
	# read_content()
	# read_content2()
	# show(read_content3())

	# Geneva saves csv files as unicode text, after trying ascii, utf-8 and
	# gbk, finally utf-16 works.
	with open('samples\\test-12345 taxlot.txt', newline='', encoding='utf-16') as f:
		content = read_taxlot(f)
		# print(len(content))
		show(content)
