#video quality measurer
#author : AKummur
#copyrights : Arris
######################

import sys, getopt
import os
import cv2
import numpy as np
from datetime import datetime
from skimage.measure import structural_similarity as ssim
#from math import ceil

startTime = datetime.now()
result = {}
#blackScreenCount = 0

def main(argv):
	inputfile = ''
	refFramesCount = 0
	passThreshold = 0.95
	withinThisY = 1000
	tsThreshold = 0.8
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
	
	print passThreshold, tsThreshold, withinThisY
	
	if cap.isOpened():
		while not foundFirstValidTimestamp:
			flag, frame = cap.read()
			if flag:
				#frame = frame.astype(np.uint8)
				currentFrameTimestamp = getTimestamp(frame, withinThisY, tsThreshold,  capWidth, capHeight)
				if  not len(currentFrameTimestamp) == 8:
					#might be black screen, check
					if compareBlack(frame):
						result[int(cap.get(1))] = 'blackScreen' #cap.get(1) gives the frame number
						print 'black check in', datetime.now() - startTime
					else:
						#no valid timestamp found
						result[int(cap.get(1))] = 'validTsNotFound' #valid timestamp not found
						print 'validTsNotFound', int(cap.get(1)), currentFrameTimestamp
				else:
				#timestamp found
					prevValidTimestamp = currentFrameTimestamp
					foundFirstValidTimestamp = True
					if (compare(frame, currentFrameTimestamp, refPath)) >= passThreshold:
						result[int(cap.get(1))] = 'PASS'
					else:
						result[int(cap.get(1))] = 'FAIL'
					print 'cts ', currentFrameTimestamp
					print 'done in ', datetime.now() - startTime
			else:
				print 'Error: unable to read ref frame for %s timestamp. moving on' % currentFrameTimestamp
			if cap.get(1) == cap.get(7):	#cap.get(cv2.CV_CAP_PROP_POS_FRAMES) == cap.get(cv2.CV_CAP_PROP_FRAME_COUNT):
				# If the number of captured frames is equal to the total number of frames,
				# we stop
				break			
	else:
		print 'Error: failed to open the video file'
		print 'Make sure you have all the decoders installed and try again'
		print 'exiting'
		sys.exit()
		
	while cap.isOpened():
		flag,frame = cap.read()
		if flag:
			#frame = frame.astype(np.uint8)
			currentFrameTimestamp = getTimestamp(frame, withinThisY, tsThreshold, capWidth, capHeight)
			if  not len(currentFrameTimestamp) == 8:
					#might be black screen, check
					if compareBlack(frame):
						result[int(cap.get(1))] = 'blackScreen' #cap.get(1) gives the frame number
						print 'black check in', datetime.now() - startTime
					else:
						#no valid timestamp found
						result[int(cap.get(1))] = 'validTsNotFound' #valid timestamp not found
						print 'validTsNotFound', int(cap.get(1)), currentFrameTimestamp
			else:
			#timestamp found
				if currentFrameTimestamp == prevValidTimestamp:
				#freeze
					result[int(cap.get(1))] = 'freeze'
				else:
					if (compare(frame, currentFrameTimestamp, refPath)) >= passThreshold:
						result[int(cap.get(1))] = 'PASS'
					else:
						result[int(cap.get(1))] = 'FAIL'
					prevValidTimestamp = currentFrameTimestamp
					print 'cts ', currentFrameTimestamp
					print 'done in ', datetime.now() - startTime
		else:
			print 'Error: unable to read ref frame for %s timestamp. moving on' % currentFrameTimestamp
		if cap.get(1) == cap.get(7):	#cap.get(cv2.CV_CAP_PROP_POS_FRAMES) == cap.get(cv2.CV_CAP_PROP_FRAME_COUNT):
			# If the number of captured frames is equal to the total number of frames,
			# we stop
			break
			
	cap.release()
	
	#results to a file
	log = open('log.txt', 'w')
	for k,v in result.iteritems():
		log.write('%-4s = %s\n'%(k, v))
	log.close()
	
	print 'Completed in ', datetime.now() - startTime
	print 'Check the results here', os.path.join(os.getcwd(), 'log.txt')
	
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
	return 0 #error reading the file

def compareBlack(img):
	path = os.path.join(os.getcwd(), 'blackScreen.png')
	img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
	refImg = cv2.imread(path)
	h, w = img.shape[:2]
	refImg = cv2.resize(refImg, (w, h))
	refImg = cv2.cvtColor(refImg, cv2.COLOR_BGR2GRAY)
	if int(ssim(img, refImg)) == 1:
		return True
	return False
'''
def getTimestampsDiffInFrames(tsa, tsb, fps): #timestampA, timestampB. Returns number of frames you need to go forward(+ve) or backward(-ve) to meet tsb from tsa 
	if not type(tsa) == str and not type(tsb) == str:
		print 'Error in getTimestampsDiffInFrames : expected string but given', type(tsa), ',', type(tsb)
		print 'exiting code'
		sys.exit()
	if not tsa.isdigit():
		print 'Error in getTimestampsDiffInFrames: timestamp contains characters other than digits 0-9'
		print 'here is the timestamp %s.'% tsa
		print 'exiting code'
		sys.exit()
	if not tsb.isdigit():
		print 'Error in getTimestampsDiffInFrames: timestamp contains characters other than digits 0-9'
		print 'here is the timestamp %s'% tsb
		print 'exiting code'
		sys.exit()
	if not len(tsa) == 8:
		print 'Error in getTimestampsDiffInFrames: invalid timestamp. Timestamp length is not equal to 8 digits'
		print 'here is the timestamp %s'% tsa
		print 'please check. exiting code'
		sys.exit()	
	if not len(tsb) == 8:
		print 'Error in getTimestampsDiffInFrames: invalid timestamp. Timestamp length is not equal to 8 digits'
		print 'here is the timestamp %s'% tsb
		print 'please check. exiting code'
		sys.exit()
	temp = [] #list to hold the 2 char strings of the timestamp
	for a in (tsa[i:i+2] for i in range(0, len(tsa), 2)):
		temp.append(a)
	ha,ma,sa,ca = temp #hrsA, minsA, secsA, countA
	del temp[:]
	for a in (tsb[i:i+2] for i in range(0, len(tsb), 2)):
		temp.append(a)
	hb,mb,sb,cb = temp #hrsB, minsB, secsB, countB
	return ((int(hb)-int(ha))*60*60*ceil(fps))+((int(mb)-int(ma))*60*ceil(fps))+((int(sb)-int(sa))*ceil(fps))+(int(cb)-int(ca))

def getNextExpectedTimestamp(timestamp):
	if not type(timestamp) == str:
		print 'Error in getNextExpectedTimestamp: expected string but given ', type(timestamp)
		print 'here is the timestamp ', timestamp
		print 'exiting code'
		sys.exit()
	if not timestamp.isdigit():
		print 'Error in getNextExpectedTimestamp: timestamp contains characters other than digits 0-9'
		print 'here is the timestamp ', timestamp
		print 'exiting code'
		sys.exit()
	if len(timestamp)>8:
		print 'Error in getNextExpectedTimestamp: invalid timestamp. Timestamp length is greater than 8 digits'
		print 'here is the timestamp ', timestamp
		print 'please check. exiting code'
		sys.exit()
	temp = [] #list to hold the 2 char strings of the timestamp
	for a in (timestamp[i:i+2] for i in range(0, len(timestamp), 2)):
		temp.append(a)
	h,m,s,c = temp #hrs, mins, secs, count
	c = int(c)+1
	if c == 30:
		c = 0
		s = int(s) + 1
		if s == 60:
			s = 0
			m = int(m) + 1
			if m == 60:
				m = 0
				h = int(h) + 1
	c = str(c)
	s = str(s)
	m = str(m)
	h = str(h)
	
	if len(c) == 1:
		c = '0'+ c
	if len(s) == 1:
		s = '0'+ s
	if len(m) == 1:
		m = '0'+ m
	if len(h) == 1:
		h = '0'+ h
	return h + m + s + c
'''
def keyExists(key, dict, width):
	for x in dict:
		if key in range(x-width, x+width):
			return x
	return False
'''	
def getTimestamp(img, withinThisY, threshold, width, height): #width,height to be resized
	matchDict = {0:[], 1:[], 2:[], 3:[], 4:[], 5:[], 6:[], 7:[], 8:[], 9:[]};  #dictionary to hold the matched coordinates for 0-9
	timestampDict = {} #dictionary to hold the matches in order 
	timestamp = ""
	img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
	img_gray = cv2.resize(img_gray, (width, height))
	for j in range(10):
		template = cv2.imread(os.path.join(os.getcwd(), 'templates', str(j)+'.png'),0)
		w, h = template.shape[::-1]
		res = cv2.matchTemplate(img_gray,template,cv2.TM_CCOEFF_NORMED)
		loc = np.where( res >= threshold)
		for pt in zip(*loc[::-1]):
			if(pt[1] <= withinThisY):
				pt = pt + (res[pt[1]][pt[0]],)
				matchDict[j].append(pt)

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
'''	
def getTimestamp(img, withinThisY, threshold, width, height): #width,height to be resized
	matchDict = {0:[], 1:[], 2:[], 3:[], 4:[], 5:[], 6:[], 7:[], 8:[], 9:[]};  #dictionary to hold the matched coordinates for 0-9
	timestampDict = {} #dictionary to hold the matches in order 
	timestamp = ""
	img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
	img_gray = cv2.resize(img_gray, (width, height))
	for file in os.listdir(os.path.join(os.getcwd(), 'templates')):
		template = cv2.imread(os.path.join(os.getcwd(), 'templates', file),0)
		w, h = template.shape[::-1]
		res = cv2.matchTemplate(img_gray,template,cv2.TM_CCOEFF_NORMED)
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