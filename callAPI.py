import os
import sys
import time
import json
import pandas as pd
import pymysql.cursors
from datetime import datetime
from collections import OrderedDict, defaultdict
from config import host, user, password, db, api_id, api_hash, phone_number


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
	result = None
	try:
		with connection.cursor() as cursor:
			sql = "SELECT * FROM `PeopleFlow` WHERE `time` < '" + timeString + "' ORDER BY `time` ASC"
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

	startTime = timeFormatTransfer(data[0]['time'])
	endTime = timeFormatTransfer(data[-1]['time'])

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

	with open('test.json', 'w') as outfile:
		json.dump(finalList, outfile)

	return json.dumps(finalList)


if __name__ == "__main__":
	# Use Jenkins to run this program
	# Just handle getting data and posting data

	# now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
	todayMorning = datetime.now().replace(hour=0,minute=0,second=0,microsecond=0).strftime("%Y-%m-%d %H:%M:%S")

	data = gettingData("2018-10-12 22:01:09")
	# print(data)

	postData = calculatePeopleFlow(data)
	print(postData)





