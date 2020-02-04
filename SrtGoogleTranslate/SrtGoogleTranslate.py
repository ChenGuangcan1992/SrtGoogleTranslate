#!c:\python27\python.exe
# -- coding: utf-8 --
import io
import os
import sys
import time
import argparse
from googletrans import Translator
from googletrans.utils import format_json
from retry import retry

#参数输入
parser=argparse.ArgumentParser()
parser.add_argument('-p',help='Path to the SRT Folder')
parser.add_argument('-d',help='Path to the Dict File')
parser.add_argument('-s',help='Source Language')
parser.add_argument('-n',help='No Source Language')
parser.add_argument('-t',help='Time to Retry')
parser.add_argument('-c',help='Use GoogleCN')
parser.add_argument('-b',help='Translate Sentence By Sentence')
parser.add_argument('-g',help='Check Mode')
args = parser.parse_args()
if args.t:
    #重试时间
    retryTime=int(args.t)
else:
    retryTime=60
if args.s:
    #视频语言
    srcLang=args.s
else:
    srcLang='en'
if args.n:
    #无原字幕
    srcSrt=False
else:
    srcSrt=True
if args.c:
    #使用GoogleCN
    googleLoc='cn'
else:
    googleLoc='com'
if args.b:
    #断连写入
    fileTrans=False
else:
    #断连重试
    fileTrans=True
if args.g:
    #检查模式
    chkMode=True
else:
    chkMode=False

#"""Google翻译API"""
headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
translator = Translator(service_urls=['translate.google.'+googleLoc])
banFlag = False

#"""单句翻译函数"""
@retry(delay=retryTime)
def sentenceTranslate(line):
	line = line.strip()
	try:
		text = translator.translate(line,src=srcLang,dest='zh-cn').text
	except:
		print 'Translate Failed. Please Change Your WAN IP Address!'
	return text

#"""段落翻译函数"""
def partTranslate(lineOffset,lineIdx,lines):
    transLines=[]
    global banFlag
    transLines.append(lines[lineIdx-lineOffset])
    transLines.append(lines[lineIdx-(lineOffset-1)])
    #"""单句翻译"""
    try:
        if chkMode:
            transLines.append(lines[lineIdx-(lineOffset-2)])
        else:
            transLines.append(translator.translate(lines[lineIdx-(lineOffset-2)].strip(),src=srcLang,dest='zh-cn').text+'\n')
            #"""防止谷歌BanIP"""
            time.sleep(0.3)
    except:
        #"""被BAN"""
        transLines.append(lines[lineIdx-(lineOffset-2)])
        if lineOffset>2:
            transLines.append(lines[lineIdx])
        banFlag=True
        print '!!!!!!!!!!!!BAN!!!!!!!!!!!!'
        return transLines
    #"""有原文"""
    if srcSrt:
        transLines.append(lines[lineIdx-(lineOffset-2)])
    #"""无原文"""
    else:
        transLines.append('    '+'\n')
    if lineOffset>2:
        transLines.append(lines[lineIdx])
    return transLines

#"""术语库加载函数"""
def loadReplaceWords(path):
    replaceTableFile=io.open(path,mode='r',encoding='utf-8')
    lines=[]
    for line in replaceTableFile:
        lines.append(line.replace('\n',''))
    replaceTableFile.close()
    dict={}
    for lineIdx in range(len(lines)):
        if lineIdx%3==0 and lines[lineIdx]!='':
            dict.setdefault(lines[lineIdx],lines[lineIdx+1])
    return dict

#"""术语库批量替换函数"""
def sentenceReplace(line,**dict):
    for key in dict.keys():
        line=line.replace(key,dict[key])
    return line

#"""单SRT翻译模式"""
def oneTranslate(path,**dict):
    #"""字幕文件读取"""
    tempFile = io.open(path,mode='r',encoding='utf-8')
    lines=[]
    for line in tempFile:
        lines.append(line)
    tempFile.close()

    #"""不是空文件"""
    if len(lines)>3:
        #"""是否已翻译"""
        isTranslate=False
        if len(lines[4])==1:
            isTranslate=True

        #"""Google翻译"""
        transLines=[]
        if not isTranslate:
            #"""逐句翻译"""
            for lineIdx in range(len(lines)):
                if lineIdx%4==2:
                    transLines.append(sentenceTranslate(lines[lineIdx])+'\n')
                    #"""进度条"""
                    sys.stdout.write(tempPath.split('\\')[-1]+': '+str(int((lineIdx*1.0)/len(lines)*10000)/100.0)+'%'+"\r")
                    #"""防止谷歌BanIP"""
                    time.sleep(0.3)
                #"""有原文"""
                if srcSrt:
                    transLines.append(lines[lineIdx])
                #"""无原文"""
                else:
                    if lineIdx%4==2:
                        transLines.append('    '+'\n')
                    else:
                        transLines.append(lines[lineIdx])

            #"""列表转文本"""
            totalContent=''.join(transLines)

            #"""术语库替换"""
            totalContent=sentenceReplace(totalContent,**dict)

            #"""写入译文"""
            tempFile = io.open(tempPath,mode='w+',encoding='utf-8')
            tempFile.write(totalContent)
            tempFile.close()
            print(tempPath.split('\\')[-1])

        #"""清理临时列表"""
        del lines[:]
        del transLines[:]
    return 0

#"""断连停止模式"""
def senTranslate(path,**dict):
    #"""字幕文件读取"""
    tempFile = io.open(path,mode='r',encoding='utf-8')
    lines=[]
    for line in tempFile:
        lines.append(line)
    tempFile.close()

    #"""不是空文件"""
    if len(lines)>3:

        #"""Google翻译"""
        transLines=[]
        senNum=0

        #"""逐句检查"""
        for lineIdx in range(len(lines)):
            #"""第X句"""
            if (lineIdx>0)&(len(lines[lineIdx-1])==1):
                senNum = lineIdx

            #"""被BAN处理"""
            if banFlag:
                transLines.append(lines[lineIdx])

            #"""空行检查"""
            elif len(lines[lineIdx])==1:
                #"""未翻译"""
                if lineIdx-senNum==3:
                    tmpTransLines=[]
                    tmpTransLines=partTranslate(3,lineIdx,lines)
                    for tmpTransLinesIdx in range(len(tmpTransLines)):
                        transLines.append(tmpTransLines[tmpTransLinesIdx])
                    del tmpTransLines[:]
                #"""已翻译"""
                else:
                    for tmpIdx in range(lineIdx-senNum,-1,-1):
                        transLines.append(lines[lineIdx-tmpIdx])

            #"""最后一句"""
            elif lineIdx==len(lines)-1:
                #"""未翻译"""
                if lineIdx-senNum==2:
                    tmpTransLines=[]
                    tmpTransLines=partTranslate(2,lineIdx,lines)
                    for tmpTransLinesIdx in range(len(tmpTransLines)):
                        transLines.append(tmpTransLines[tmpTransLinesIdx])
                    del tmpTransLines[:]
                #"""已翻译"""
                else:
                    for tmpIdx in range(lineIdx-senNum,-1,-1):
                        transLines.append(lines[lineIdx-tmpIdx])

            #"""进度条"""
            if not chkMode:
                sys.stdout.write(tempPath.split('\\')[-1]+': '+str(int((lineIdx*1.0)/len(lines)*10000)/100.0)+'%'+"\r")

        #"""列表转文本"""
        totalContent=''.join(transLines)

        #"""术语库替换"""
        totalContent=sentenceReplace(totalContent,**dict)

        #"""写入译文"""
        if len(lines)!=len(transLines):
            if chkMode:
                print tempPath
                print str(len(lines))+'--O--N--'+str(len(transLines))
                print '\n'
            else:
                tempFile = io.open(tempPath,mode='w+',encoding='utf-8')
                tempFile.write(totalContent)
                tempFile.close()
                print('---------------Complete:'+tempPath.split('\\')[-1])

        #"""清理临时列表"""
        del lines[:]
        del transLines[:]
    return 0

if args.d:
    #"""术语库路径"""
    replaceTablePath=args.d
    rDict=loadReplaceWords(replaceTablePath)
else:
    rDict={}

if args.p:
    #"""SRT文件夹路径"""
    tempDirPath=args.p
    #"""批量翻译SRT"""
    for dirpath, dirnames, filenames in os.walk(tempDirPath):
        for filepath in filenames:
            tempPath = os.path.join(dirpath, filepath)
            if filepath[-4:]=='.srt' or filepath[-4:]=='.SRT':
                if fileTrans:
                    oneTranslate(tempPath,**rDict)
                else:
                    senTranslate(tempPath,**rDict)