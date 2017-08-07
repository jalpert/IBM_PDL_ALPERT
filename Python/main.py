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

print "Working Directory: " + os.getcwd()
print "Timestamp: " + str(datetime.datetime.today())

'''def firstFrame(fileName):
	cap = cv2.VideoCapture(fileName)
	ret, image = cap.read()
	if not ret:
		print("Fatal Error Reading File: " + str(fileName))
		exit()
	cap.release()
	return image'''

def calculateCenter(LeftEdges, RightEdges):
        return numpy.array(zip(LeftEdges, RightEdges)).mean(1)
        

parser = argparse.ArgumentParser(description='Analyze the video and extract oscillation parameters')
parser.add_argument('file', action='store')
parser.add_argument('-fps', '--framerate', type=float)
#parser.add_argument('-b', '--bounds', nargs=4, type=int)
#parser.add_argument('-l', '--line', nargs=2, type=float)
parser.add_argument('-c', '--calibration', type=float, help='Length calibration (pixels/mm) of the video', default=0)
parser.add_argument('-f', '--frames', type=int)
parser.add_argument('-a', '--animate', type=int, default=0, nargs='?', const=1)
parser.add_argument('--mode', choices=['left', 'right', 'center'], default='center')
parser.add_argument('-w', '--filter_window', type=int, help='Size of the median filter. MUST BE ODD NUMBER!', default=35)
args = parser.parse_args()

# Filename minus extension
f = args.file[:args.file.find('.')]

# Get the bounds and inspection line and framerate
args.framerate, ailFrames = getRelevantFrames(args.file)
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
print('File: {}\nFramerate: {} fps\nLength Calibration: {} pixels/mm\nBounds: x1={}, x2={}, y1={}, y2={}\nInspection Line: y = {}*x + {}'.format(args.file, args.framerate, args.calibration, *(args.bounds + args.line)))

cv2.destroyAllWindows()
del ailFrames
del croppedFrames

frames = readFrames(args.file, bounds=args.bounds, fNums=args.frames)
LeftEdges, RightEdges, Intensities, Thresholds = analyze(frames, args.line, mode=args.mode, filter_window=args.filter_window)

# Enable Live Tracking
positions = calculateCenter(LeftEdges, RightEdges)
vizualize.liveTracking(frames, args.line, args.framerate, zip(LeftEdges, positions, RightEdges), args.calibration)

# Convert to actual positions
positions = positions / args.calibration
fNums = np.arange(len(positions)) # Array of frame numbers
tt = fNums.astype(float) / args.framerate # Array of frame times

cParams = extractParameters(tt, positions)
fig = vizualize.plotResults(tt, positions, cParams).savefig(f + '.png', bbox_inches='tight')
plt.show()

print("Csenter (T, w, TAU, A, p): " + str(cParams))

# Write the results to a text file
file = open(f + '.tsv', 'w')
file.write("Timestamp: " + str(datetime.datetime.today()) + '\n')
file.write(args.file + "\t" + str(args.framerate) + "\t" + str(len(fNums)) + '\n')
file.write("T\tw\tTAU\tA\tp\n")
file.write("%.3f\t%.3f\t%.3f\t%.3f\t%.3f\n" % cParams)
file.write("tt\tPosition\n")
for t,p in zip(tt, positions):
	file.write("%.3f\t%.3f\n" % (t,p))
file.close()
