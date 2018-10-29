import os
import sys
import time
import json
import pymysql.cursors
from datetime import datetime
from config import host, user, password, db, api_id, api_hash, phone_number
from watchdog.observers import Observer
from watchdog.events import *
from telethon import TelegramClient, events, sync

second = 0
client = TelegramClient('session_name', api_id, api_hash)

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


	def uploadData(self, data, outputTume):
		global second
		connection = self.connectting()

		
		# Expected that data is a list.
		try:
			if( data ):
				for people in data:
					try:
						with connection.cursor() as cursor:
							sql = "INSERT INTO `PeopleFlow` (`peopleID`, `state`, `time`, `frameNumber`, `outputTime`) VALUES (%s, %s, %s, %s, %s )"
							cursor.execute(sql, (people["ID"],people["inOut"], self.timeStringTransfer(people["time"]), people["frameNumber"], self.timeStringTransfer(outputTume)))
						connection.commit()
					except:
						print("stored fail...")
					finally:
						pass
				print("Done with stored...共 {} 筆資料...[{}]".format(len(data), self.timeStringTransfer(outputTume)))
			else:
				print("空資料...[{}]".format(self.timeStringTransfer(outputTume)))

		except TypeError as e:
			print(e)
		finally:
			pass
			

		self.disconect(connection)
		second = 0


	def on_created(self, event):
		if not event.is_directory:
			# if there is a file created
			# avoid the json format error cuz read before write.
			time.sleep(5)
			try:
				with open(event.src_path) as f:
					data = json.load(f)

				filename = os.path.basename(event.src_path).replace(".json", "")

				self.uploadData(data, filename)
			except ValueError:
				print("Something like json format is wrong...({})".format(event.src_path))



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