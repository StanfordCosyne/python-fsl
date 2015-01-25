#voxel_inspector.py
from common import *

from subprocess import call, Popen, PIPE
import csv
import pylab
import copy

#list of scan_ids you want to inspect
sub_list = '../addblock_gppi/sub_age_addblock_gppi.csv'

r = csv.reader(open(sub_list, "r"))
r.next()

bad = []

standard = '/mnt/mapricot/musk2/local/fsl/data/standard/avg152T1_brain.nii.gz'

last_sid = None

Xs = []
Ys = []

for row in r:
	sid = row[0]
	visit = row[4]
	if last_sid != sid:
		pylab.plot(Xs, Ys)
		Xs = []
		Ys = []
		last_sid = copy.deepcopy(sid)

	age = float(row[1])
	Xs.append(age)
	path = row[6]
	path = path.replace('0001', '0011').replace('.img', '')
	#con_path = os.path.join(path, 'stats_spm8', 'christian_addblock_gppi_gPPI', 'PPI_left_aIPS', 'spmT_0001')
#	print con_path

	#command = ['slices', path, standard, '-z', '0.3', '-i', '-1', '1']
	#command = ['slicer', con_path, '-a', '%s_add.png' % line]
	#command = ['fslview', '/mnt/mapricot/musk2/local/fsl/data/standard/avg152T1_brain.nii.gz', path, '-b', '-2', '2']
	#print command
	#call(command)

	command = ['fslmeants', '-i', path, '-c', '27', '49', '29']
	output = Popen(command, stdout=PIPE).communicate()[0]
	output = float(output)
	#print output, path
	Ys.append(output)

	if abs(output) >= 3.5:
		print sid, visit, output, path
	
	#call(command)

	#good = raw_input("good?: ")
	#if good:
		#bad.append("%s, %s" % (con_path, good))
#pylab.scatter(Xs, Ys)
pylab.show()

print bad
