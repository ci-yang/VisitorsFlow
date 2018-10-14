import sys
import json
from datetime import datetime
import threading
import time
import random

t = None

def timeFormatTransfer(time):
	# transfer the time format to the request of API.

	# print(datetime.strptime(time, "%Y-%m-%d %H:%M:%S").strftime("%Y%m%d%H%M%S"))

	return datetime.strptime(time, "%Y-%m-%d %H:%M:%S").strftime("%Y%m%d%H%M%S")


def randomGenerating(path, filename):
	count = random.randint(1, 8)		# output data count

	data = []

	for c in range(count):
		ID = random.randint(1, 99)
		state = random.randint(0, 2)
		now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
		
		obj = {
			"ID": ID,
			"inOut": state,
			"time": timeFormatTransfer(now),
			"frameNumber": random.randint(1, 5000),
			"outputTime": timeFormatTransfer(now)
		}

		data.append(obj)

	with open(path + filename + '.json', 'w') as outfile:
		json.dump(data, outfile)


def creatingJSON():
	global t
	# print(datetime.now())
	time = str(datetime.now().strftime("%Y%m%d%H%M%S"))
	randomGenerating('Files/', time)
	t = threading.Timer(2, creatingJSON)
	t.start()

# print(datetime.now())

if __name__ == "__main__":
	try:
		creatingJSON()
		time.sleep(5)
		t.cancel()
	except IndexError:
		print("Please enter path.")