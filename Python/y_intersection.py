import numpy as np


def y_intersection(xx, yy, y_value=0):
	# Function to determine where a set of scattered data crosses a certain threshold
	# Returns an array of interpolated x-values such that y(x) = 0
	# xx is array of x data as float
	# yy is array of y data as float
	# y_value is the line of intersection, by default zero
	
	# Subtract the y value, so we are only looking for zero crossings
	yy = yy - y_value
	
	# Get the sign of y
	ss = np.sign(yy)

	# Take the difference of the signs
	dd = np.diff(ss) # Length is length of xx/yy/ss -1
	
	# Zero crossings will appear as pairs of values, one with positive y value and one with negative y value
	preCrossingIndices, = np.nonzero(dd) # Indices of the first elements
	postCrossingIndices = preCrossingIndices+1 # Indices of the second elements
	
	# Return nothing if no crossings are found
	if preCrossingIndices.size == 0:
		return
		
	# Use linear interpolation to find x such that y is 0 for each of our pairs
	x0 = xx[preCrossingIndices]
	y0 = yy[preCrossingIndices]
	x1 = xx[postCrossingIndices]
	y1 = yy[postCrossingIndices]
	#print('x0=%s, y0=%s, x1=%s, y1=%s' % (x0, y0, x1, y1))
	
	# Find the slope of the line between the two points (x0, y0) and (x1, y1)
	m = (y1 - y0) / (x1 - x0)
	
	# Use the equation y-y1 = m(m-x1) to find x when y=0, i.e.
	xCrossing = -y1 / m + x1
	
	return xCrossing