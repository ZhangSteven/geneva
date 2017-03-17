# coding=utf-8
# 
# Reading the tax lot appraisal report from Geneva.
#



from geneva.utility import logger, to_date, to_float, get_output_directory, \
							get_input_directory
from os.path import join
import csv, re



class UnrecognizedCurrency(Exception):
	pass

class FXGenerationError(Exception):
	pass

class TaxLotNotFound(Exception):
	pass



def read_report(csvfile):
	"""
	Read the tax lot appraisal with accruals report, return the tax lots,
	parameters, errors.
	"""
	taxlots = read_taxlot(csvfile)

	# There is one and only one blank line in between tax lots and parameters,
	# and that blank line has been reached at the end of read_taxlot() function.
	parameters = read_parameter(csvfile)
	return taxlots, parameters



def read_taxlot(csvfile):
	reader = csv.DictReader(csvfile, delimiter='\t', restval='')
	taxlots = []
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
		
		taxlots.append(row)
		i = i + 1
	# end of for

	return taxlots



def read_parameter(csvfile):
	reader = csv.DictReader(csvfile, delimiter='\t', restval='')
	parameters = []
	i = 1
	for row in reader:
		logger.debug('read_parameter(): reading parameter {0}'.format(i))
		if row['ParameterName'] == '':
			logger.debug('read_parameter(): it\'s a blank line')
			break	# it's a blank line

		parameters.append(row)
		i = i + 1

	return parameters



def add_info(taxlots, fx):
	"""
	Add the following fields to each non-cash tax lot:

	1. AmortCostLocal: the amortized cost in local currency.

	2. AccruedInterestLocal: the accrued interest in local currency.

	3. TotalAmortValueLocal: the total amortized value in local currency.

	4. InvestID: the investment id embedded in the investment description,
		e.g. if the description is
		EDF 6.5 01/26/19 144A (US268317AB08 HTM), then InvestID is
		US268317AB08 HTM
	
	fx: the dictionary to lookup the fx rate of other currency to HKD. for
		example, fx['USD'] = 0.1282 means 1 HKD is equal to 0.1282 USD.
	"""
	for taxlot in taxlots:
		if is_cash_lot(taxlot):
			continue

		fxrate = fx[get_taxlot_currency(taxlot)]
		taxlot['AmortUnitCostLocal'] = taxlot['UnitCost'] + \
										taxlot['AccruedAmortBook']/taxlot['Quantity']*fxrate*100
		taxlot['AccruedInterestLocal'] = taxlot['AccruedInterestBook']*fxrate
		taxlot['TotalAmortValueLocal'] = taxlot['AmortUnitCostLocal']*taxlot['Quantity']/100 + \
											taxlot['AccruedInterestLocal']
		m = re.search('(\([A-Z0-9]{12}.*\))', taxlot['InvestmentDescription'])
		if m is None:
			logger.warning('add_info(): failed to extract investment id from investment description {0}'.
							format(taxlot['InvestmentDescription']))
			taxlot['InvestID'] = ''
		else:
			taxlot['InvestID'] = m.group(0)[1:-1]

	return taxlots



def is_cash_lot(taxlot):
	if taxlot['ThenByDescription'] == 'Cash and Equivalents':
		return True
	else:
		return False



def get_taxlot_currency(taxlot):
	if taxlot['SortByDescription'] == 'Chinese Renminbi Yuan':
		return 'CNY'
	elif taxlot['SortByDescription'] == 'Hong Kong Dollar':
		return 'HKD'
	elif taxlot['SortByDescription'] == 'United States Dollar':
		return 'USD'
	else:
		logger.error('get_taxlot_currency(): unrecognized currency: {0}'.format(taxlot['SortByDescription']))
		raise UnrecognizedCurrency()



def get_fx_rate(taxlots):
	"""
	Work out the fx rate of other currencies to HKD used in this tax lot appraisal
	report, based on the cash tax lot information.

	Note that the tax lot appraisal report can only show up to 2 decimal
	points for the quantity and market value, so if the quantity for a foreign
	currency (other than HKD) is too low (< 10,000), then fx rate derived cannot
	have enough precision, thus will give an error.
	"""
	fx = {}
	fx['HKD'] = 1.0
	for taxlot in taxlots:
		if is_cash_lot(taxlot) and get_taxlot_currency(taxlot) != 'HKD':
			if taxlot['Quantity'] < 10000:
				logger.error('get_fx_rate(): currency {0} balance {1} is too low'.
								format(get_taxlot_currency(taxlot), taxlot['Quantity']))
				raise FXGenerationError()

			fx[get_taxlot_currency(taxlot)] = taxlot['Quantity']/taxlot['MarketValueBook']

	return fx



def merge_lots(taxlots):
	"""
	Merge multiple lots for the same bond into one lot per bond.
	"""
	merged_lots = []
	for taxlot in taxlots:
		if is_cash_lot(taxlot):
			merged_lots.append(taxlot)
			continue

		try:
			merge_taxlot(find_taxlot(merged_lots, taxlot['InvestmentDescription']), taxlot)
		except TaxLotNotFound:
			merged_lots.append(taxlot)

	return merged_lots



def find_taxlot(taxlots, inv_description):
	for taxlot in taxlots:
		if taxlot['InvestmentDescription'] == inv_description:
			return taxlot

	raise TaxLotNotFound()



def merge_taxlot(ta, tb):
	"""
	Merge tax lot B (tb) into tax lot A (ta).
	"""
	ta['TaxLotID'] = ta['TaxLotID'] + '-' + tb['TaxLotID']
	ta['TaxLotDate'] = ta['TaxLotDate'] + '-' + tb['TaxLotDate']
	ta['UnitCost'] = get_weighted_average(ta['UnitCost'], ta['Quantity'],
											tb['UnitCost'], tb['Quantity'])
	ta['CostBook'] = ta['CostBook'] + tb['CostBook']
	ta['MarketValueBook'] = ta['MarketValueBook'] + tb['MarketValueBook']
	ta['UnrealizedPriceGainLossBook'] = ta['UnrealizedPriceGainLossBook'] + \
											tb['UnrealizedPriceGainLossBook']
	ta['UnrealizedFXGainLossBook'] = ta['UnrealizedFXGainLossBook'] + \
											tb['UnrealizedFXGainLossBook']
	ta['AccruedAmortBook'] = ta['AccruedAmortBook'] + tb['AccruedAmortBook']
	ta['AccruedInterestBook'] = ta['AccruedInterestBook'] + tb['AccruedInterestBook']
	ta['AmortUnitCostLocal'] = get_weighted_average(ta['AmortUnitCostLocal'], ta['Quantity'],
											tb['AmortUnitCostLocal'], tb['Quantity'])
	ta['AccruedInterestLocal'] = ta['AccruedInterestLocal'] + tb['AccruedInterestLocal']
	ta['TotalAmortValueLocal'] = ta['TotalAmortValueLocal'] + tb['TotalAmortValueLocal']
	ta['Quantity'] = ta['Quantity'] + tb['Quantity']



def get_weighted_average(unit_a, quantity_a, unit_b, quantity_b):
	"""
	Compute the weighted average.
	"""
	return (unit_a*quantity_a + unit_b*quantity_b)/(quantity_a + quantity_b)



def filter_out_cash(taxlots):
	taxlots_no_cash = []
	for t in taxlots:
		if not is_cash_lot(t):
			taxlots_no_cash.append(t)

	return taxlots_no_cash



def get_portfolio_id(parameters):
	for p in parameters:
		if p['ParameterName'] == 'Portfolio':
			return p['ParameterValue']

	return ''



def write_csv(taxlots, portfolio_id, output_dir=get_output_directory()):
	with open(join(output_dir, portfolio_id+'_output.csv'), 'w', newline='') as csvfile:
		file_writer = csv.writer(csvfile, delimiter=',')
	
		fields = ['Portfolio', 'InvestID', 'Currency', 'TaxLotDescription', 'Quantity', 
					'UnitCost', 'AmortUnitCostLocal', 'AccruedInterestLocal', 
					'TotalAmortValueLocal']
		file_writer.writerow(fields)
		
		for taxlot in taxlots:
			row = []
			
			for fld in fields:
				if fld == 'Portfolio':
					item = portfolio_id
				elif fld == 'Currency':
					item = get_taxlot_currency(taxlot)
				else:
					try:
						item = taxlot[fld]
					except KeyError:
						item = ''

				row.append(item)

			file_writer.writerow(row)




if __name__ == '__main__':
	import argparse, sys, glob
	from os.path import isdir, exists
	parser = argparse.ArgumentParser(description='Read tax lot files and create csv output containing amortized cost and accrued interest in local currency.')
	parser.add_argument('--folder', help='folder containing multiple tax lot files', required=False)
	parser.add_argument('--file', help='input tax lot file', required=False)
	args = parser.parse_args()

	if not args.file is None:
		file = join(get_input_directory(), args.file)
		if not exists(file):
			print('{0} does not exist'.format(file))
			sys.exit(1)

		files = [file]

	elif not args.folder is None:
		folder = join(get_input_directory(), args.folder)
		if not exists(folder) or not isdir(folder):
			print('{0} is not a valid directory'.format(folder))
			sys.exit(1)

		files = glob.glob(folder+'\\*.xls*')

	else:
		print('Please provide either --file or --folder input')
		sys.exit(1)

	for input_file in files:
		with open(input_file, newline='', encoding='utf-16') as f:
			taxlots, parameters = read_report(f)
			write_csv(filter_out_cash(merge_lots(add_info(taxlots, get_fx_rate(taxlots)))),
						get_portfolio_id(parameters))