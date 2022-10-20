import requests 
from threading import Timer  
 
def setTimeout(fn, ms, *args, **kwargs): 
    t = Timer(ms / 1000., fn, args=args, kwargs=kwargs) 
    t.start() 
    return t 

writeurl = "http://localhost:5000/api/upload?key=hot&file"
readurl = "http://localhost:5000/api/key/cold"

payload={'key': 'hot'}
files=[
  ('file',('hot.jpeg',open('/Users/chenliang/Desktop/University of Toronto/Fall 2022/ECE1779/Assignements/ECE1779_Project1/backend/static/images/hot.jpeg','rb'),'image/jpeg'))
]

def writeResponse():
  return requests.request("POST", writeurl, headers={}, data=payload, files=files)
def readResponse():
  return requests.request("POST", readurl, headers={}, data={})

# 1000 ms is a maximum allowed value according to requirements 
maximumResponseTime = 1000
# 100 is a number of sent requests according to requirements 
readIterations = 20
writeIterations = 80
# 100 ms is a delay between requests according to requirements 
delay = 100
# responseTimes is an array for collecting response time values
readResponseTimes = []
writeResponseTimes = []
i = 0
j = 0

def sendWriteRequest():
  global i
  global writeResponseTimes
  res = writeResponse()
  writeResponseTimes.append(res.elapsed.total_seconds())
  if (i < writeIterations - 1):
    i = i + 1
    setTimeout(sendWriteRequest, delay)
  else:
    print(writeResponseTimes)
    return

def sendReadRequest():
  global j
  global readResponseTimes
  res = readResponse()
  readResponseTimes.append(res.elapsed.total_seconds())
  if (j < readIterations - 1):
    j = j + 1
    setTimeout(sendReadRequest, delay)
  else:
    print(readResponseTimes)
    return

sendWriteRequest()
sendReadRequest()