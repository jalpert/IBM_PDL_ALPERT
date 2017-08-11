from manual import *
from oscillation_extraction import *
from edgedetection import *
from automatic import *
import vizualize
import argparse
from videoread import *
import datetime
import os
import cv2
import numpy
import tkFileDialog
import Tkinter as tk

print "Working Directory: " + os.getcwd()
print "Timestamp: " + str(datetime.datetime.today())

parser = argparse.ArgumentParser(description='Analyze the video and extract oscillation parameters')
parser.add_argument('file', action='store', nargs='?')
parser.add_argument('-fps', '--framerate', type=float)
parser.add_argument('-c', '--calibration', type=float, help='Length calibration (pixels/mm) of the video', default=0)
parser.add_argument('-f', '--frames', type=int)
parser.add_argument('-w', '--filter_window', type=int, help='Size of the median filter. MUST BE ODD NUMBER!', default=35)
parser.add_argument('-p', '--parabola', type=float, help='Intensity of the upside down parabola added to the image intensity to emphasize values toward the center. Helps eliminate outliers. Integer from 1 to 10, 1 being the smallest and 10 being the largest', default=1)
args = parser.parse_args()

# If no file is given, prompt the user for one
if(args.file is None):
        #tk.Tk().withdraw()
        args.file = tkFileDialog.askopenfilename(initialdir = os.getcwd(), title="Select a video to analyze")

# Filename minus extension
f = args.file[:args.file.find('.')]

# Get the bounds and inspection line and framerate
args.framerate, ailFrames, scaling = getRelevantFrames(args.file)
args.line, args.bounds = autoInspectionLine(ailFrames)
croppedFrames = cropAllFrames(grayscale(ailFrames), args.bounds)

# Allow the user to modify the bounds and inspection line
done = False
while not done:
        left  = (0, int(args.line[1]))
        width = args.bounds[1]-args.bounds[0]
        right = (width, int(args.line[0] * width + args.line[1]))
        for frame in croppedFrames:
                cv2.line(frame, left, right, (255, 0, 255))
                frame = cv2.resize(frame, (0, 0), fx = 4, fy = 4)
                cv2.imshow('Inspection Line and Bounds Preview. Press Y to continue or N to adjust manually.', frame)
                key = cv2.waitKey(200) & 0xFF
                if key == ord('Y') or key == ord('y'):
                        done = True
                        break
                elif key == ord('N') or key == ord('n'):
                        # Launch manual adustment mode
                        cv2.destroyAllWindows()
                        args.bounds = getCropBounds(ailFrames, args.bounds)
                        croppedFrames = cropAllFrames(ailFrames, args.bounds)
                        args.line = getInspectionLine(croppedFrames[0])
                        break

# Get pixel/mm conversion factor
if args.calibration == 0:
        args.calibration = getLengthCalibration(ailFrames[0])

# Print out information gathered so far
status = 'File\t{}\nFramerate\t{} fps\nLength Calibration\t{} pixels/mm\nScaling Factor\t{}\nBounds\tx1={}, x2={}, y1={}, y2={}\nInspection Line\ty = {}*x + {}'.format(args.file, args.framerate, args.calibration, scaling, *(args.bounds + args.line))
print(status)

cv2.destroyAllWindows()
del ailFrames
del croppedFrames

frames = readFrames(args.file, scaling, bounds=args.bounds, fNums=args.frames)
LeftEdges, RightEdges, Intensities, Thresholds = analyze(frames, args.line, filter_window=args.filter_window, parabola=args.parabola)

# Enable Live Tracking
positions = numpy.array(zip(LeftEdges, RightEdges)).mean(1)
vizualize.animate(Intensities, positions, Thresholds, speed=3)
vizualize.liveTracking(frames, args.line, args.framerate, zip(LeftEdges, positions, RightEdges), args.calibration)

# Convert to actual positions
positions = positions / args.calibration
fNums = np.arange(len(frames)) # Array of frame numbers
tt = fNums.astype(float) / args.framerate # Array of frame times

cParams = extractParameters(tt, positions)
fig = vizualize.plotResults(tt, positions, cParams).savefig(f + '.png', bbox_inches='tight')
plt.show()

print("Fit Parameters (T, w, TAU, A, p): " + str(cParams))

# Write the results to a text file
file = open(f + '.tsv', 'w')
file.write("Timestamp\t{}\n".format(str(datetime.datetime.today())))
file.write(status + '\n')
file.write("T\tw\tTAU\tA\tp\n")
file.write("%.3f\t%.3f\t%.3f\t%.3f\t%.3f\n" % cParams)
file.write("Time\tLeft\tCenter\tRight\n")
for t, l, c, r in zip(tt, LeftEdges, positions, RightEdges):
	file.write("%.3f\t%.3f\t%.3f\t%.3f\n" % (t, l, c, r))
file.close()
