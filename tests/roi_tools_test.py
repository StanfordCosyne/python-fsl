#roi_tools_test.py

import sys
import unittest

sys.path.append('../.')

from roi_tools import *

class ROIToolsTest(unittest.TestCase):
	def setUp(self):
		self.roi_file = 'ROIs.csv'
		self.roi_img = '2.nii.gz'
		self.func_img = os.path.join(os.getcwd(), 'filtered_func_data')
		self.test_func = os.path.join(os.getcwd(), 'swarI.nii.gz')
		self.anat_img = '%s/data/standard/avg152T1.nii.gz' % os.environ['FSLDIR']
		self.cleanup = []	

	def tearDown(self):
		pass
		#for item in self.cleanup:
		#	os.remove(item)
	"""
	def test_single_from_seeds(self):
		roi_imgs = single_from_seeds(self.roi_file, os.getcwd())
		self.assertTrue(len(roi_imgs)==2)

		self.cleanup += roi_imgs

	def test_combined_from_seeds(self):
		roi_img = combined_from_seeds(self.roi_file, 'test_combined', os.getcwd())
		self.assertTrue(roi_img == os.path.join(os.getcwd(), 'test_combined.nii.gz'))
		self.cleanup.append(roi_img)

	def test_extract_from_roi(self):
		#single_from_seeds(self.roi_file, os.getcwd())
		value = extract_from_roi(self.anat_img, self.roi_img)
		self.assertTrue(type(value) == float)

	def test_extract_timeseries_from_roi(self):
		name = extract_timeseries_from_roi(self.test_func, self.roi_img, 'test_extract_ts')
		self.assertTrue(name == os.path.join(os.getcwd(), 'test_extract_ts.txt'))

	"""

	def test_label_seed(self):
		d = label_seed(-28, -98, -12)
		self.assertTrue(d['structure'] == 'Fusiform Gyrus' and d['BA'] == '18')

		d = label_seed(25, -98, -12)
		self.assertTrue(d['structure'] == 'Fusiform Gyrus' and d['BA'] == '*' and d['hemisphere'] == 'Right')
		

		
if __name__ == '__main__':
    unittest.main()


