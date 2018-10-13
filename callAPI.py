import os
import sys
import time
import json
import pymysql.cursors
from datetime import datetime
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
	#try:
	with connection.cursor() as cursor:
		sql = "SELECT * FROM `PeopleFlow` WHERE `time` < '" + timeString + "'"
		cursor.execute(sql)
		result = cursor.fetchall()

	connection.commit()
	#except:
	print("Getting fail...")
	#finally:
	disconect(connection)

	return result



if __name__ == "__main__":
	# Use Jenkins to run this program
	# Just handle getting data and posting data

	# now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
	todayMorning = datetime.now().replace(hour=0,minute=0,second=0,microsecond=0).strftime("%Y-%m-%d %H:%M:%S")

	data = gettingData("2018-10-12 22:01:09")
	print(data)



