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

def firstFrame(fileName):
	cap = cv2.VideoCapture(fileName)
	ret, image = cap.read()
	if not ret:
		print("Fatal Error Reading File: " + str(fileName))
		exit()
	cap.release()
	return image

parser = argparse.ArgumentParser(description='Analyze the video and extract oscillation parameters')
parser.add_argument('file', action='store')
parser.add_argument('framerate', action='store', type=float)
#parser.add_argument('-b', '--bounds', nargs=4, type=int)
#parser.add_argument('-l', '--line', nargs=2, type=float)
parser.add_argument('-f', '--frames', type=int)
parser.add_argument('-m', '--manual', action='store_true', help='Manually pick bounds and line using graphical user interface')
parser.add_argument('-a', '--animate', type=int, default=0, nargs='?', const=1)
parser.add_argument('--mode', choices=['left', 'right', 'center'], default='center')
parser.add_argument('-w', '--filter_window', type=int, help='Size of the median filter. MUST BE ODD NUMBER!', default=35)
args = parser.parse_args()

# Filename minus extension
f = args.file[:args.file.find('.')]

# Get the framerate

# Get the bounds and inspection line
ailFrames = getRelevantFrames(args.file, args.frames)
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
                
cv2.destroyAllWindows()
del ailFrames
del croppedFrames

frames = readFrames(args.file, bounds=args.bounds, fNums=args.frames)
Intensities, EdgePositions, Thresholds = analyze(frames, args.line, mode=args.mode, filter_window=args.filter_window)

if args.animate:
	vizualize.animate(Intensities, EdgePositions, Thresholds, speed=args.animate, window=args.filter_window)

fNums = np.arange(len(Intensities)) # Array of frame numbers
tt = fNums.astype(float) / args.framerate # Array of frame times

cParams = extractParameters(tt, EdgePositions)
fig = vizualize.plotResults(tt, EdgePositions, cParams).savefig(f + '.png', bbox_inches='tight')
if args.animate:
        plt.show()
print("Csenter (T, w, TAU, A, p): " + str(cParams))

# Write the results to a text file
file = open(f + '.tsv', 'w')
file.write("Timestamp: " + str(datetime.datetime.today()) + '\n')
file.write(args.file + "\t" + str(args.framerate) + "\t" + str(len(fNums)) + '\n')
file.write("T\tw\tTAU\tA\tp\n")
file.write("%.3f\t%.3f\t%.3f\t%.3f\t%.3f\n" % cParams)
file.write("tt\tPosition\n")
for t,p in zip(tt, EdgePositions):
	file.write("%.3f\t%.3f\n" % (t,p))
file.close()
