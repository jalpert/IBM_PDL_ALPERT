from scipy.signal import *
from matplotlib import pyplot as plt
from numpy import *
from y_intersection import *

# Returns the points in xx, yy closest to each x value in targetsx
def nearestPoints(targetxs, xx, yy):
	i = []
	for x in targetxs:
		d = abs(xx-x) # Absolute distance between each point and x
		i.append(argmin(d))
	return (xx[i], array([yy[a] for a in i]))
	

def extractParameters(tt, yy, plot=False):
	# Function to extract the fit parameters of a damped oscillation
	# Fit to y = A*sin(w*t+p)*e^(t/T) + y0
	# tt time series data
	# yy position data
	
	# Get the first derivative of the data using a Savitzky-Golay filter
	dydt = savgol_filter(yy, 5, 2, deriv=1)
	# Get the times of all of the zero crossings for the derivative of the data
	zero_crossings = y_intersection(tt, dydt)

	# Extract the period T and the angular frequency w
	T = 2 * np.mean(np.diff(zero_crossings))
	w  = 2*pi/T
	#print('T=' + str(T) + ' w=' + str(w))
	
	# Extract the damping constant TAU
	# Get only the peaks of the signal
	ptt, pyy = nearestPoints(zero_crossings, tt, yy)
	yeven = pyy[0::2] # Get even indexed peaks
	yodd = pyy[1::2] # Get odd indexed peaks
	length = min(yeven.size, yodd.size)
	yeven = yeven[0:length]
	yodd = yodd[0:length]
	
	Amp = (yeven-yodd) / 2 # Array of amplitude values over time
	Att = linspace(0, max(tt), len(Amp))
	
	try:
		# Fit the linear equation ln(y) = ln(A) - t/T
		lAmp = log(abs(Amp))
		poly = polyfit(Att, lAmp, 1) # p[0] = -1/T, p[1] = ln(A)
		TAU = -1/poly[0]
		A = sign(median(Amp))*exp(poly[1])
		p = y_intersection(tt, yy, np.mean(yy))[0] # The phase
		return (T, w, TAU, A, p)
	except:
		print 'error fitting curve'
		return None
	
	'''if plot:
		# Check my work
		D = A * exp(-tt/TAU)
		# Plot everything
		plt.plot(tt, yy, 'ro', label='raw data')
		plt.plot(tt, dydt, 'b^-', label='first derivative')
		plt.plot(zero_crossings, np.zeros_like(zero_crossings), 'bo', label='zero crossings')
		plt.plot(ptt, pyy, 'go', label='peaks')
		plt.plot(tt, D, 'g-', label='damping curve')
		plt.legend()
		plt.show()'''
