#Resize and template match
#Author : Rateesh Manoharan
####################################

import numpy as np
import cv2
import imutils #For resizing the template
import math
import argparse
import os
import time
import sys

#Global variables initialization
blackScreenThreshold = 0.25
matchFrameThreshold = 0.9
foundCount = 0
blackCount = 0
notFoundCount = 0
matchTemplateShape = ()
meanDistThreshold = 50
totalFrames = 0
shape = (1280, 720)
video = []
maxBnf = 15
minBnf = 10
maxFf = 250
minFf = 230
blackOrNotFoundFramesRange = (0,0)
foundFramesRange = (0,0)

def main():
    """Main Function"""
    global blackScreenThreshold
    global matchFrameThreshold
    global foundCount
    global blackCount
    global notFoundCount
    global matchTemplateShape
    global video
    global maxBnf
    global minBnf
    global maxFf
    global minFf
    global totalFrames
    
    start_time = time.time()

    
    #Get the input values for captured video and channel icon template
    ap = argparse.ArgumentParser()
    ap.add_argument("-i", "--inputVideo", required = True, help = "Absolute path of the video to be verified")
    ap.add_argument("-t", "--template", required = True, help = "Absolute path of the template to be matched")
    ap.add_argument("-p", "--folderPath", required = True, help = "Folder to be used for copying the result file and video")
    #Get the optional input variables
    ap.add_argument("-bt", "--blackFrameThreshold", help = "Correlation value upto which the frame will be identified as black screen", default = 0.25)
    ap.add_argument("-mt", "--matchFrameThreshold", help = "Minimum Correlation value required to be considered as channel icon found", default = 0.9)
    ap.add_argument("-bnfr", "--blackOrNotFoundFramesRange", help = "Range of black frames or notFound frames that can be present in each cycle. Eg: (10,15)", type = str, default = (10,15))
    ap.add_argument("-fr", "--foundFramesRange", help = "Range of found frames that can be present in each cycle. Eg. (230,250)", type = str , default = (230,250))
    
    args = vars(ap.parse_args()) # Creates a dictionary with labels as keys and input values as values
    
    #Assign variables for the input values
    capture = str(args["inputVideo"])
    templateFile = str(args["template"])
    currentWorkingDir = str(args["folderPath"])
    blackFrameThreshold = (args["blackFrameThreshold"])
    matchFrameThreshold = (args["matchFrameThreshold"])
    blackOrNotFoundFramesRange = (args["blackOrNotFoundFramesRange"])
    foundFramesRange = (args["foundFramesRange"])
    
    
    """ #sample input 
    capture = "C:\\Template\\capturedTestVideo.avi"
    templateFile = "C:\\automoto\\config\\data\\eos\\EOS-Sanity-Tune-005\\ui2025\\iconFromFrame.png"
    currentWorkingDir = "D:\\"
    """
    
    print "\n Initial Values: ", "\n Input Video: ", capture, "\n Channel Icon Template: ", templateFile, "\n Folder Path: ", currentWorkingDir, "\n Black Frame Threshold: ", \
          blackFrameThreshold, "\n Match Frame Threshold: ", matchFrameThreshold, "\n Black or Not Found Frames Range: ", blackOrNotFoundFramesRange, "\n Found frames Range: ", \
          foundFramesRange, "\n"
    
    #Set the working directory to session folder
    os.chdir(currentWorkingDir)
    
    #Make sure that the input files exist
    if not os.path.isfile(capture):
        print 'unable to find the capture video file'
        print 'try the absolute path to the file'
        sys.exit()

    if not os.path.isfile(templateFile):
        print 'unable to find the channel icon template'
        print 'try the absolute path to the file'
        sys.exit()        

    #Extract min and max number of black/notFound/found frames
    try:
        blackOrNotFoundFramesRange = blackOrNotFoundFramesRange.replace("(","").replace(")","").split(',')
        minBnf,maxBnf  = blackOrNotFoundFramesRange
        minBnf = int(minBnf)
        maxBnf = int(maxBnf)
    except:
        print 'Issue with the input value for blackOrNotFoundFramesRange i.e -bnfr'
        print 'Enter value in correct format. Eg: (10,15)'
        sys.exit()           
    
    try:
        foundFramesRange = foundFramesRange.replace("(","").replace(")","").split(',')
        minFf, maxFf = foundFramesRange
        minFf = int(minFf)
        maxFf = int(maxFf)
    except:
        print 'Issue with the input value for foundFramesRange i.e -fr'
        print 'Enter value in correct format. Eg: (230,250)'
        sys.exit()       
           
    #Read captured video and template using openCV
    try:
        capture = cv2.VideoCapture(capture) #captured video
    except:
        print 'problem opening captured video'
        sys.exit()
        
    if not capture.isOpened():
        print 'Error: failed to open the video file'
        sys.exit()
        
    try:
        template = cv2.imread(templateFile,1) #Channel Icon Template
    except:
        print 'problem opening the channel icon template'
        sys.exit()
        
    print "\n After updates:", "\n Input Video: ", capture, "\n Channel Icon Template: ", templateFile, "\n Folder Path: ", currentWorkingDir, "\n Black Frame Threshold: ", \
          blackFrameThreshold, "\n Match Frame Threshold: ", matchFrameThreshold, "\n Black or Not Found Frames Range: ", (minBnf, maxBnf), "\n Found frames Range: ", \
          (minFf, maxFf), "\n"
          
    totalFrames = int(capture.get(7)) # Get the number of frames in captured video
    
    #Initialize variables
    w = 0
    h = 0
    
    foundArray = []
    locArray = []
    diffArray = []    
    prevFrameString = ""
    rPrev = ""     
        
    #Initiate Video Writer  
    fourcc = cv2.VideoWriter_fourcc(*'MSVC') #Set fourcc i.e video compressor as Microsoft Video 1
    video = cv2.VideoWriter('graphicsVerificationVideo.avi',fourcc, 50, shape, 1)
    
    #Open the file to store the result
    f = open("result.txt", 'w')   
    
    #totalFrames = 100
    lastFrameIndex = totalFrames-1    
    
    
    for i in range(totalFrames):        
        currentFrameResult = range(4)        
        #capture.set(cv2.CAP_PROP_POS_FRAMES, i) #To set the position of captured video to a specified frame        
        ret, frame = capture.read()        
        #frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) #Convert the color space to gray                
        matchResult = cv2.matchTemplate(frame,template,cv2.TM_CCORR_NORMED) #Template match
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(matchResult) 
        
        print "\n Frame ", i
        print "Template width", w, "Template height", h, "Max correlation value", max_val 
        
        if max_val > blackScreenThreshold: 
            currentFrameString = "Found"
            
            if max_val < matchFrameThreshold:  #Go for resize and match if match corr value is less than threshold
                template = np.copy(cv2.imread(templateFile,1)) # Reset to original template
                template, max_loc, max_val, frame = resizeAndTemplateMatch(frame, template,i) #Resize template and match
                if max_val>matchFrameThreshold:
                    h, w = template.shape[:2]
                    x, y = max_loc
                    x1, y1 = x+w, y+h
                    matchTemplateShape = template.shape
                else:
                    template = np.copy(cv2.imread(templateFile,1)) # Reset to original template
                    currentFrameString = "Not Found"
                    print "Current Frame: ", currentFrameString                                      
                    
                    if currentFrameString!=prevFrameString and int(i)!=0: #Populate foundArray
                        updateFoundArray(foundArray, currentFrameString, prevFrameString)

                    frameText = "Frame number: "+ str(i) + " Result: " + currentFrameString
                    cv2.putText(frame, frameText , (600,600), cv2.FONT_HERSHEY_SIMPLEX, 0.5, 255)
                    video.write(frame)
                    
                    locArray.append("Not Found")
                    notFoundCount = notFoundCount+1
                    prevFrameString=currentFrameString  
                    
                    continue
            else:
                # if template match corr value exceeds threshold
                h, w = template.shape[:2]
                x, y = max_loc
                x1, y1 = x+w, y+h
                matchTemplateShape = template.shape

            cv2.rectangle(frame, (x,y), (x1,y1), (0,255,0), 1)
            
            
            if currentFrameString!=prevFrameString and int(i)!=0: #Populate foundArray
                updateFoundArray(foundArray, currentFrameString, prevFrameString)
                
            foundCount = foundCount+1
            
        else:  # if match corr value is less than 0.2 consider it as black frame
            template = np.copy(cv2.imread(templateFile,1)) # Reset to original template
            currentFrameString = "Black"
            
            if currentFrameString!=prevFrameString and int(i)!=0: #Populate foundArray
                updateFoundArray(foundArray, currentFrameString, prevFrameString)
                
            blackCount = blackCount+1
            
        currentFrameResult[0] = i
        currentFrameResult[1] = max_val
        currentFrameResult[2] = currentFrameString
        currentFrameResult[3] = max_loc
  
        #Populate locArray
        if currentFrameString=="Found":
            locArray.append(max_loc)
        elif currentFrameString=="Not Found":
            locArray.append("Not Found")
        elif currentFrameString == "Black":
            locArray.append("Black")
            
        
        #Append foundArray for last frame    
        if i==lastFrameIndex:
            if currentFrameString=="Found":
                string = ["Found" , foundCount, matchTemplateShape]
                foundArray.append(string)                
            elif currentFrameString=="Black":
                string = ["Black", blackCount]
                foundArray.append(string)
            elif currentFrameString=="Not Found":
                string = ["Not Found", notFoundCount]
                foundArray.append(string)          
        
        #i=i+1
        print "Current Frame: ", currentFrameString
        prevFrameString=currentFrameString
        
        frameText = "Frame number: "+ str(i) + " Result: " + currentFrameString
        cv2.putText(frame, frameText , (600,600), cv2.FONT_HERSHEY_SIMPLEX, 0.5, 512)
        video.write(frame)
        
        """      
        cv2.imshow('frame',frame)
        cv2.imshow('template',template)       
        
        if cv2.waitKey(50) & 0xFF == ord('q'):
            print "Quitting due to user input"
            break
            
        if cv2.waitKey(50) & 0xFF == ord('p'):
            cv2.waitKey(0)
            break
        
        """
            
    capture.release()
    video.release()
    cv2.destroyAllWindows()

    print "\n Location Array: \n", locArray
    print "\n Found Array: \n", foundArray
    
    verifiedArray = computeVerifiedArray(locArray,foundArray, diffArray)
    print "\n Final Verified Array: ", verifiedArray
    
    updatedVerifiedArray = updateVerifiedArray(verifiedArray)
    
    result, comment = finalResult(updatedVerifiedArray)
    result = str(result)
    comment = str(comment)
    
    #Write result and comment in the output file
    f.write("Result: ")
    f.write(result)
    f.write("\n")
    f.write("Comment: ")
    f.write(comment)
    f.close()
    
    elapsed_time = time.time() - start_time
    print "Elapsed time: ", elapsed_time

def updateFoundArray(foundArray, currentFrameString, prevFrameString):
    """Update foundArray based on the previous Count"""
    print "\n UPDATING FOUND ARRAY"
    global foundCount
    global blackCount
    global notFoundCount
    global matchTemplateShape
    
    if prevFrameString != currentFrameString:    
        if prevFrameString == "Found":
            prevCount = foundCount
            foundCount = 0
        elif prevFrameString == "Not Found":
            prevCount = notFoundCount
            notFoundCount = 0
        elif prevFrameString == "Black":
            prevCount = blackCount
            blackCount = 0
        elif prevFrameString == "": 
            return
    else:
        return
        
    if len(foundArray)>0:    
        if foundArray[-1][0]!=prevFrameString and prevCount > 0:
            string = [prevFrameString , prevCount]
            foundArray.append(string)
            #Append template shape
            if prevFrameString == "Found" and matchTemplateShape != ():
                foundArray[-1].append(matchTemplateShape)
                matchTemplateShape = ()
            print "foundArray: ", foundArray
    else:
        string = [prevFrameString , prevCount]
        foundArray.append(string)
        #Append template shape
        if prevFrameString == "Found" and matchTemplateShape != ():
            foundArray[-1].append(matchTemplateShape)
            matchTemplateShape = ()
        print "foundArray: ", foundArray

"""
methods = ['cv2.TM_CCOEFF', 'cv2.TM_CCOEFF_NORMED', 'cv2.TM_CCORR',
            'cv2.TM_CCORR_NORMED', 'cv2.TM_SQDIFF', 'cv2.TM_SQDIFF_NORMED']
"""


def resizeAndTemplateMatch(frame, template, i):
    """Return resized Template, maximum correlation value and location"""
    print "RESIZE TEMPLATE AND MATCH"
    for resizeScale in np.linspace(0.3, 2.5, 40)[::-1]:
    
        tempFrame = []  #internal temporary variable to store the frame
        tempFrame = np.copy(frame)
       
        resizedTemplate = imutils.resize(template, width = int(template.shape[1] * resizeScale)) #Resize the template 
        resizedTemplate = imutils.resize(template, width = int(template.shape[1] * resizeScale)) #Resize the template 
        resizeRatio =  float(resizedTemplate.shape[1])/template.shape[1]        
        h,w = resizedTemplate.shape[:2]
        
        matchResult = cv2.matchTemplate(frame,resizedTemplate,cv2.TM_CCORR_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(matchResult)
        print "Template width", w, "Template height", h, "Max correlation value", max_val, "Resize Ratio", resizeRatio, "Resize Scale", resizeScale 
        
        if max_val>blackScreenThreshold: 
            x, y = max_loc
            x1, y1 = x+w, y+h
            cv2.rectangle(frame, (x,y), (x1,y1), (0,0,255), 1)
            
            
        frameText = "Frame number: "+ str(i) + " Max Corr Value: " + "%.2f"%max_val
        cv2.putText(frame, frameText , (600,600), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,255))
        video.write(frame)
            
        """
        cv2.imshow("frame",frame)
        cv2.imshow("resizedTemplate",resizedTemplate) 

        if max_val <matchFrameThreshold:
            cv2.waitKey(50)
        else:
            cv2.waitKey(2000)
        cv2.destroyAllWindows()
        """
        
        #Break the loop if the max correlation value exceeds threshold
        if max_val>matchFrameThreshold:
            frame = []
            frame = np.copy(tempFrame)            
            break     
        
        # Copy the frame from temporary variable to avoid the rectangle drawn for next iteration
        frame = []
        frame = np.copy(tempFrame)    

        """           
        if cv2.waitKey(500) & 0xFF == ord('q'):
            print "Quitting due to user input"
            break """
        
    return resizedTemplate, max_loc, max_val, frame

def updateVerifiedArray(verifiedArray):
    """Update verifiedArray to remove "Black" elements with count less than 3 and then combine the adjacent "Found" elements"""
    print "\n UPDATING VERIFIED ARRAY \n"    
    
    if verifiedArray == "":
        return ""
    
    for v in range(len(verifiedArray)-1):
        print "Current Element: ", verifiedArray[v]
        i = verifiedArray[v]
        currentFrameString = i[0]
        count = i[1]
        if currentFrameString=="Black" and (v != 0 or v != (len(verifiedArray)-1)):
            if count<3:
                verifiedArray.remove(i)
                print "Removed black element with count less than 3 \n Current verifiedArray:", verifiedArray
                                
    for i in range(len(verifiedArray)-1):
        if i<len(verifiedArray)-1:
            if ("Verified" in verifiedArray[i] and "Verified" in verifiedArray[i+1]):
                if (computeDist(verifiedArray[i][3], verifiedArray[i+1][3]))<10:
                    verifiedArray[i][1] += verifiedArray[i+1][1]
                    j = verifiedArray[i+1]                    
                    verifiedArray.remove(j)
                    print "Combined adjacent verified frames with distance less than 10 \n Current verifiedArray: ", verifiedArray
    updatedVerifiedArray = verifiedArray
    print "Updated verifiedArray: \n", updatedVerifiedArray
    return updatedVerifiedArray

def computeDist(pos, prevPos):
    """Compute distance between 2 given points"""
    x1,y1 = pos
    x2,y2 = prevPos
    dist = math.hypot(x2-x1, y2-y1)
    return dist 
 
 
def finalResult(updatedVerifiedArray):
    """Evaluate the updatedVerifiedArray to arrive at final result"""
    global maxBnf
    global minBnf
    global maxFf
    global minFf
    global blackScreenThreshold
    global matchFrameThreshold
    global totalFrames
    
    notVerifiedCount = 0
    verifiedInstantCount = 0
    totalVerifiedCount = 0
    
    print "\n EVALUATING FINAL RESULT \n"
    print updatedVerifiedArray
    comment = ""
    result = "Pass"   
    y = updatedVerifiedArray
    last = len(y)-1 
    
    if updatedVerifiedArray == "":
        result = "Fail"
        comment = "Empty updatedVerifiedArray"
        return result, comment
    
    for x in range(len(y)):
        currentFrameString = y[x][0]
        count = y[x][1]
        prevPos = ""
        pos=""
        prevShape = ""
        
        if len(y[x])==4:
            pos = y[x][3]
            shape = y[x][2]
            if (x > 1):
                if currentFrameString =="Verified":
                    for i in range(1,8):
                        z = x-i
                        if z>-1 and y[z][0]=="Verified":
                            prevShape = y[x-i][2]
                            prevPos = y[x-i][3]
                            print "Current Element: ", y[x], "Current position: ", pos, "Previous position: ", prevPos, "Previous Shape: ", prevShape
        
        if currentFrameString == "Black":
            if (x>0 and x<last):
                if count<minBnf or count>maxBnf:
                    result = "Fail"
                    comment1 = "Black frames count", count, "Expected: 10 to 15 in every cycle"
                    comment = "\n" + comment + str(comment1) + "\n"                 
            else:
                if count > maxBnf:
                    result = "Fail"
                    comment1 = "Black frames count", count, "Expected range: ", (minBnf, maxBnf)
                    comment = "\n" + comment + str(comment1) + "\n"
            notVerifiedCount += count
                        
        if currentFrameString == "Verified":
            if (x>0 and x<last):
                if count < minFf or count > maxFf:
                    result = "Fail"
                    comment1 = "Verifed frames count", count, "Expected: 230 to 250 in every cycle"
                    comment = "\n" + comment + str(comment1) + "\n"
            else:
                if count > maxFf:
                    result = "Fail"
                    comment1 = "Verifed frames count", count, "Expected range: ", (minFf, maxFf)
                    comment = "\n" + comment + str(comment1) + "\n"               
                    
            if prevPos != "":
                dist = computeDist(pos, prevPos) 
                print "dist", dist
                if dist<10: #Taking 10 as the minimum distance between the icon positions in consecutive cycles arbitrarily
                    result = "Fail"
                    comment = "\n" + comment + " In current and next cycle channel icon is displayed in same position \n"
                    
            if prevShape != "":
                print "Current shape: ", shape, "Previous shape: ", prevShape
                if prevShape == shape:
                    result = "Fail"
                    comment = "\n" + comment + " In current and next cycle channel icons are of same size"
                    
            if verifiedInstantCount>0:
                if notVerifiedCount>(2*maxBnf):
                    result = "Fail"
                    comment = "\n" + comment + "No. of frames between consecutive verified frames " + str(notVerifiedCount) + " is greater than threshold "+ str(2*maxBnf)
                    
            verifiedInstantCount += 1
            totalVerifiedCount += count
                    
        if currentFrameString == "Mismatch":
            if count > minBnf: #Using minBnf as threshold for number of mismatch frames
                result = "Fail"
                comment1 = "Mismatch frames count", count, "Expected value: Less than ", minBnf
                print comment1
                comment = "\n" + comment + str(comment1) + "\n"
            notVerifiedCount += count
                
        if currentFrameString == "Not Found":
            if count > minBnf: #Using minBnf as threshold for number of notFound frames
                result = "Fail"
                comment1 = "Not Found frames count", count, "Expected value: Less than ", minBnf
                print comment1
                comment = "\n" + comment + str(comment1) + "\n"
            notVerifiedCount += count            
            
    if totalVerifiedCount < (0.85*totalFrames):
        result = "Fail"
        comment = "\n" + comment + "\nTotal verified count " + str(totalVerifiedCount) + " is less than threshold 0.85*totalFrames i.e " + str(int(0.85*totalFrames))
        
    if comment == "" and result == "Pass":
        comment = "Graphics verification passed. \n updatedVerifiedArray: " + str(updatedVerifiedArray)
        
    print "\n Result:   ", result, "\n Comment: ", comment
    return result, comment 
    
def allElementEqual(locSet):
    count = 0
    for i,loc in enum(locSet):
        if loc[0]==loc[i]:
            count += 1
    if count == len(locSet):
        return True
    else:
        return False
   
        
    

def findMeanPos(locSet):
    """Find mean position for a set of found frames"""
    global meanDistThreshold
    print "FINDING meanLoc"
    print "locSet: ", locSet
    iterArray = []
    sumArray = []
    pos = ""
    
    if allElementEqual(locSet):
        pos = locSet[0]
    else:
        for i in locSet:
            if locSet.count(i) > 2:
                pos = i
                return pos
             
        for i in locSet:
            iter = computeDiffPos(i, locSet)
            iterArray.append(iter)
            sumIterArray = sum(iter)
            sumArray.append(sumIterArray)
        print "iterArray", iterArray, "\nsumArray", sumArray
        
        minimumValue = min(sumArray)
        if minimumValue > meanDistThreshold:
            return pos
            
        for i in range(len(sumArray)):
            if minimumValue == sumArray[i]:
                pos = locSet[i]
                break
    return pos

def computeDiffPos(meanLoc, diffLocSet):
    """Compute distance between mean location and all the elements in the given locSet to find meanLoc"""
    print "\n COMPUTING diffLocArray \n"
    print "diffLocSet", diffLocSet
    diffLocArray = []
    for i in range(len(diffLocSet)):        
        x1,y1 = meanLoc
        x2,y2 = diffLocSet[i]
        print x1, y1, x2, y2
        dist = math.hypot(x2-x1, y2-y1)
        diffLocArray.append(dist)
    return diffLocArray
    
    
def computeDiff(meanLoc, diffLocSet, diffArray):
    """Compute distance between mean location and all the elements in the given diffLocSet and then append the diffArray"""
    for i in range(len(diffLocSet)):
        x1,y1 = meanLoc
        x2,y2 = diffLocSet[i]
        dist = math.hypot(x2-x1, y2-y1)
        diffArray.append(dist)
    return diffArray

def computeDiffArray(locArray, foundArray, diffArray):
    """COMPUTE diffArray LISTING THE DISTANCE BETWEEN FOUND POSITION OF EACH "Found" FRAME AND CORRESPONDING MEAN LOCATION"""
    print "\n COMPUTING diffArray"
    locIndex = 0
    for i in range(len(foundArray)):
        value = foundArray[i][0]
        count = foundArray[i][1]        
        if value == "Found":
            if count > 5:
                print "\n Index: ", locIndex, locIndex+4
                locSet = locArray[locIndex:locIndex+5]
                meanLoc = findMeanPos(locSet)
                j = 1
                while meanLoc == "":
                    nextStartIndex = (locIndex + (5*j))
                    nextEndIndex = nextStartIndex + 4
                    k = (j+1)*5
                    if count > k:
                        locSet = locArray[nextStartIndex:nextEndIndex+1]
                        meanLoc = findMeanPos(locSet)
                    else:
                        return ""
                    j += 1
                        
                    
                print "meanLoc: ", meanLoc
                foundArray[i].append(meanLoc)
                print "Current foundArray: ", foundArray
                diffLocSet = locArray[locIndex:locIndex+count]
                print "diffLocSet: ", diffLocSet
                diffArray = computeDiff(meanLoc, diffLocSet, diffArray)
                print "Current diffArray: ", diffArray
                
        elif value == "Black":
            for i in range(count):
                diffArray.append("Black")        
        
        elif value == "Not Found":
            for i in range(count):
                diffArray.append("Not Found")
                
        locIndex += count
        
    return diffArray
    
def computeVerifiedArray(locArray,foundArray,diffArray):
    """Compute verifiedArray from foundArray"""
    print "\n COMPUTING verifiedArray \n"
    verifiedCount = 0
    mismatchCount = 0
    notFoundCount = 0
    diffIndex = 0
    verifiedArray = []
    
    diffArray = computeDiffArray(locArray,foundArray,diffArray) #Compute diffArray
    print "\n Final diffArray: ", diffArray
    
    if diffArray =="": #Not able to find meanLoc since the meanDist exceeds meanDistThreshold 
        return ""
        
    length = len(foundArray)
    
    for i in range(len(foundArray)):
        currentFrameString=""
        print "\n Current foundArray element: ", foundArray[i]       
        value = foundArray[i][0]
        count = foundArray[i][1] 
        prevString = "initial"
        verifyArraySet = diffArray[diffIndex:diffIndex+count]
        print "verifyArraySet: ", verifyArraySet
        
        diffIndex += count
        if value == "Found":                          
            for k in range(len(verifyArraySet)):
                x = verifyArraySet[k]
                if x>10:
                    currentFrameString = "Mismatch"
                    if prevString!=currentFrameString and int(k)!=0:
                        string = ["Verified", verifiedCount, foundArray[i][2], foundArray[i][3]]
                        verifiedArray.append(string)
                        print "Current verifiedArray: ", verifiedArray
                        verifiedCount = 0
                    prevString = currentFrameString
                    mismatchCount += 1
                else:
                    currentFrameString="Verified"
                    if prevString!=currentFrameString and int(k)!=0:
                        string = ["Mismatch", mismatchCount]
                        verifiedArray.append(string)
                        print "Current verifiedArray: ", verifiedArray
                        mismatchCount = 0
                    prevString = currentFrameString
                    verifiedCount += 1
        else:
            if verifiedCount>0:
                string = ["Verified", verifiedCount, foundArray[i-1][2], foundArray[i-1][3]]
                verifiedArray.append(string)
                print "Current verifiedArray: ", verifiedArray
                verifiedCount = 0
            if mismatchCount>0:
                string = ["Mismatch", mismatchCount]
                verifiedArray.append(string)
                print "Current verifiedArray: ", verifiedArray
                mismatchCount = 0
            currentFrameString = value
            verifiedArray.append(foundArray[i])
            print "Current verifiedArray: ", verifiedArray            
            
        if i==(len(foundArray)-1):
            if currentFrameString=="Verified":
                string = ["Verified", verifiedCount, foundArray[i][2], foundArray[i][3]]
                verifiedArray.append(string)
                print "Current verifiedArray: ", verifiedArray
            elif currentFrameString == "Mismatch":
                string = ["Mismatch", mismatchCount]
                verifiedArray.append(string)
                print "Current verifiedArray: ", verifiedArray
                        
    return verifiedArray

if __name__ == "__main__":
   main()







            
            
                
                
            


    

