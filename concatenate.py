#concatenate.py

from subprocess import call
import glob

def merge(imgs, name):
	"""
	imgs - list of images in the order you want them merged in
	name - output (merged) image name
	"""
	#file_list = " ".join(imgs)
	command = ['fslmerge', '-t', name] + imgs
	call(command)

	return "%s" % name


def split(img):
	"""
	img - image to split
	"""

	command = ['fslsplit', img, "split_%s" % img, '-t'] 
	call(command)
	
	files = glob.glob("*split_%s*" % img)
	
	return files


def concatenate(img, timepoints):
	"""
	img - image to split
	timepoints - list of [start, end] indexes to split at - eg. [start:end]
	"""
	imgs = split(img)

	c = 1
	chunks = []
	
	#make the chunks
	imgs.sort()

	for timepoint in timepoints:
		start = timepoint[0]
		end = timepoint[1]
		chunk = imgs[start:end]
		name = "%s_chunk_%i" % (img, c)
		merge(chunk, name)
		chunks.append(name)
		c += 1	

	merged_img = merge(chunks, '%s_merged' % img)

	return merged_img


