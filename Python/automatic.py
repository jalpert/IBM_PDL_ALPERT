
import cv2
import edgedetection
import numpy as np
import itertools
from matplotlib import pyplot as plt
import random

colors = [ (0, 0, 255), (0, 255, 0), (255, 0, 0), (100, 100, 0), (0, 100, 100), (100, 0, 100) ]
MAX_SIZE = 10**6 # 1 megabyte
def getRelevantFrames(filename):
        cap = cv2.VideoCapture(filename)
        # Get first 100 frames
        i = 0
        frames = []
        while(i < 100):
                ret, frame = cap.read()
                if not ret:
                        break
                # Resize Frame if too large
                if(frame.size > MAX_SIZE):
                        scaling = (MAX_SIZE / float(frame.size))**.5
                        frame = cv2.resize(frame, (0,0), fx=scaling, fy=scaling)
                else:
                        scaling = 1
                
                frames.append(frame)
                i = i + 1

        # Shuffle the order of the frames
        random.seed()
        random.shuffle(frames)

        # Get the framerate
        fps = cap.get(cv2.CAP_PROP_FPS)
        cap.release()
        
        return fps, frames, scaling

def fitLine(cnt1, cnt2):
	M = cv2.moments(cnt1)
	x1 = (M['m10']/M['m00'])
	y1 = (M['m01']/M['m00'])
	M = cv2.moments(cnt2)
	x2 = (M['m10']/M['m00'])
	y2 = (M['m01']/M['m00'])
	m = (y2-y1)/(x2-x1) # Slope
	b = y2-m*x2 # y-intercept
	return [m, b]

def extremePoints(cnt):
# Return the leftmost and rightmost x values for the contour
	leftmost = tuple(cnt[cnt[:,:,0].argmin()][0])[0]
	rightmost = tuple(cnt[cnt[:,:,0].argmax()][0])[0]
	return (leftmost, rightmost)

def leftmost(cnt):
	return tuple(cnt[cnt[:,:,0].argmin()][0])[0]
	
def rightmost(cnt):
	return tuple(cnt[cnt[:,:,0].argmax()][0])[0]

def grayscale(frames):
        gray = []
        for f in frames:
                gray.append(cv2.cvtColor(np.copy(f), cv2.COLOR_BGR2GRAY))
        return gray

def autoInspectionLine(f, pad=10):
	slopes = []
	y_ints = []
	left_bound = None
	right_bound = None
	frames = grayscale(f)
	for i in range(len(frames)-1):
                frame1 = frames[i]
                frame2 = frames[i+1]
                ret = compareFrames(frame1, frame2)
                if ret is None:
                        continue
                slopes.append(ret[0])
                y_ints.append(ret[1])
                if left_bound is None:
                        left_bound = ret[2]
                else:
                        left_bound = min(left_bound, ret[2])
                if right_bound is None:
                        right_bound = ret[3]
                else:
                        right_bound = max(right_bound, ret[3])
        print('Number of frames: ' + str(len(slopes)))

        m, b = (np.median(slopes), np.median(y_ints))
        vert_bounds = (int(m*left_bound+b), int(m*right_bound+b))
	bot_bound = min(vert_bounds) - pad
	top_bound = max(vert_bounds) + pad
        # Returns the fit line parameters and the bounds (line, bounds), ie ( (m, b), (x1, x2, y1, y2) )
	return [(m, top_bound-bot_bound-pad), (left_bound-pad/2, right_bound+pad/2, bot_bound, top_bound)]

def compareFrames(frame1, frame2):
        # Compare the two frames
        diff = cv2.absdiff(frame1, frame2)
        ret,thresh = cv2.threshold(diff,60,255,cv2.THRESH_TOZERO)

        # Get the contour representations of the difference
        _, cnts, _ = cv2.findContours(thresh, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

        # Find the two largest contours by area
        largest_contour_area = 0
        largest_contour_index = 0
        next_largest_area = 0
        next_largest_index = 1
        for j in range(2, len(cnts)):
                area = cv2.contourArea(cnts[j])
                # Check if this is smaller than the second largest contour area
                if area < next_largest_area:
                        continue
                # This contour is AT LEAST bigger than the second largest
                elif area < largest_contour_area:
                # This contour is the new next largest contour
                        next_largest_area = area
                        next_largest_index = j
                else:
                # This contour is the new largest contour
                        # Shift the biggest contour down to next biggest
                        next_largest_area = largest_contour_area
                        next_largest_index = largest_contour_index
                        # Make this contour the new biggest contour
                        largest_contour_area = area
                        largest_contour_index = j

        # If there are too few contours or they are just too small,  don't do anything
        if(next_largest_area < 1):
                pass
        else:
                # Save the fit from these two points to a big array
                cnts = [cnts[largest_contour_index], cnts[next_largest_index]]

                m, b = fitLine(*cnts)
                # Return the slope and y-intercept of this particular comparison, as well as the left and right bounds (m, b, left, right)
                return (m, b, min(leftmost(cnts[0]), leftmost(cnts[1])), max(rightmost(cnts[0]), rightmost(cnts[1])))

