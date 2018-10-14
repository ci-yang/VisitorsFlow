# VisitorsFlow
The visitors flow python program that handle data processing and storing.



This project is including two program. Upload and Calling API.



## How To Use

#### Prepare

create a new file named config.py



```python
host = "Your host IP"
user = "your db user name"
password = "your db password"
db = "your db name"
api_id = 12345   # your telegram app api id
api_hash = 'xxxxxx'	# your telegram app api hash
phone_number = '+886012312312'	# your telegram phone number
```





#### Step1: install package

```bash
$ pip install -r requirements.txt
```



#### Step2: Start upload.py to watch specific folder



```bash
$ python uploadData.py
```



> Note: It may requests telegram Auth code, just enter it and go on.



#### Step3: Schedule the callAPI.py



排程每五分鐘執行 callAPI.py，程式會自行計算資料並 POST 資料至官方 API 位址



> Note: 請注意執行程式的 IP 必須為官方已解鎖之 IP



```bash
$ python callAPI.py
```







## Upload program



#### Flow:

1. Watching on folder
2. if the new json come in, handle it.
3. Store the content of the json into database
4. Use telegram to send a message if errors occur



#### Timer

程式執行時開始計時，有新檔案進入受監視資料夾時計時歸零，否則當計時超過指定時間（ex: 一分鐘）即以 telegram 依下列訊息進行通知

> 已經一分鐘沒有資料了，快去查看一下吧 [ recorded  time ]



## Calling API



Flow:

1. getting data from SQL by start time (today morning) and end time (current time).
2. calculate the request data format of the API.
3. calling API to post the output data



> Note: 取資料喂當日起始時間 00:00:00 及當下時間做為起始時間及結束時間，但是輸出的統計起始時間及統計結束時間為以下定義：
>
> - 統計起始時間：傳回資料的第一筆資料的時間（已照時間排序）
> - 統計結束時間：傳回資料的最後一筆資料的時間





#### API Document



```json
[
    {
        "SSID":"SS-007",
        "TagType":"Count",
        "TagID":"901",
        "TagValue":"56",
        "StartTime":"20180531101825",
        "EndTime":"20180531102825"
    },
    {
        "SSID":"SS-007",
        "TagType":"CountAccuIn",
        "TagID":"902",
        "TagValue":"72",
        "StartTime":"20180531101825",
        "EndTime":"20180531102825"
    },
    {
        "SSID":"SS-007",
        "TagType":"CountAccuOut",
        "TagID":"903",
        "TagValue":"20",
        "StartTime":"20180531101825",
        "EndTime":"20180531102825"
    }
]
```



- SSID
- TagType
  - Count
  - CountAcculn
  - CountAccuOut
- TagID: 901, 902, 903
- TagValue: Count of People who's type matches TagType
- StartTime: the calculate start time
- EndTime: the calculate end time





