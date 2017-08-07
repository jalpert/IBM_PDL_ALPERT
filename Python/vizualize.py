from matplotlib import pyplot as plt
import cv2
import numpy as np
import matplotlib.animation as animation
import itertools
import time
from oscillation_extraction import *
from edgedetection import *
	
def plotResults(tt, positions, cParams=None):
		fig, ax = plt.subplots()
		if cParams:
			(T, w, TAU, A, p) = cParams
			yy = A * np.sin(w * (tt - p)) * exp(-tt/TAU) + np.mean(positions)
			ax.plot(tt, yy, 'b-')
			AA = A * exp(-tt/TAU) + np.mean(positions)
			AAA = -A * exp(-tt/TAU) + np.mean(positions)
			ax.plot(tt, AA, 'g-', linewidth=3, linestyle='dashed')
			ax.plot(tt, AAA, 'g-', linewidth=3, linestyle='dashed')
		ax.plot(tt, positions, '.m-', markersize=4)
		plt.xlabel('Time (s)')
		plt.ylabel('Position along line of motion (mm)')
		return fig

# Edges is a list of edge positions. Each element in the list can either be a single value or a tuple of multiple values to plot
# i.e. Time 0: edges[0] ...
# Time 1: edges[1] ...
def liveTracking(frames, line, fps, edges, calibration=1):
    COLORS = [(255, 0, 0), (0, 255, 0), (0, 0, 255)]
    time = 0
    for f, e in zip(frames, edges):
        # f is a single grayscale frame
        # e is either a single value or a tuple of values
        time = time + 1/fps

        # convert frame to color
        f = cv2.cvtColor(f, cv2.COLOR_GRAY2BGR)

        if type(e) is not tuple:
            e = [e]
        
        # To allow multiple point plotting
        for x, c in zip(e, COLORS):
            y = int( line[0] * x + line[1])
            x = int(x)
            cv2.circle(f, (x, y), 3, c, -1)

        f = cv2.resize(f, (0, 0), fx=4, fy=4)
        
        text = "Time: {:3.1f}".format(time)
        if len(e) == 1:
            text = "{} Position: {:3.1f} mm".format(text, e[0]/calibration)
        else:
            text = "{} Positions:".format(text)
            for p in e:
                text = "{}  {:3.1f} mm".format(text, p/calibration)
                
        cv2.putText(f, text, (0, 0), cv2.FONT_HERSHEY_PLAIN, 1, (0, 0, 0), bottomLeftOrigin=True, thickness=2)
        f = cv2.flip(f, 0)
        cv2.imshow("Live Tracker. Press Y to continue to results", f)
        if cv2.waitKey(50) & 0xFF == ord('y'):
            break
    cv2.destroyAllWindows()
        

def animate(Intensities, EdgePositions, Thresholds, speed=1, window=None):
	length = len(Intensities)
	width = Intensities[0].size
	iterator = itertools.izip(Intensities, EdgePositions, Thresholds, range(length))
	
	zz = np.arange(width)
	
	fig, ax = plt.subplots()
	ax.set_ylim(np.min(Intensities), np.max(Intensities))
	ax.set_xlim(0, len(zz))
	
	intensity_line, = ax.plot([], [], 'm-')
	intensity_line.set_xdata(zz)
	intensity_line.set_ydata(Intensities[0])
	
	threshold_line, = ax.plot(zz, zz*0, '-y')
	edge_line, = ax.plot([], [], 'g.')
	ax.plot(zz, Intensities[0], 'k-', linewidth=3) # Plot the first frame's intensity in black
	
	frame_text = ax.text(.02, .8, "Frame: 1 of " + str(length), transform=ax.transAxes, verticalalignment='bottom', horizontalalignment='left')

	def update_plots(data):
		# Update the intensity line graph
		I, E, T, i = data
		intensity_line.set_ydata(I)
		
		# Draw the locations of the edges (IMPROVE THIS)
		ax.plot(E, T, 'o', color='b')
		threshold_line.set_ydata(np.ones_like(I) * T)
		text = "Frame: " + str(i+1) + " of " + str(length) + "\nSpeed: " + str(speed) + "x\nEdge Position: " + str(int(E)) + ", " + str(int(T))
		if window is not None:
			text = text + "\nFilter Window: " + str(window)
		frame_text.set_text(text)
	def next_frame():
		# Gets the next frame and yields the result of the analysis as a generator object
		for i in range(speed):
			data = iterator.next()
                        ax.plot(data[1], data[2], 'bo')
		yield data
	
	ani = animation.FuncAnimation(fig, update_plots, next_frame, interval=1, blit=False)
	try:
        	plt.show()
        except:
            print 'animation interrupted...continuing'
