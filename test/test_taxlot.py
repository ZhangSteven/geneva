"""
Test the read_holding() method from open_holding.py

"""

import unittest2
from geneva.taxlot import read_report, get_fx_rate, add_info, merge_lots, \
                            get_portfolio_id
from geneva.utility import get_current_directory
from os.path import join



class TestTaxlot(unittest2.TestCase):

    def __init__(self, *args, **kwargs):
        super(TestTaxlot, self).__init__(*args, **kwargs)

    def setUp(self):
        """
            Run before a test function
        """
        pass

    def tearDown(self):
        """
            Run after a test finishes
        """
        pass



    def test_read_report(self):
        filename = join(get_current_directory(), 'samples', 'test-12345 taxlot.txt')
        with open(filename, newline='', encoding='utf-16') as f:
            taxlots, parameters = read_report(f)
            self.assertEqual(len(taxlots), 10)
            self.assertEqual(get_portfolio_id(parameters), 'Test-12345')
            self.verify_lot1(taxlots[0])
            self.verify_lot2(taxlots[9])



    def test_get_fx_rate(self):
        filename = join(get_current_directory(), 'samples', 'test-12345 taxlot.txt')
        with open(filename, newline='', encoding='utf-16') as f:
            taxlots, parameters = read_report(f)
            fx = get_fx_rate(taxlots)
            self.assertEqual(len(fx), 3)
            self.assertAlmostEqual(fx['USD'], 0.128729950)
            self.assertAlmostEqual(fx['CNY'], 0.889704179)
            self.assertEqual(fx['HKD'], 1.0)



    def test_add_info(self):
        filename = join(get_current_directory(), 'samples', 'test-12345 taxlot.txt')
        with open(filename, newline='', encoding='utf-16') as f:
            taxlots, parameters = read_report(f)
            taxlots = add_info(taxlots, get_fx_rate(taxlots))
            self.assertEqual(len(taxlots), 10)
            self.verify_lot1(taxlots[0])    # cash lot shouldn't change
            self.verify_added_lot1(taxlots[1])  # CNY
            self.verify_added_lot2(taxlots[9])  # USD
            self.verify_added_lot3(taxlots[4])  # HKD



    def test_merge_lots(self):
        filename = join(get_current_directory(), 'samples', 'test-12345 taxlot.txt')
        with open(filename, newline='', encoding='utf-16') as f:
            taxlots, parameters = read_report(f)
            taxlots = merge_lots(add_info(taxlots, get_fx_rate(taxlots)))
            self.assertEqual(len(taxlots), 8)
            self.verify_merged_lot1(taxlots[1])



    def verify_lot1(self, record):
        """
        First tax lot in test-12345 taxlot.txt
        """
        self.assertEqual(len(record), 18)
        self.assertEqual(record['SortByDescription'], 'Chinese Renminbi Yuan')
        self.assertEqual(record['TaxLotID'], '')
        self.assertAlmostEqual(record['Quantity'], 8533168.41)
        self.assertEqual(record['OriginalFace'], 0)
        self.assertAlmostEqual(record['UnitCost'], 1.0002)
        self.assertAlmostEqual(record['UnrealizedFXGainLossBook'], 1056233.01)
        self.assertEqual(record['ExtendedDescription'], '')
        


    def verify_lot2(self, record):
        """
        Last tax lot in test-12345 taxlot.txt
        """
        self.assertEqual(len(record), 18)
        self.assertEqual(record['SortByDescription'], 'United States Dollar')
        self.assertEqual(record['TaxLotDescription'], 'HKCGAS 6.25 08/07/18 REGS')
        self.assertAlmostEqual(record['TaxLotID'], '1008876')
        self.assertEqual(record['Quantity'], 270000)
        self.assertAlmostEqual(record['UnitCost'], 113.8)
        self.assertAlmostEqual(record['MarketPrice'], 'NA')
        self.assertAlmostEqual(record['CostBook'], 2396723.87)
        self.assertAlmostEqual(record['AccruedAmortBook'], -82492.55)



    def verify_added_lot1(self, record):
        """
        First CNY bond tax lot in test-12345 taxlot.txt
        """
        self.assertEqual(len(record), 22)
        self.assertEqual(record['SortByDescription'], 'Chinese Renminbi Yuan')
        self.assertEqual(record['TaxLotDescription'], 'BJEHF 6.15 08/07/21')
        self.assertAlmostEqual(record['TaxLotID'], '1008871')
        self.assertEqual(record['TaxLotDate'], '8/1/2012')
        self.assertEqual(record['Quantity'], 153000)
        self.assertAlmostEqual(record['UnitCost'], 95.75)
        self.assertAlmostEqual(record['MarketPrice'], 'NA')
        self.assertAlmostEqual(record['CostBook'], 176503.01)
        self.assertEqual(record['InvestID'], 'HK0000120748 HTM')
        self.assertAlmostEqual(record['AccruedAmortBook'], 3167.02)
        self.assertAlmostEqual(record['AmortUnitCostLocal'], 97.59164113)
        self.assertAlmostEqual(record['AccruedInterestLocal'], 953.8429529)
        self.assertAlmostEqual(record['TotalAmortValueLocal'], 150269.053881)



    def verify_added_lot2(self, record):
        """
        Last USD bond tax lot in test-12345 taxlot.txt
        """
        self.assertEqual(len(record), 22)
        self.assertEqual(record['SortByDescription'], 'United States Dollar')
        self.assertEqual(record['TaxLotDescription'], 'HKCGAS 6.25 08/07/18 REGS')
        self.assertAlmostEqual(record['TaxLotID'], '1008876')
        self.assertEqual(record['Quantity'], 270000)
        self.assertAlmostEqual(record['UnitCost'], 113.8)
        self.assertAlmostEqual(record['MarketPrice'], 'NA')
        self.assertAlmostEqual(record['CostBook'], 2396723.87)
        self.assertAlmostEqual(record['AccruedAmortBook'], -82492.55)
        self.assertEqual(record['InvestID'], 'USY32358AA46 HTM')
        self.assertAlmostEqual(record['AmortUnitCostLocal'], 109.8669401)
        self.assertAlmostEqual(record['AccruedInterestLocal'], 1828.1249195)
        self.assertAlmostEqual(record['TotalAmortValueLocal'], 298468.8630571)



    def verify_added_lot3(self, record):
        """
        First HKD bond tax lot in test-12345 taxlot.txt
        """
        self.assertEqual(len(record), 22)
        self.assertEqual(record['SortByDescription'], 'Hong Kong Dollar')
        self.assertEqual(record['TaxLotDescription'], 'CHMERC 6 03/21/22')
        self.assertAlmostEqual(record['TaxLotID'], '1008877')
        self.assertEqual(record['Quantity'], 756000)
        self.assertAlmostEqual(record['UnitCost'], 99.5)
        self.assertAlmostEqual(record['MarketPrice'], 'NA')
        self.assertAlmostEqual(record['CostBook'], 752220)
        self.assertAlmostEqual(record['AccruedAmortBook'], 1666.29)
        self.assertEqual(record['InvestID'], 'HK0000175916 HTM')
        self.assertAlmostEqual(record['AmortUnitCostLocal'], 99.72040873)
        self.assertAlmostEqual(record['AccruedInterestLocal'], 21872.22)
        self.assertAlmostEqual(record['TotalAmortValueLocal'], 775758.51)



    def verify_merged_lot1(self, record):
        """
        Merged lot of the first and second CNY bond tax lot in
        test-12345 taxlot.txt
        """
        self.assertEqual(len(record), 22)
        self.assertEqual(record['SortByDescription'], 'Chinese Renminbi Yuan')
        self.assertEqual(record['TaxLotDescription'], 'BJEHF 6.15 08/07/21')
        self.assertEqual(record['TaxLotID'], '1008871-1008872')
        self.assertEqual(record['TaxLotDate'], '8/1/2012-10/1/2013')
        self.assertEqual(record['Quantity'], 411000)
        self.assertAlmostEqual(record['UnitCost'], 102.7429927)
        self.assertAlmostEqual(record['OriginalFace'], 0)
        self.assertAlmostEqual(record['MarketPrice'], 'NA')
        self.assertAlmostEqual(record['CostBook'], 508763.49)
        self.assertAlmostEqual(record['MarketValueBook'], 469946.12)
        self.assertAlmostEqual(record['UnrealizedPriceGainLossBook'], 0)
        self.assertAlmostEqual(record['UnrealizedFXGainLossBook'], -34140.91)
        self.assertAlmostEqual(record['AccruedAmortBook'], -4676.46)
        self.assertAlmostEqual(record['AccruedInterestBook'], 2879.92)
        self.assertEqual(record['InvestID'], 'HK0000120748 HTM')
        self.assertAlmostEqual(record['AmortUnitCostLocal'], 101.73066521)
        self.assertAlmostEqual(record['AccruedInterestLocal'], 2562.276858317)
        self.assertAlmostEqual(record['TotalAmortValueLocal'], 420675.3108548)