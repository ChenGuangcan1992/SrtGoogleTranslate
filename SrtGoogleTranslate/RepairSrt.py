#!c:\python27\python.exe
# -- coding: utf-8 --
import io

tempPath='D:\\Download\\ZBrushMerge2019.srt'
tempFile = io.open(tempPath,mode='r',encoding='utf-8')
lines=[]
for line in tempFile:
    lines.append(line)
tempFile.close()
tempFile = io.open(tempPath,mode='w+',encoding='utf-8')
for lineIdx in range(len(lines)):
    if lineIdx%4==1 and lineIdx>2 and lineIdx<3457:
        tempFile.write(lines[lineIdx][:-13]+lines[lineIdx+4][:12]+'\n')
    else:
        tempFile.write(lines[lineIdx])
tempFile.close()
