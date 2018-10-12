import sys
import time
import json
from config import host, user, password, db
import pymysql.cursors
from watchdog.observers import Observer
from watchdog.events import *


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
		print("got connection~")
		return connection

	def disconect(self, connection):
		connection.close()


	def uploadData(self, data):
		connection = self.connectting()
		
		# Expected that data is a list.
		try:
			for people in data:
				try:
					with connection.cursor() as cursor:
						sql = "INSERT INTO `PeopleFlow` (`peopleID`, `state`, `time`, `frameNumber`) VALUES (%s, %s, %s, %s )"
						cursor.execute(sql, (people["ID"],people["inOut"], people["time"], people["frameNumber"]))
					connection.commit()
				except:
					print("stored fail...")
				finally:
					pass

		except TypeError as e:
			print(e)

		print("Done with stored")
		self.disconect(connection)


	def on_created(self, event):
		if not event.is_directory:
			# if there is a file created
			with open(event.src_path) as f:
				data = json.load(f)

			self.uploadData(data)




if __name__ == "__main__":
	try:
		observer = Observer()
		event_handler = FileEventHandler()
		observer.schedule(event_handler, sys.argv[1], True)
		observer.start()

		try:
			while True:
				time.sleep(1)
		except KeyboardInterrupt:
			observer.stop()
		observer.join()
	except IndexError:
		print("Please enter path.")