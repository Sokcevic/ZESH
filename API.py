from flask import Flask
from flask import request as postbody
import json
import requests
import os

app = Flask(__name__)

REQUEST_URL = 'https://neilo.webuntis.com/WebUntis/jsonrpc.do?school=Spengergasse'
sessionId = ''
klasseId = ''
personId = ''
personType = ''


@app.route('/login', methods=['POST'])
def login():
    postData = {}
    postData["id"] = "ID"
    postData["method"] = "authenticate"
    postData["params"] = postbody.json
    postData["jsonrpc"] = "2.0"
    r = requests.post(REQUEST_URL, data = json.dumps(postData)).json()
    global sessionId
    sessionId = {'JSESSIONID':r['result']['sessionId']}
    print(sessionId)
    global klasseId
    klasseId = r['result']['klasseId']
    global personId
    personId = r['result']['personId']
    global personType
    personType = r['result']['personType']
    return r

@app.route('/table', methods=['GET'])
def getTable():
    global personType
    global personId
    postData = {}
    postData["id"] = "ID"
    postData["method"] = "getTimetable"
    postData["params"] = { "id":personId, "type":personType}
    postData["jsonrpc"] = "2.0"
    print(10 * '-')
    print(sessionId)
    print(10 * '-')
    print(json.dumps(postData))
    print(10 * '-')
    return requests.post(REQUEST_URL, data = json.dumps(postData), cookies = sessionId).json()

@app.route('/subjects', methods=['GET'])
def getSubjects():
    postData = {}
    postData["id"] = "ID"
    postData["method"] = "getSubjects"
    postData["jsonrpc"] = "2.0"
    return requests.post(REQUEST_URL, data = json.dumps(postData), cookies = sessionId).json()

@app.route('/prepared/firstLesson', methods=['GET'])
def getLesson():
    table = getTable()
    startTime = min(t['startTime'] for t in table['result'] )
    return {'startTime': startTime}

@app.route('/prepared/timetable', methods=['GET'])
def getprepedtable():
    table = getTable()
    table = table['result']
    subjects = getSubjects()['result']
    
    for lesson in table:
        print(lesson['su'][0]['id'])
        lesson['startTime'] = str(lesson['startTime']//100) + ':' + str(lesson['startTime']%100)
        lesson['endTime'] = str(lesson['endTime']//100) + ':' + str(lesson['endTime']%100)
        lesson['su'][0]['name'] = list(filter(lambda x: x['id'] == lesson['su'][0]['id'], subjects))[0]['name']

    return str(table)

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=5000, threaded = True)