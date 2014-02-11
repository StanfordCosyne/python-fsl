#voxel_inspector.py
from common import *

from subprocess import call

#list of scan_ids you want to inspect
sub_list = '../quasi_ev/con_subjects.txt' 

lines = open(sub_list, "r").readlines()

for line in lines:
	line = line.strip()
	path = path_from_scan(line, 'musk2')
	con_path = os.path.join(path, 'stats_spm8', 'christian_quasi_ev', 'spmT_0001')
	command = ['slicer', con_path, '-x', '0.5', '%s.png' % line]
	call(command)
