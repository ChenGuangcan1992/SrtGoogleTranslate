#!c:\python27\python.exe
# -- coding: utf-8 --
import io
import os

tempDirPath='C:\\Users\\CGC\\AppData\\Local\\Temp'
for dirpath, dirnames, filenames in os.walk(tempDirPath):
	for filepath in filenames:
		tempPath = os.path.join(dirpath, filepath)
		if filepath[-5:]=='.flac' or filepath[-5:]=='.FLAC':
			if filepath[:3]=='tmp':
				os.remove(tempPath)
				print 'Delete: '+tempPath
