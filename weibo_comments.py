#!/usr/bin/python
# author:gitxxx
# -*- coding: UTF-8 -*-
import urllib
import urllib2
import re
import datetime
import time
import json
import sys  
import HTMLParser
import getopt

reload(sys)  
sys.setdefaultencoding('UTF-8')   

def getAllInfo(page):
	preUrl = 'http://weibo.com/aj/v6/comment/big?ajwvr=xxxxxxxx&id=xxxxxxxx&page='
	timestamp = "%d" % (time.time()*1000)
	url = preUrl + str(page) + '&__rnd=' + str(timestamp)
	cookie = 'xxxxxxxx'
	user_agent = 'xxxxxxxx'
	headers = { 
		'User-Agent' : user_agent,
		'Cookie' : cookie
	}
	req = urllib2.Request(url, headers=headers)
	response = urllib2.urlopen(req)
	res = response.read()
	return res
	
def parsePageContent(res):
	dic={}
	resJson = json.loads(res)
	data = resJson["data"]
	page = data['page']
	dic['count'] = data['count']
	dic['html'] = data['html']
	dic['totalpage'] = page['totalpage']
	dic['pagenum']  = page['pagenum']
	return dic

def parseWeiboComment(startTime,page,html):
	regular = '<div class="WB_text">.*?<a target="_blank" href=".*?" usercard="(.*?)" ucardconf="type=1">(.*?)</a>(.*?) </div>.*?<div class="WB_from S_txt2">(.*?) </div>'
	pattern = re.compile(regular,re.S)
	items = re.findall(pattern,html)
	length = len(items)
	if page == 1:
		min = length - 20
		for i in range(min,length):
			item = items[i]
			parseDetail(startTime, item)
	else:
		for item in items:
			parseDetail(startTime, item)
	
def parseDetail(startTime,item):
	cgid = ''
	uid = item[0].strip()
	uname = '"' + item[1].strip() + '"'
	ucomment = item[2].strip()
	utime = processTime(item[3].strip())
	if compareTime(utime, startTime):
		regular = r'\d{5,}'
		pattern = re.compile(regular,re.S)
		items = re.findall(pattern,ucomment)
		for item in items:
			if uid !='id=3227514625':
				if cgid == '':
					cgid = item
				else:
					cgid = cgid + ";" + item
		if cgid != '' :
			print (uid +"," + uname +"," + cgid + "," + utime).encode('GBK')
	else:
		exit()

def processTime(utime):
	today = "今天"
	minute = "分钟"
	seconds = "秒"
	month = "月"
	if today in utime:
		regular = '.*?(\d+:\d+)'
		pattern = re.compile(regular,re.S)
		items = re.findall(pattern,utime)
		utime = time.strftime('%Y-%m-%d',time.localtime(time.time())) + ' '+ items[0]
	elif minute in utime:
		regular = r'\d+'
		pattern = re.compile(regular,re.S)
		items = re.findall(pattern,utime)
		sec = int(items[0]) * 60 
		timestamp = time.time() - float(sec)
		time_local = time.localtime(timestamp)
		utime = time.strftime("%Y-%m-%d %H:%M",time_local)
	elif seconds in utime:
		regular = r'\d+'
		pattern = re.compile(regular,re.S)
		items = re.findall(pattern,utime)
		sec = int(items[0])
		timestamp = time.time() - float(sec)
		time_local = time.localtime(timestamp)
		utime = time.strftime("%Y-%m-%d %H:%M",time_local)
	elif month in utime:
		year = time.strftime('%Y',time.localtime(time.time()))
		utime = year + "-" + utime.replace("月","-").replace("日","")
	return utime
	
def compareTime(nowTime,startTime):
	flag = False
	n_time = time.mktime(time.strptime(nowTime,'%Y-%m-%d %H:%M'))
	s_time = time.mktime(time.strptime(startTime,'%Y-%m-%d %H:%M'))
	if n_time >= s_time:
		flag = True
	return flag

def usage():
	print("Usage:%s [-t|-h|-d|-w] [--help=|--time=|--hours=|--days=|--weeks=]"%sys.argv[0])
	print "example1: "
	print("    %s -t \"2016-12-01 00:00\""%sys.argv[0])
	print "example2: "
	print("    %s -h 1 "%sys.argv[0])
	print "example3: "
	print("    %s -d 1 "%sys.argv[0])
	print "example4: "
	print("    %s -w 1 "%sys.argv[0])
	
def getArgs(argv):
	try:
		opts, args = getopt.getopt(argv,"t:h:d:w:",["help","time=","hours=","days=","weeks="])
	except getopt.GetoptError:
		usage()
		exit(2)
	today = datetime.datetime.today()
	startTime = today.strftime("%Y-%m-%d ") + '00:00'
	for opt, arg in opts:
		if opt in ("-help","--help"):
			usage()
			exit()
		elif opt in ("-t","--time"):
			startTime = arg
		elif opt in ("-h","--hours"):
			tmpDay = today - datetime.timedelta(hours=float(arg))
			startTime = tmpDay.strftime("%Y-%m-%d %H:%M")
		elif opt in ("-d","--days"):
			tmpDay = today - datetime.timedelta(days=float(arg))
			startTime = tmpDay.strftime("%Y-%m-%d ") + '00:00'
		elif opt in ("-w","--weeks"):
			tmpDay = today - datetime.timedelta(weeks=float(arg))
			startTime = tmpDay.strftime("%Y-%m-%d %H:%M")
		else:
			usage()
			exit(2)
	return startTime

if __name__ == '__main__':
	startTime = getArgs(sys.argv[1:])
	pageNum = 1
	res = getAllInfo(pageNum)
	dic = parsePageContent(res)
	parseWeiboComment(startTime,pageNum,dic['html'])
	totalPage = dic['totalpage'] + 1
	#print totalPage
	for pageNum in range(2,totalPage):
		#print pageNum
		res = getAllInfo(pageNum)
		dic = parsePageContent(res)
		#print dic['html']
		parseWeiboComment(startTime,pageNum,dic['html'])
