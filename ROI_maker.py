import nibabel
import numpy as np
from subprocess import call
import os, csv, glob

mask_img = "../addblock/001_comp-simp/mask.img"
atlas_img = "/mnt/mapricot/musk2/local/fsl/data/atlases/MNI/MNI-maxprob-thr0-2mm.nii.gz"

def makeROIsFromSeeds(radius=2):
	"""take a list of seeds and draw spheres of a given size in MNI 2mm space
	"""

	roi_file = "../arithmetic-growth-curve/ROIs.csv"
	rows = csv.reader(open(roi_file, 'r'))
	rows.next()

	coords = []
	
	#create the individual ROIs
	count = 1
	for row in rows:
		side = row[0]
		cortex = row[1]
		structure = row[2]
		name = "ROIs/%i_%s_%s_%s" % (count, side[0], cortex, structure)
		#command = ['fslmaths', atlas_img, '-mul', '0', '-add', '1', '-roi', row[8], '1', row[9], '1', row[10], '1', '0', '1', name, '-odt', 'float']
		#print command
		#call(command)
		command = ['fslmaths', name, '-kernel', 'sphere', '5', '-fmean', "%s" % name, '-odt', 'float']
		#call(command)
		command = ['fslmaths', name, '-mul', '80.1', name, '-odt', 'float']
		#call(command)
		print command

		#draw a picture of it for slides/figures etc
		x = int(row[8]) / 91.
		y = int(row[9]) / 109.
		z = int(row[10]) / 91.
		standard = '/mnt/mapricot/musk2/local/fsl/data/standard/avg152T1_brain.nii.gz'
		lut = '/mnt/mapricot/musk2/local/fsl/etc/render3.lut'

		command = ['overlay', '0', '1', standard, '3000', '8000', name, '0.01', '0.012', '%s_overlay' % name]
		call(command)

		#command = ['slicer', '/mnt/mapricot/musk2/local/fsl/data/standard/avg152T1_brain.nii.gz', name, '-L', '-x', str(x), '%s_x.ppm' % name]
		command = ['slicer', '%s_overlay' % name, '-L', '-x', str(x), '%s_x.ppm' % name]
		call(command)
		command = ['slicer', '%s_overlay' % name, '-L', '-y', str(y), '%s_y.ppm' % name]
		call(command)
		command = ['slicer', '%s_overlay' % name, '-L', '-z', str(z), '%s_z.ppm' % name]
		call(command)

		count += 1

	#now sum up all the images so we can look for collisions
	images = glob.glob('ROIs/*.nii.gz')
	start_img = images.pop()

	for img in images:
		command = ['fslmaths', start_img, '-add', img, 'summed_ROIs']
		start_img = 'summed_ROIs'
		#call(command)

	
	


def makeROIs():
	"""take a mask image from group stats and bust it up into its component parts from an atlas
	"""

	mask_img = "../addblock_comp/001T_comp-simp/mask.img"
	atlas_img = "/mnt/mapricot/musk2/local/fsl/data/atlases/MNI/MNI-maxprob-thr0-2mm.nii.gz"

	roi_name = "../masks/addcomp_ROI_%i.nii"

	mask = nibabel.load(mask_img)
	atlas = nibabel.load(atlas_img)

	header = mask._header

	print header

	affine= atlas.get_affine()

	mask_data = mask.get_data()
	atlas_data = atlas.get_data()

	orig_shape = atlas_data.shape

	#flatten
	mask_data = np.ravel(mask_data)
	atlas_data = np.ravel(atlas_data)

	#apply the mask to the atlas
	non_zero = np.nonzero(mask_data)
	masked_atlas = np.zeros(atlas_data.shape)
	masked_atlas[non_zero] = atlas_data[non_zero]

	#now iterate through the ROIs and create a nifti file for each
	for roi in np.unique(masked_atlas):
		indexes = np.where(masked_atlas==roi)
		ROI = np.zeros(atlas_data.shape)
		ROI[indexes] = roi
		ROI = ROI.reshape(orig_shape)
		roi_img = nibabel.Nifti1Image(ROI, affine)
		roi_img._header = header
		roi_img.to_filename(roi_name % roi)

def text_to_nii(model, value, ROIs, directory="."):
	files=[]
	for roi in ROIs:
		txt_file = "%s_%s_subcomp_ROI_%s_img.txt" % (model, value, roi)
		#txt_file = "%s_%s_MNI_2mm_ROI_%s_img.txt" % (model, value, roi)
		nii_file = "%s_%s_MNI_2mm_ROI_%s_img" % (model, value, roi)
		command = ['fslascii2img', os.path.join(directory, txt_file), "91", "109", "91", "1", "2", "2", "2", "2", os.path.join(directory, nii_file)]
		call(command)

def split_text(model, ROIs, directory):
	for roi in ROIs:
		inters = []
		slopes = []
		slope2s = []

		#txt_file = "%s_terms_MNI_2mm_ROI_%s_img.txt" % (model, roi)
		txt_file = "%s_terms_subcomp_ROI_%s_img.txt" % (model, roi)
		path = os.path.join(directory, txt_file)
		for row in open(path, 'r').readlines():
			row = row.strip()
			row = row.strip("\"")
			inter = 0
			slope = 0
			slope2 = 0

			if row != "0":
				frags = row.split(",")
				inter = float(frags[0])
				slope = float(frags[1])
				if len(frags) == 3:
					slope2 = float(frags[2])

			inters.append(inter)
			slopes.append(slope)
			slope2s.append(slope2)

		inters = np.array(inters)
		slope = np.array(slopes)
		slope2 = np.array(slope2s)

		np.savetxt("%s/%s_inters_subcomp_ROI_%s_img.txt" % (directory, model, roi), inters)
		np.savetxt("%s/%s_slope_subcomp_ROI_%s_img.txt" % (directory, model, roi), slope)
		np.savetxt("%s/%s_slope2_subcomp_ROI_%s_img.txt" % (directory, model, roi), slope2)


def combineROIs(model, value, ROIs, directory="."):
	files=[]
	for roi in ROIs:
		fileName = "%s_%s_MNI_2mm_ROI_%s_img.nii.gz" % (model, value, roi)

		files.append("%s/%s" % (directory, fileName))

	#load atlas and transform
	atlas = nibabel.load(atlas_img)
	affine = atlas.get_affine()
	atlas_data = atlas.get_data()
	orig_shape = atlas_data.shape

	#flatten atlas, create new image from it
	atlas_data = np.ravel(atlas_data)
	master_img = np.zeros(atlas_data.shape)


	d ={}
	d['tval'] = -1
	d['pval'] = -1
	d['slope'] = 0
	d['inters'] = 0
	d['slope2'] = 0

	for roi_file in files:
		print roi_file
		roi = nibabel.load(roi_file)
		#load and flatten data
		roi_data = roi.get_data()
		roi_data = np.ravel(roi_data)

		#add values to new image
		i = roi_data != d[value]
		nz = np.nonzero(i)
		master_img[nz] = roi_data[nz]

	master_img = master_img.reshape(orig_shape)
	master_img = nibabel.Nifti1Image(master_img, affine)
	master_img.to_filename("%s/master_%s_%s.nii" % (directory, model, value))


	ROIs = [1,2,3,4,5,6,7,8,9]
	#path = "../subblock/con_0005"

def process_LME_output(path):
	#ROIs = [3,4,5,6,7,8,9]
	ROIs = [1, 2, 3, 4, 5, 6, 7, 8 ,9]
	#path = "../subblock/con_0005"

	model = "lin"

	split_text(model, ROIs, path)

	text_to_nii(model, "tval", ROIs, path)
	text_to_nii(model, "pval", ROIs, path)
	combineROIs(model, "tval", ROIs, path)
	combineROIs(model, "pval", ROIs, path)
	text_to_nii(model, "inters", ROIs, path)
	text_to_nii(model, "slope", ROIs, path)
	combineROIs(model, "inters", ROIs, path)	
	combineROIs(model, "slope", ROIs, path)

	model = "indiv"

	split_text(model, ROIs, path)

	text_to_nii(model, "tval", ROIs, path)
	text_to_nii(model, "pval", ROIs, path)
	text_to_nii(model, "inters", ROIs, path)
	text_to_nii(model, "slope", ROIs, path)
	text_to_nii(model, "slope2", ROIs, path)

	combineROIs(model, "inters", ROIs, path)
	combineROIs(model, "slope", ROIs, path)	
	combineROIs(model, "slope2", ROIs, path)
	combineROIs(model, "tval", ROIs, path)
	combineROIs(model, "pval", ROIs, path)


#makeROIs()
"""
process_LME_output("../addblock_comp/comp-simp")
process_LME_output("../addblock_comp/comp-rest")
process_LME_output("../addblock_comp/simp-rest")
process_LME_output("../addblock_comp/comp-find")
process_LME_output("../addblock_comp/simp-find")
process_LME_output("../addblock_comp/math-rest")
process_LME_output("../addblock_comp/find-rest")

process_LME_output("../subblock_comp/comp-rest")
process_LME_output("../subblock_comp/simp-rest")
process_LME_output("../subblock_comp/comp-find")
process_LME_output("../subblock_comp/simp-find")
process_LME_output("../subblock_comp/find-rest")
"""

#process_LME_output("../subblock_indiv/fsiq-comp-simp")
#process_LME_output("../subblock_indiv/fsiq-math-rest")

makeROIsFromSeeds()


#process_LME_output("../addblock/con_0003")
#process_LME_output("../subblock/PPI_right_AI")
#process_LME_output("../subblock/con_0005")
