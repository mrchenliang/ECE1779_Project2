import requests
from concurrent.futures import ThreadPoolExecutor

writeurl = "http://localhost:5000/api/upload?key=hot&file"
readurl = "http://localhost:5000/api/key/cold"

payload = {'key': 'hot'}
files = [
    ('file', ('hot.jpeg', open(
        '/Users/chenliang/Desktop/University of Toronto/Fall 2022/ECE1779/Assignements/ECE1779_Project1/backend/static/images/hot.jpeg',
        'rb'), 'image/jpeg'))
]


def writeResponse(url):
    return requests.post(url, headers={}, data=payload, files=files)


def readResponse(readurl):
    return requests.post(readurl, headers={}, data={})


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

list_of_write_urls = [writeurl] * writeIterations
list_of_read_urls = [readurl] * readIterations

with ThreadPoolExecutor(max_workers=writeIterations) as pool:
    writeResponseList = list(pool.map(writeResponse, list_of_write_urls))
    for response in writeResponseList:
        writeResponseTimes.append(response.elapsed.total_seconds())
    print('write')
    print(writeResponseTimes)

with ThreadPoolExecutor(max_workers=readIterations) as pool:
    readResponseList = list(pool.map(readResponse, list_of_read_urls))
    for response in readResponseList:
        readResponseTimes.append(response.elapsed.total_seconds())
    print('read')
    print(readResponseTimes)
