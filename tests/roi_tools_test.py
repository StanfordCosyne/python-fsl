#roi_tools_test.py

import sys
import unittest

sys.path.append('../.')

from roi_tools import *

class ROIToolsTest(unittest.TestCase):
	def setUp(self):
		self.roi_file = 'ROIs.csv'
		self.cleanup = []	

	def tearDown(self):
		for item in self.cleanup:
			os.remove(item)

	def test_single_from_seeds(self):
		roi_imgs = single_from_seeds(self.roi_file, os.getcwd())
		self.assertTrue(len(roi_imgs)==2)

		self.cleanup += roi_imgs

	def test_combined_from_seeds(self):
		roi_img = combined_from_seeds(self.roi_file, 'test_combined', os.getcwd())
		self.assertTrue(roi_img == os.path.join(os.getcwd(), 'test_combined.nii.gz'))
		self.cleanup.append(roi_img)


if __name__ == '__main__':
    unittest.main()


