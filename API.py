from flask import Flask
from flask import request as postbody
import json
import requests
import markdown
import urllib.parse

app = Flask(__name__)

UNTIS_URL = 'https://neilo.webuntis.com/WebUntis/jsonrpc.do?school=Spengergasse'


@app.route("/")
def index():
    readme_file = open("index.md", "r")
    md_template_string = markdown.markdown(
        readme_file.read(), extensions=["fenced_code"]
    )

    return md_template_string

@app.route('/login', methods=['POST'])
def login():
    postData = {}
    postData["id"] = "ID"
    postData["method"] = "authenticate"
    postData["params"] = postbody.json
    postData["jsonrpc"] = "2.0"
    print(postbody.json)
    r = requests.post(UNTIS_URL, data = json.dumps(postData)).json()
    if "error" in r:
        return {}
    return json.dumps(r['result'])

@app.route('/table', methods=['POST'])
def getTableRoute():
    r = getTable(postbody)
    if "error" in r:
        return json.dumps(r['error'])
    return json.dumps(r['result'])

def getTable(p):
    postData = {}
    postData["id"] = "ID"
    postData["method"] = "getTimetable"
    postData["params"] = { "id":p.json['id'], "type":p.json['type']}
    postData["jsonrpc"] = "2.0"
    return requests.post(UNTIS_URL, data = json.dumps(postData), cookies = {"JSESSIONID": p.json['JSESSIONID']}).json()

@app.route('/subjects', methods=['POST'])
def getSubjectsRoute():
    r = getSubjects(postbody)
    if "error" in r:
        return str(r['error'])
    return json.dumps(r['result'])

def getSubjects(p):
    postData = {}
    postData["id"] = "ID"
    postData["method"] = "getSubjects"
    postData["jsonrpc"] = "2.0"
    return requests.post(UNTIS_URL, data = json.dumps(postData), cookies = {"JSESSIONID": p.json['JSESSIONID']}).json()

# ---------------------------------------------------------------------------------------------------------------------------------------------#

def ScottyLogin():
    return requests.get('https://tickets.oebb.at/api/domain/v3/init').json()['accessToken']

@app.route('/station', methods=['POST'])
def getStation():
    return json.dumps(requests.get('https://tickets.oebb.at/api/hafas/v1/stations?' + urllib.parse.urlencode(postbody.json), headers={'AccessToken':ScottyLogin()}).json())

@app.route('/route', methods=['POST'])
def getRoute():
    journey = json.loads(open('Journey.json', 'r').read())
    for a,b in postbody.json.items():
        journey[a] = b
    # print(type(postbody.json['from']['number']))
    # journey['from'] = postbody.json['from']
    # journey['to'] = postbody.json['to']
    return requests.post('https://tickets.oebb.at/api/hafas/v4/timetable', json=journey, headers={'AccessToken':ScottyLogin()}).json()
    
@app.route('/journey', methods=['GET'])
def showJourney():
    return json.loads(open('Journey.json', 'r').read())

# ---------------------------------------------------------------------------------------------------------------------------------------------#

@app.route('/prepared/firstLesson', methods=['POST'])
def getLesson():
    table = getTable(postbody)
    startTime = min(t['startTime'] for t in table['result'] )
    return {'startTime': startTime}

@app.route('/prepared/timetable', methods=['POST'])
def getprepedtable():
    table = getTable(postbody)
    subjects = getSubjects(postbody)

    if "error" in table:
        return table['error']
    if "error" in subjects:
        return subjects['error']

    table = table['result']
    subjects = subjects['result']

    for lesson in table:
        lesson['startTime'] = str(lesson['startTime']//100) + ':' + str(lesson['startTime']%100)
        lesson['endTime'] = str(lesson['endTime']//100) + ':' + str(lesson['endTime']%100)
        lesson['su'][0]['name'] = list(filter(lambda x: x['id'] == lesson['su'][0]['id'], subjects))[0]['name']

    return json.dumps(table)

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=5000, threaded = True)