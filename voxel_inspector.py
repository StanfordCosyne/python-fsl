#voxel_inspector.py
from common import *

from subprocess import call

#list of scan_ids you want to inspect
task = "sub"

sub_list = '../both_blocks/%s_subjects.txt' % task

lines = open(sub_list, "r").readlines()

bad = []

for line in lines:
	line = line.strip()
	path = path_from_scan(line, 'musk2')
	con_path = os.path.join(path, 'stats_spm8', 'christian_%sblock' % task, 'spmT_0001')
#	print con_path

	#command = ['slicer', con_path, '-x', '0.5', '%s.png' % line]
	#command = ['slicer', con_path, '-a', '%s_add.png' % line]
	command = ['slices', con_path ,'/mnt/mapricot/musk2/local/fsl/data/standard/avg152T1_brain.nii.gz']
	call(command)

	good = raw_input("good?: ")
	if good:
		bad.append("%s, %s" % (con_path, good))

print bad
