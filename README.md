# SrtGoogleTranslate

使用步骤：
1、说明：
	需要配合AutoSub使用（https://github.com/agermanidis/autosub/issues/31）
	将AutoSub生成的英文字幕批量翻译成中文（上译文下原文形式），并支持术语库文本替换
	由于GoogleTranslateAPI会检测异常流量，所以设置了每0.3秒翻译一句避免IP被Ban，如果不幸被Ban请切换下WANIP

2、运行CMD：
	C:\Python27\Scripts\pip.exe install googletrans
	C:\Python27\Scripts\pip.exe install retry
	
3、将SrtGoogleTranslate.py复制到C:\Python27\scripts\

4、新建txt，输入：
	C:\Python27\python.exe C:\Python27\scripts\SrtGoogleTranslate.py -p "D:\"
	或者
	C:\Python27\python.exe C:\Python27\scripts\SrtGoogleTranslate.py -p "D:\" -d "D:\术语库.txt"
	PS："D:\"替换成需要批量翻译的文件夹（包括子文件夹），"D:\术语库.txt"替换成术语库文本路径
	
5、术语库格式：
	替换目标
	替换为
	
	替换目标
	替换为
	
	...	