#video quality measurer
#author : AKummur
#copyrights : Arris
######################

import sys, getopt
import os
import cv2
import numpy as np
from datetime import datetime
from skimage.measure import compare_ssim as ssim
import threading
from memory_profiler import profile

startTime = datetime.now()
result = {}
passThreshold = 0.95
withinThisY = 1000
tsThreshold = 0.8
capHeight = 0
capWidth = 0

def main(argv):
	inputfile = ''
	refFramesCount = 0
	global passThreshold
	global withinThisY
	global tsThreshold
	global capWidth
	global capHeight
	try:
		opts, args = getopt.getopt(argv,"hi:f:p:m:y:",["ivid=","framespath=", "passthreshold=", "templatematchthreshold=", "withinThisY="])
	except getopt.GetoptError:
		print 'correctUsage : videoQualityMeasurer.py -i <testVideo> -f <referenceFramesPath> -p <passThreshold(optional, default=0.95) -m <templateMatchThreshold(optional, default=0.8)> -y <maxYCoordinateForTimestamp(optional, default=1000)>'
		sys.exit(2)
	if len(opts) < 2:
		print 'Some args are missing'
		print 'correctUsage : videoQualityMeasurer.py -i <testVideo> -f <referenceFramesPath> -p <threshold(optional, default=0.95)> -m <templateMatchThreshold(optional, default=0.8)> -y <maxYCoordinateForTimestamp(optional, default=1000)>'
		sys.exit()
	for opt, arg in opts:
		if opt == '-h':
			print 'videoQualityMeasurer.py -i <testVideo> -f <referenceFramesPath> -p <threshold(optional, default=0.95)> -m <templateMatchThreshold(optional, default=0.8)> -y <maxYCoordinateForTimestamp(optional, default=1000)>'
			sys.exit()
		elif opt in ("-i", "--ivid"):
			inputfile = arg
		elif opt in ("-f", "--framespath"):
			refPath = arg
		elif opt in ("-p", "--passthreshold"):
			try:
				passThreshold = float(arg)
			except:
				print 'InputError : threshold value must be float and less than or equal to 1'
				print 'Check your threshold input'
				sys.exit(0)
		elif opt in ("-m", "--templatematchthreshold"):
			try:
				tsThreshold = float(arg)
			except:
				print 'InputError : threshold value must be float and less than or equal to 1'
				print 'Check your threshold input'
				sys.exit(0)
		elif opt in ("-y", "--withinThisY"):
			withinThisY = int(arg)
			
	if not passThreshold <= 1:
		print 'InputError : threshold value must be float and less than or equal to 1'
		sys.exit(0)
		
	if not tsThreshold <= 1:
		print 'InputError : threshold value must be float and less than or equal to 1'
		sys.exit(0)
	
	if (not type(withinThisY) == int) or (withinThisY < 0):
		print 'InputError : withinThisY value should be an integer and greater than 1'
		sys.exit(0)
		
	if not os.path.isfile(inputfile):
		print 'unable to find the input file'
		print 'try the absolute path to the file'
		sys.exit()
	
	if not os.path.exists(refPath):
		print 'unable to find the specified reference file'
		print 'try the absolute path to the file'
		sys.exit()
	
	try:
		cap = cv2.VideoCapture(inputfile) #captured video
	except:
		print 'problem opening input streams'
		sys.exit()
		
	if not cap.isOpened():
		print 'Error: failed to open the video file'
		sys.exit()
	
	prevValidTimestamp = ''
	foundFirstValidTimestamp = False
	capWidth = int(cap.get(3)) # width of captured video
	capHeight = int(cap.get(4)) # height of captured video
	totalFrames = int(cap.get(7))
	framesPerThread = int(totalFrames/4) # we are gonna use only 10 threads. this is to make the code work across all machines(low capability machines)
	
	print passThreshold, tsThreshold, withinThisY
		
	threads = []
	for i in xrange(0, totalFrames, framesPerThread):
		t = threading.Thread(target=readNFrames, args=(i, i+framesPerThread, inputfile, refPath))
		threads.append(t)
		
	for t in threads:
		t.start()

	for t in threads:
		t.join()

	cap.release()
	
	#results to a file
	log = open('log.txt', 'w')
	for k,v in result.iteritems():
		log.write('%-4s = %s\n'%(k, v))
	log.close()
	
	print 'Completed in ', datetime.now() - startTime
	print 'Check the results here', os.path.join(os.getcwd(), 'log.txt')

def readNFrames(a, n, input, refPath):
	global result
	try:
		vidFile = cv2.VideoCapture(input)
	except:
		print "problem opening input stream"
		sys.exit(1)
	if not vidFile.isOpened():
		print "capture stream not open"
		sys.exit(1)
		
	vidFile.set(1, a)
	ret, frame = vidFile.read() # read first frame, and the return code of the function.
	while ret:  # note that we don't have to use frame number here, we could read from a live written file.
		#print '%-6s %s'%(vidFile.get(1), getTimestamp(frame, 50, 0.8))
		print vidFile.get(1)
		cts = getTimestamp(frame, withinThisY, tsThreshold, capWidth, capHeight)
		if len(cts) == 8:
			result[int(vidFile.get(1))] = (compare(frame, cts, refPath), cts)
		else:
			result[int(vidFile.get(1))] = (compareBlack(frame), 'validTsNotFound')
		if(int(vidFile.get(1)) == n):
			break
		#log.write('%-4s = %s\n'%(int(vidFile.get(1)), getTimestamp(frame, 100, 0.8)))
		#cv2.imwrite(os.path.join(framesPath, getTimestamp(frame, 100, 0.8)+'.png'), frame)
		ret, frame = vidFile.read() # read next frame, get next return code
		

def compare(img, ts, refPath):
	#print 'ref', refPath, os.path.join(refPath, ts+'.png')
	img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
	h, w = img.shape[:2]
	refImg = cv2.imread(os.path.join(refPath, ts + '.png'), 0)
	if refImg is not None:	
		#h1, w1 = refImg.shape[:2]
		refImg = cv2.resize(refImg, (w, h))
		#refImg = cv2.cvtColor(refImg, cv2.COLOR_BGR2GRAY)
		return ssim(img, refImg)
        #return (ssim(img[0:h/2, 0:w], refImg[0:h/2, 0:w])+ssim(img[h/2+1:h, h/2+1:w], refImg[h/2+1:h, h/2+1:w]))/2
	return 0 #unable to read refImg 

def compareBlack(img):
	path = os.path.join(os.getcwd(), 'blackScreen.png')
	img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
	refImg = cv2.imread(path)
	h, w = img.shape[:2]
	if refImg is not None:
		refImg = cv2.resize(refImg, (w, h))
		refImg = cv2.cvtColor(refImg, cv2.COLOR_BGR2GRAY)
		if int(ssim(img, refImg)) == 1:
			return True
	return False

def keyExists(key, dict, width):
	for x in dict:
		if key in range(x-width, x+width):
			return x
	return False

def getTimestamp(img, withinThisY, threshold, width, height): #width,height to be resized
	matchDict = {0:[], 1:[], 2:[], 3:[], 4:[], 5:[], 6:[], 7:[], 8:[], 9:[]};  #dictionary to hold the matched coordinates for 0-9
	timestampDict = {} #dictionary to hold the matches in order 
	timestamp = ""
	img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
	img_gray = cv2.resize(img_gray, (width, height))
	for file in os.listdir(os.path.join(os.getcwd(), 'templates')):
		template = cv2.imread(os.path.join(os.getcwd(), 'templates', file),0)
		w, h = template.shape[::-1]
		res = cv2.matchTemplate(img_gray, template, cv2.TM_CCOEFF_NORMED)
		loc = np.where( res >= threshold)
		for pt in zip(*loc[::-1]):
			if(pt[1] <= withinThisY):
				pt = pt + (res[pt[1]][pt[0]],)
				matchDict[int(file[0])].append(pt)
		
	for k,v in matchDict.iteritems():
		for i in v:
			key = keyExists(i[0], timestampDict, int(w/2))
			if key:
				if i[2] > timestampDict[key][1]:
					timestampDict[key] = (k, i[2])
			else:
				timestampDict[i[0]] = (k, i[2])
	for r in sorted(timestampDict):
		timestamp += str(timestampDict[r][0])
	return timestamp
		
if __name__ == "__main__":
   main(sys.argv[1:])