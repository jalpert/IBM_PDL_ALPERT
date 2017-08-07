import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib import pyplot as plt
import matplotlib.patches as patches
import cv2
import videoread
import Tkinter as tk
from scipy.spatial import distance

# Disable keymaps (keyboard shortcuts) for plot windows
keymaps = ['keymap.all_axes', 'keymap.back', 'keymap.forward', 'keymap.fullscreen', 'keymap.grid', 'keymap.home', 'keymap.pan', 'keymap.quit', 'keymap.save', 'keymap.xscale', 'keymap.yscale', 'keymap.zoom']
for k in keymaps:
	plt.rcParams[k] = ''

# TODO make cursor crosshair (lines that go all the way across the image) during selection
def getInspectionLine(frame, fig=None, verbose=False):
	if fig is None:
		fig = plt.figure(figsize=(12, 8), tight_layout=True)
		plt.imshow(frame)
		plt.xticks([]), plt.yticks([])  # to hide tick values on X and Y axis

	while True:
		plt.title('Pick two points for the inspection line. Double click to remove a point.')
		pts = np.array(plt.ginput(2))
		plt.title('Click anywhere to continue. Press any keyboard button to start again')
		
		# Display the inspection line on the image
		fit = np.polyfit(pts[:,0], pts[:,1], 1)
		x = np.arange(frame.shape[1]) # Array of x values from zero to frame width
		y = np.polyval(fit, x) # Y values for the inspection line on the frame
		bounded_indices = np.where(np.logical_and(y >= 0, y < frame.shape[0]-1))
		x = x[bounded_indices] # Don't go beyond the bounds of the frame
		y = y[bounded_indices]
		plt.plot(x, y)
		
		if not plt.waitforbuttonpress(): # Close on click, loop on button press
			if verbose:
				print('Fit line coefficients in form [m b] is %d' % str(fit))
			plt.close()
			return (fit[0], fit[1])
		
def getCropBounds(frames, bounds):
        RED = (30, 60, 255)
        BLUE = (255, 150, 0)
        GREEN = (0, 230, 0)
        PURPLE = (255, 30, 180)
        SPACE = 32
        ENTER = 10
        
        height, width, _ = frames[0].shape
        x1, x2, y1, y2 = bounds
        del bounds

        i = 0
        line = 0
        while True:
                frame = np.copy(frames[i])
                
                left = ( (x1, 0), (x1, height) )
                cv2.line(frame, (x1, 0), (x1, height), PURPLE if line is 0 else BLUE)
                right = ( (x2, 0), (x2, height) )
                cv2.line(frame, (x2, 0), (x2, height), PURPLE if line is 1 else BLUE)
                top = ( (0, y1), (width, y1) )
                cv2.line(frame, (0, y1), (width, y1), PURPLE if line is 2 else BLUE)
                bottom = ( (0, y2), (width, y2) )
                cv2.line(frame, (0, y2), (width, y2), PURPLE if line is 3 else BLUE)

                cv2.imshow('Crop Bounds Preview. Use AWSD and SPACE to adjust bounds. Press ENTER when finished', frame)
                key = cv2.waitKey(0) & 0xFF
                if key == ord('a'):#move left
                        if line == 0:
                                x1 = x1 - 1
                        elif line == 1:
                                x2 = x2 - 1
                elif key == ord('d'):#move right
                        if line == 0:
                                x1 = x1 + 1
                        elif line == 1:
                                x2 = x2 + 1
                elif key == ord('w'):#move up
                        if line == 2:
                                y1 = y1 - 1
                        elif line == 3:
                                y2 = y2 - 1
                elif key == ord('s'):#move down
                        if line == 2:
                                y1 = y1 + 1
                        elif line == 3:
                                y2 = y2 + 1
                elif key == SPACE:#toggle line
                        line = (line + 1) & 3
                elif key == ENTER:#exit
                        break

        return x1, x2, y1, y2

# Prompts the user for a conversion factor between pixels and mm
def getLengthCalibration(frame):
        fig = plt.figure(figsize=(12, 8), tight_layout=True)
        plt.imshow(frame)
        plt.xticks([]), plt.yticks([])  # to hide tick values on X and Y axis

        plt.title('Pick two points to calibrate length. Double click to remove a point.')
        length = distance.euclidean(*plt.ginput(2))
	# Display the dialog box
	master = tk.Tk()
	tk.Label(master, text="Conversion").grid(row=0, column=0)
	entry = tk.Entry(master)
	entry.grid(row=0, column=1)
	tk.Label(master, text="mm").grid(row=0, column=2)
	tk.Button(master, text="Done", command=master.quit).grid(row=1, column=0, sticky=tk.W, pady=4)
	tk.mainloop()
	
	plt.close('all')

        ret = length / float(entry.get())
        master.destroy()
        return ret
