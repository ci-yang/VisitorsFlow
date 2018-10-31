import os
import sys
import time
import json
import socket
import logging
import pymysql.cursors
from datetime import datetime
from config import host, user, password, db, api_id, api_hash, phone_number
from watchdog.observers import Observer
from watchdog.events import *
from telethon import TelegramClient, events, sync

# make dir named log to store log files
if not os.path.exists("log"):
    os.makedirs("log")

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    datefmt='%m-%d %H:%M',
                    handlers = [logging.FileHandler('log/' + datetime.now().strftime("%Y%m%d%H%M%S")+'.log', 'w', 'utf-8'),])


logger = logging.getLogger('peopleFlow')


second = 0
client = TelegramClient('session_name', api_id, api_hash)
ip = socket.gethostbyname(socket.gethostname())
ipTail = ip.split('.')[-1]

dataList = []		# Stored the fail data result in cutting network.

class FileEventHandler(FileSystemEventHandler):
	def __init__(self):
		FileSystemEventHandler.__init__(self)

	def connectting(self):
		connection = pymysql.connect(host=host,
								user=user,
								password=password,
								db=db,
								charset='utf8',
								cursorclass=pymysql.cursors.DictCursor)
		# print("got connection~")
		return connection

	def disconect(self, connection):
		connection.close()

	def timeStringTransfer(self, timeString):
		# YYYYMMDDhhmmss -> YYYY-MM-DD hh:mm:ss
		# print(datetime.strptime(timeString, "%Y%m%d%H%M%S").strftime("%Y-%m-%d %H:%M:%S"))
		
		return datetime.strptime(timeString, "%Y%m%d%H%M%S").strftime("%Y-%m-%d %H:%M:%S")


	def uploadData(self, data, outputTime):
		global second
		connection = self.connectting()

		
		# Expected that data is a list.
		try:
			if( data ):
				for people in data:
					try:
						with connection.cursor() as cursor:
							sql = "INSERT INTO `PeopleFlow` (`peopleID`, `state`, `time`, `frameNumber`, `outputTime`, `ip`) VALUES (%s, %s, %s, %s, %s, %s )"
							cursor.execute(sql, (people["ID"],people["inOut"], self.timeStringTransfer(people["time"]), people["frameNumber"], self.timeStringTransfer(outputTime), ipTail))
						connection.commit()
					except:
						logger.error("意外的沒存到...")
					finally:
						pass
				print("Done with stored...共 {} 筆資料...[{}]".format(len(data), self.timeStringTransfer(outputTime)))
				logger.info("Done with stored...共 {} 筆資料...[{}]".format(len(data), self.timeStringTransfer(outputTime)))
			else:
				print("空資料...[{}]".format(self.timeStringTransfer(outputTime)))
				logger.warning("空資料...[{}]".format(self.timeStringTransfer(outputTime)))

		except TypeError as e:
			print(e)
		finally:
			pass
			

		self.disconect(connection)
		second = 0

	def reUploadData(self):	# 恢復網路後重新上傳
		global dataList
		connection = self.connectting()

		
		# Expected that data is a list.
		try:
			for people in dataList:
				try:
					with connection.cursor() as cursor:
						sql = "INSERT INTO `PeopleFlow` (`peopleID`, `state`, `time`, `frameNumber`, `outputTime`, `ip`) VALUES (%s, %s, %s, %s, %s, %s )"
						cursor.execute(sql, (people["ID"],people["inOut"], self.timeStringTransfer(people["time"]), people["frameNumber"], self.timeStringTransfer(people["outputTime"]), ipTail))
					connection.commit()
				except:
					logger.error("意外的沒存到...")
				finally:
					pass
			print("結束補傳...共 {} 筆資料".format(len(dataList)))
			logger.info("結束補傳...共 {} 筆資料".format(len(dataList)))
			dataList = []

		except TypeError as e:
			print(e)
		finally:
			pass
			

		self.disconect(connection)


	def on_created(self, event):
		global second, dataList
		if not event.is_directory:
			# if there is a file created
			# avoid the json format error cuz read before write.
			time.sleep(5)
			try:
				with open(event.src_path) as f:
					data = json.load(f)

				filename = os.path.basename(event.src_path).replace(".json", "")

				try:
					self.uploadData(data, filename)

					if(dataList):
						logger.info("網路已恢復...[{}]".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
						self.reUploadData()
				except pymysql.OperationalError as e:	# 斷網時
					second = 400
					for people in data:
						people['outputTime'] = filename
						dataList.append(people)
					logger.error("斷網中...({} 筆資料進暫存)...[{}]".format(len(data), datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
					print(e)
					# print("dataList: ", dataList)

			except ValueError:
				print("Something like json format is wrong...({})".format(event.src_path))
				logger.error("Something like json format is wrong...({})".format(event.src_path))



if __name__ == "__main__":
	try:
		client.connect()
		if not client.is_user_authorized():
		    client.send_code_request(phone_number)
		    me = client.sign_in(phone_number, input('Enter code: '))

		observer = Observer()
		event_handler = FileEventHandler()
		observer.schedule(event_handler, sys.argv[1], True)
		observer.start()
		print("開始偵測...")

		try:
			while True:
				time.sleep(1)
				second = second + 1
				# if(second < 310):
				#	print(second)
				if(second == 310):
					print("已經五分鐘沒有資料了，快去查看一下吧 ",  datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
					client.send_message('me', "已經五分鐘沒有資料了，快去查看一下吧 " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
		except KeyboardInterrupt:
			observer.stop()
		observer.join()
	except IndexError:
		print("Please enter path.")
		print("EX: python uploadData.py [folder path]")