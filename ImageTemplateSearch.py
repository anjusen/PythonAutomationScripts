from System import *
from System.Collections.Generic import *
from System.IO import *
from System.Net import *
from System.Text import *
from System.Globalization import *
#import os

#get runtime variables from AM
templateSearchResults = automotoContext.Variables.GetRunTimeArray("templateSearchResults")
numTemplatesMin1 = automotoContext.Variables.GetVarValue("numTemplatesMin1").IntValue
numCharPosMin1 = automotoContext.Variables.GetVarValue("numCharPosMin1").IntValue
margin = automotoContext.Variables.GetVarValue("margin").IntValue
timeStampDigitXPosArray = automotoContext.Variables.GetRunTimeArray("timeStampDigitXPosArray")
timeStampDigitYPosArray = automotoContext.Variables.GetRunTimeArray("timeStampDigitYPosArray")
bestSimilarity = automotoContext.Variables.GetRunTimeArray("bestSimilarity")
digitResultArray = automotoContext.Variables.GetRunTimeArray("digitResultArray")
templateArray = automotoContext.Variables.GetRunTimeArray("templateArray")
template2NumberArray = automotoContext.Variables.GetRunTimeArray("template2NumberArray")

#initialize arrays to copy digitResultArray and bestSimilarity to for further processing
digits = []
similarity = []

#copy each element of the digitResultArray to digits list for further processing
for digitIndex in range (0, digitResultArray.Length):
	digits.insert(digitIndex, digitResultArray.GetValueByIndex(digitIndex))
	
#copy each element of the bestSimilarity array to similarity list for further processing
for similarityIndex in range (0, bestSimilarity.Length):
	similarity.insert(similarityIndex, bestSimilarity.GetValueByIndex(similarityIndex))

#
for templateIndex in range (0, numTemplatesMin1 + 1):
	print '-------------------------TEMPLATE INDEX: ' + str(templateIndex) + '-------------------------------------------------'
	templateResult = templateSearchResults.GetValueByIndex(templateIndex)
	print templateIndex
	print templateResult
	currentTemplate = templateArray.GetValueByIndex(templateIndex)
	currentDigit = template2NumberArray.GetValueByKey(str(currentTemplate).replace("\"", ''))
	print 'current digit: ' + str(currentDigit)
		
	#number of matches for the current iteration
	numberOfResults = templateResult.Length
	print 'numberOfResults: ' + str(numberOfResults)
	if numberOfResults > 0:
		for i in range (0, numberOfResults):
			#X and Y coordinates of the current match
			print '-----------imageTemplateSearch result index: ' + str (i) + '---------------'
			currentXresult = templateResult.GetValueByIndex(i).GetValueByKey(str("X")).IntValue
			currentYresult = templateResult.GetValueByIndex(i).GetValueByKey(str("Y")).IntValue
			
			#current similarity level
			currentSimilarity = templateResult.GetValueByIndex(i).GetValueByKey(str("Similarity")).DoubleValue
			print 'Positions and sim from imageTemplateSearch: current X: ' + str(currentXresult) + ' current Y: ' + str(currentYresult) + '. Current Similarity: ' + str (currentSimilarity)
			
			for posIndex in range (0, numCharPosMin1+1):
				print 'position index: ' + str(posIndex)
				currentXpos = timeStampDigitXPosArray.GetValueByIndex(posIndex).IntValue
				currentYpos = timeStampDigitYPosArray.GetValueByIndex(posIndex).IntValue
				lowerXrange = currentXpos - margin
				upperXrange = currentXpos + margin
				lowerYrange = currentYpos - margin
				upperYrange = currentYpos + margin
				currentBestSimilarity = bestSimilarity.GetValueByIndex(posIndex).DoubleValue
				currentBestSimilarity = similarity[posIndex]
				print 'positions and ranges from the positions array: ' 
				print 'X: ' + str(currentXpos) + ' Y: ' + str (currentYpos) + '. Current Best similarity: ' + str(currentBestSimilarity)
				
				if  currentXresult >= lowerXrange and currentXresult <= upperXrange and currentYresult >= lowerYrange and currentYresult <= upperYrange and currentBestSimilarity < currentSimilarity:
					#print 'Found a match!'
					digits[posIndex] = currentDigit
					similarity[posIndex] = currentSimilarity
					#print 'digits[posIndex]: ' + str (digits[posIndex]) + '. similarity[posIndex]: ' + str(similarity[posIndex])
					#print 'better match found'
					#digitResultArray.insert(posIndex, currentDigit)
					#bestSimilarity.insert(posIndex, currentSimilarity)
					#if len(digitResultArray) > posIndex:
					#digitResultArray[posIndex] = currentDigit
					#else: 
					#	digitResultArray.append(currentDigit)
					#bestSimilarity[posIndex] = currentSimilarity
					#similarityResultArray.append(currentSimilarity)
				#else:
					#print 'previous one was better'
					#print currentBestSimilarity
				
#print digitResultArray
#print similarityResultArray
				
#output_dict = digitResultArray, similarityResultArray
#output_dict = digitResultArray, bestSimilarity
output_dict = digits, similarity
			

