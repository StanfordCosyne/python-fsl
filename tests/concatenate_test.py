#contatenate_test.py

import sys
import unittest
import glob
import os
from subprocess import Popen, PIPE

sys.path.append('../.')

import concatenate as concat

class ConcatenateTest(unittest.TestCase):
	def setUp(self):
		self.img = 'filtered_func_data'

	def tearDown(self):
		files = glob.glob("*split*") + glob.glob("*chunk*")
		for f in files:
			os.remove(f)

		#os.remove('test_merged.nii.gz')


	def test_split(self):
		images = concat.split(self.img)
		self.assertTrue(len(images) == 180)
	
	def test_merge(self):
		images = concat.split(self.img)
		image = concat.merge(images, 'test_merged')
		self.assertTrue(image == 'test_merged')

	def test_concatenate_filename(self):
		merged_img = concat.concatenate(self.img, [[2, 12], [15, 25], [36, 56]]) 
		self.assertTrue(merged_img == 'filtered_func_data_merged')

	def test_concatenate_voxels(self):
		merged_img = concat.concatenate(self.img, [[10, 50], [55, 75], [100, 105]])

		command = ['fslmeants', '-i', merged_img, '-c', '33', '28', '11']
		output = Popen(command, stdout=PIPE).communicate()[0].split('\n')

		#TR 10
		t1 = int(float(output[0]))
		#TR 40
		t2 = int(float(output[30]))  		

		self.assertTrue(t1==12227)
		self.assertTrue(t2==12420)

		command = ['fslmeants', '-i', merged_img, '-c', '39', '28', '16']
		output = Popen(command, stdout=PIPE).communicate()[0].split('\n')

		#TR 60
		t3 = int(float(output[59]))
		#TR 65
		t4 = int(float(output[64]))  		

		self.assertTrue(t1==12227)
		self.assertTrue(t2==12420)


	
if __name__ == '__main__':
    unittest.main()


