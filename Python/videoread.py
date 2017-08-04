import cv2 
import time
import numpy
def readFrames(fileName, bounds=None, fNums=None):
	cap = cv2.VideoCapture(fileName)
	ret, image = cap.read()
	if not ret:
		print 'error reading file', fileName
		exit()
	
	# Read all the frames into a list
	time0 = time.clock()
	image = cropFrame(image, bounds) # Crop the image
	frames = [cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)] # Include the first frame that was just read (in grayscale)
	del image
	i = 0
	while i < fNums or fNums is None:
		ret, frame = cap.read()
		if not ret:
			cap.release()
			break
	
		# Convert to grayscale and crop
		frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
		frame = cropFrame(frame, bounds)
		frames.append(frame)
		i = i + 1
	m_time = time.clock() - time0
	print('Reading all ' + str(i) + ' frames took ' + str(m_time) + ' seconds. That is ' + str(i/m_time) + ' frames per second')
	return frames

# Returns a cropped version of the image
def cropFrame(frame, bounds, verbose=False):
	if bounds is None:
		return frame
		
	x1, x2, y1, y2 = bounds
	
	if verbose: print('x1=%d, y1=%d, x2=%d, y2=%d' % (x1, y1, x2, y2))
		
	return frame[y1:y2, x1:x2]
	
def cropAllFrames(frameList, bounds):
        cropped = []
	for i in range(len(frameList)):
		cropped.append(cropFrame(numpy.copy(frameList[i]), bounds))
	return cropped
