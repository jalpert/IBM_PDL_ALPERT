from matplotlib import pyplot as plt
import cv2
import numpy as np
from scipy import signal
import time

from y_intersection import *

# TODO: average the data from all the frames in the video to get a better function for background noise
def cleanIntensity(zz, I_0, filter_window, p, plot=False):
	# Clean the data using a median filter, and convert back to integers
	I = signal.medfilt(I_0, filter_window).astype(int)
	
	# Subtract a small parabola to reduce the intensity at the edges
	w = zz.size
	x = np.array([0, w, w/2])
	y = np.array([0, 0, max(I)*p/20])
	yy = np.polyval(np.polyfit(x, y, 2), zz)
	I = I + yy
	
	# Plot the different Intensities, if applicable
	if plot:
		I_1 = signal.medfilt(I_0, filter_window+10).astype(int)
		I_2 = signal.medfilt(I, filter_window-10).astype(int)
		fig, ax = plt.subplots()
		l1, l2, l3, l4 = ax.plot(zz, I_0, 'b.', zz, I, 'r-', zz, I_1, 'y-', zz, I_2, 'm-')
		ax.legend( (l1, l2, l3, l4), ('Raw Data', 'Median Filter Standard', 'Filter Window + 10', 'Filter Window x2'))
		plt.show()
	return I
	
# Takes grayscale frame and gets the image intensity along the line
def imageIntensity(image, line, filter_window, parabola):
	height, width = image.shape

	# TODO if |m|>1, transpose the image
	m = line[0] # slope
	b = line[1] # y-intercept 
	
	zz = np.arange(width) # really just an indexing array
	yy = (m * zz + b).astype(int)
	bounded_indices = np.where(np.logical_and(yy > 0, yy < height-1))
	zz = zz[bounded_indices]
	yy = yy[bounded_indices]
	
	# Get image intensity along the fit line, averaging with points above and below line
	I = image[yy, zz]
	'''for x in zz:
		y = yy[x]
		span = image[y-thickness/2:y+1+thickness/2, x]
		i = np.mean(span) # Mean intensity at point x along the axis of motion
		print(y, i)
		I.append(i)'''
	
	return (zz, cleanIntensity(zz, I, filter_window, parabola))


def threshold(I):
	return np.average([np.min(I), max(I)], weights = [.5, .5])
	
def analyze(frames, line, filter_window=35, parabola=1):
	# Analyze all the frames in the video
	# List of intensity graphs for each frame. Each element is the intensity values
	# for the frame along the x values of the inspection line. So the first frame's intensity is
	# Intensities[0] and the first frame's intensity at 300 pixels is Intensities[0][300]
	time0 = time.clock()
	Intensities = [] 
	LeftEdges = []
	RightEdges = []
	Thresholds = []
	Backgrounds = []
	for frame in frames:
		# The cleaned image intensity along the inspection line, with the indexing array zz st I[0] is the leftmost value
		zz, I = imageIntensity(frame, line, filter_window, parabola)
		T = threshold(I)
		edges_z = y_intersection(zz, I, y_value=T)
		Thresholds.append(T)
		Intensities.append(I)
		# Note, the intensity at the edge position can be derived from interpolation
		
		LeftEdges.append(edges_z[0])
                RightEdges.append(edges_z[1])
			
	m_time = time.clock() - time0
	print('Processing all ' + str(len(frames)) + ' frames took ' + str(m_time) + ' seconds. That is ' + str(len(frames)/m_time) + ' frames per second')
	return (LeftEdges, RightEdges, Intensities, Thresholds)
