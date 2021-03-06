import nibabel
import numpy as np
from subprocess import call, Popen, PIPE
import os, csv, glob

def label_seed(x, y, z):
	"""given a seed in MNI space, assign a label
	"""
	d = {'hemisphere':'', 'lobe':'', 'structure':'', 'BA':''}

	if x < 0:
		d['hemisphere'] = 'Left'
	else:
		d['hemisphere'] = 'Right'

	command = ['atlasquery', '-a', 'Talairach Daemon Labels', '-c', '%s,%s,%s' % (x, y, z)]

	tal = Popen(command, stdout=PIPE).communicate()[0]
	tal = tal.split('<br>')[-1].split('.')
	d['lobe'] = tal[1]
	d['structure'] = tal[2]
	d['BA'] = tal[4].split(' ')[-1].strip()

	print d

	return d


def extract_timeseries_from_roi(func_img, roi, name, convert=False):
	"""func_img - functional image (nifti)
	roi - roi to extract timeseries from
	name - name of the output file
	convert = bool indicating whether func_img needs to be converted to nifti
	"""

	name = "%s.txt" % name

	#make a temporary nifti file
	if convert:
		command = ['fslchfiletype', 'NIFTI', func_img, 'nifti']
		call(command)
		func_img = 'nifti'

	command = ['fslmeants', '-i', func_img, '-o', name, '-m', roi]	
	call(command)

	if os.path.exists(name):
		return os.path.join(os.getcwd(), name)
	else:
		return False

def extract_from_roi(func_img, roi, convert=False):
	"""func_img - functional image (nifti)
	rois - list of rois to extract from
	convert - bool indicating whether the functional image needs to be converted ot nifti
	"""

	#make a temporary nifti file
	if convert:
		command = ['fslchfiletype', 'NIFTI', func_img, 'nifti']
		call(command)
		func_img = 'nifti'

	#temp file name
	#extract the masked voxels into a temporary file
	tempfile = '%s_tempfile' % roi
	command = ['fslmaths', func_img, '-mas', roi, tempfile]
	call(command)
	#extract the dang ol' ROI value
	command = ['fslstats', tempfile, '-n', '-M']
	output = Popen(command, stdout=PIPE).communicate()[0]
	try:
		beta = float(output)
	except:
		print "no beta value for %s" % tempfile
		beta = "NA"

	#remove the temp roi
	command = ['rm', '%s.nii.gz' % tempfile, '-r']
	call(command)

	return beta

def single_from_seeds(roi_file, output_dir = "ROIs"):
	"""take a list of seeds and draw spheres of a given size in MNI 2mm space
	roi_file - .csv, see tests for details
	output_dir - where to draw the ROI files
	"""

	atlas_img = "%s/data/atlases/MNI/MNI-maxprob-thr0-2mm.nii.gz" % os.environ['FSLDIR']

	rows = csv.DictReader(open(roi_file, 'r'))

	#create the individual ROIs
	count = 1

	roi_images = []

	for row in rows:
		name = "%s/%s" % (output_dir, row['id'])
		command = ['fslmaths', atlas_img, '-mul', '0', '-add', '1', '-roi', row['x'], '1', row['y'], '1', row['z'], '1', '0', '1', name, '-odt', 'float']
		call(command)
		command = ['fslmaths', name, '-kernel', 'sphere', '%s' % (int(row['radius'])/2), '-fmean', name, '-odt', 'float']
		call(command)

		#now that we have an image, we gotta make a new one
		ROI = nibabel.load(name + ".nii.gz")
		header = ROI._header
		affine= ROI.get_affine()
		roi_data = ROI.get_data()
		orig_shape = roi_data.shape

		#flatten
		roi_data = np.ravel(roi_data)

		#create an with index #s
		non_zero = np.nonzero(roi_data)
		new_roi = np.zeros(roi_data.shape)
		new_roi[non_zero] = int(row['id'])
		new_roi = new_roi.reshape(orig_shape)
		new_roi_img = nibabel.Nifti1Image(new_roi, affine)
		new_roi_img._header = header
		new_roi_img.to_filename(name + ".nii.gz")
		roi_images.append(name + ".nii.gz")
	
	return roi_images

def combined_from_seeds(roi_file, name, output_dir = "ROIs"):
	roi_images = single_from_seeds(roi_file, output_dir)		

	start_img = roi_images.pop()

	for roi in roi_images:
		roi_name = os.path.join(os.getcwd(), output_dir, name)
		command = ['fslmaths', start_img, '-add', roi, roi_name]
		start_img = roi_name
		call(command)

	return roi_name + ".nii.gz"

	

def make_figures(roi_list):
	"""	roi_list - a list of ROI images (nii)
	"""

	for roi in roi_list:
		#draw a picture of it for slides/figures etc
		x = int(row[8]) / 91.
		y = int(row[9]) / 109.
		z = int(row[10]) / 91.
		standard = '%s/data/standard/avg152T1_brain.nii.gz' % os.environ['FSLDIR']

		command = ['overlay', '0', '1', standard, '3000', '8000', name, '0.01', '0.012', '%s_overlay' % name]
		call(command)

		command = ['slicer', '%s_overlay' % name, '-L', '-x', str(x), '%s_x.ppm' % name]
		call(command)
		command = ['slicer', '%s_overlay' % name, '-L', '-y', str(y), '%s_y.ppm' % name]
		call(command)
		command = ['slicer', '%s_overlay' % name, '-L', '-z', str(z), '%s_z.ppm' % name]
		call(command)

		count += 1

	#now sum up all the images so we can look for collisions
	images = []
	for item in glob.glob('%s/*.nii.gz' % output_dir):
		if item.count("overlay"):
			pass
		else:
			images.append(item)

	start_img = images.pop()

	for img in images:
		command = ['fslmaths', start_img, '-add', img, '%s/summed_ROIs' % output_dir]
		start_img = '%s/summed_ROIs' % output_dir
		call(command)
