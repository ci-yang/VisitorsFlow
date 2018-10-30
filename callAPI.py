import os
import sys
import time
import json
import logging
import requests
import pandas as pd
import pymysql.cursors
from datetime import datetime, timedelta
from collections import OrderedDict, defaultdict
from config import host, user, password, db, api_id, api_hash, phone_number

if not os.path.exists("log"):
    os.makedirs("log")

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    datefmt='%m-%d %H:%M',
                    handlers = [logging.FileHandler('log/callAPI.log', 'w', 'utf-8'),])

logger = logging.getLogger('peopleFlow')

def connectting():
	connection = pymysql.connect(host=host,
							user=user,
							password=password,
							db=db,
							charset='utf8',
							cursorclass=pymysql.cursors.DictCursor)
	print("got connection~")
	return connection

def disconect(connection):
	connection.close()

def gettingData(timeString):
	connection = connectting()
	todayMorning = datetime.now().replace(hour=0,minute=0,second=0,microsecond=0).strftime("%Y-%m-%d %H:%M:%S")
	result = None
	try:
		with connection.cursor() as cursor:
			sql = "SELECT * FROM `PeopleFlow` WHERE `time` <= '" + timeString + "' and `time` >= '" + todayMorning + "' ORDER BY `time` ASC"
			cursor.execute(sql)
			result = cursor.fetchall()

		connection.commit()
	except:
		print("Getting fail...")
	finally:
		disconect(connection)

	return result

def timeFormatTransfer(time):
	# transfer the time format to the request of API.

	# print(datetime.strptime(time, "%Y-%m-%d %H:%M:%S").strftime("%Y%m%d%H%M%S"))

	return datetime.strptime(time, "%Y-%m-%d %H:%M:%S").strftime("%Y%m%d%H%M%S")



def calculatePeopleFlow(data):
	# Use data to calculate the total in and out people, formating the data to match the API.
	countObj = { "SSID": "SS-007", "TagType": "Count", "TagID": "901", "TagValue": "", "StartTime": "", "EndTime": "" }
	countAccuInObj = { "SSID": "SS-007", "TagType": "CountAccuIn", "TagID": "902", "TagValue": "", "StartTime": "", "EndTime": "" }
	countAccuOuntObj = { "SSID": "SS-007", "TagType": "CountAccuOut", "TagID": "903", "TagValue": "", "StartTime": "", "EndTime": "" }

	#startTime = timeFormatTransfer(data[0]['time'])
	#endTime = timeFormatTransfer(data[-1]['time'])
	
	# default 5 minutes
	startTime = (datetime.now()- timedelta(seconds=300)).strftime("%Y-%m-%d %H:%M:%S")
	endTime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

	df = pd.DataFrame(data)
	# people who is getting in the place.
	getInPeople = df[df["state"] == 0].to_dict('records', into=defaultdict(list))
	getInPeopleCount = len(getInPeople)
	countAccuInObj['TagValue'] = str(getInPeopleCount)
	countAccuInObj['StartTime'] = startTime
	countAccuInObj['EndTime'] = endTime

	# people who is getting out the place.
	getOutPeople = df[df["state"] == 1].to_dict('records', into=defaultdict(list))
	getOutPeopleCount = len(getOutPeople)
	countAccuOuntObj['TagValue'] = str(getOutPeopleCount)
	countAccuOuntObj['StartTime'] = startTime
	countAccuOuntObj['EndTime'] = endTime

	# people who is stay in the place
	stayPeopleCount = getInPeopleCount - getOutPeopleCount if (getInPeopleCount - getOutPeopleCount) >= 0 else 0
	countObj['TagValue'] = str(stayPeopleCount)
	countObj['StartTime'] = startTime
	countObj['EndTime'] = endTime
	
	finalList = [countObj, countAccuInObj, countAccuOuntObj]


	return json.dumps(finalList)

def callingAPI(postData):
	url = "http://210.65.129.47:8008/FloraIOCAPI/reportParkPeopleFlow"
	res = requests.post(url, data=postData)
	res.encoding = 'utf-8'
	# res.encoding = 'utf-8-sig'	# for windows
	print(res.json())
	logger.info("state: {}...[{}]".format(res.json(), datetime.now().strftime("%Y-%m-%d %H:%M:%S")))


if __name__ == "__main__":
	# Use Jenkins to run this program
	# Just handle getting data and posting data

	now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
	# todayMorning = datetime.now().replace(hour=0,minute=0,second=0,microsecond=0).strftime("%Y-%m-%d %H:%M:%S")

	data = gettingData(now)
	# print(data)

	if(data):
		postData = calculatePeopleFlow(data)
		print(postData)
		logger.info("Data: {}".format(postData))

		callingAPI(postData)
	
	else:
		print("No Data")
		logger.error("No Data...[{}]".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S")))





