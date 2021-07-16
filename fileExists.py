import os
import shutil

fileName = automotoContext.Variables.GetVarValue("fileName").StringValue

if (fileName.find ('\\\\') == -1):
	file = fileName.replace('\\', '\\\\')
else:
	file = fileName

if (os.path.isfile(file)):
	result = 1
else:
	result = 0

output_dict = result