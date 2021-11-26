from collections import defaultdict
from flask import Flask
from flask import request as postbody
import json
import requests
import markdown
import urllib.parse

app = Flask(__name__)

UNTIS_URL = 'https://{server}/WebUntis/jsonrpc.do?school={loginName}'


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
    postData["params"] = postbody.json['data']
    postData["jsonrpc"] = "2.0"
    print(postbody.json)
    print(postData)
    print(UNTIS_URL.format(server = postbody.json['server'], loginName = postbody.json['loginName']))
    r = requests.post(UNTIS_URL.format(server = postbody.json['server'], loginName = postbody.json['loginName']), data = json.dumps(postData)).json()
    if "error" in r:
        return r['error']
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
    uid = getUserID(p)
    utyp = getUserType(p)
    if uid is False or utyp is False:
        return {'error':'Your JSESSIONID is probably expired'}
    postData["params"] = { "id":uid, "type":utyp}
    if "startDate" in p.json['data']:
        postData['params']["startDate"] = p.json['data']['startDate']
    if "endDate" in p.json['data']:
        postData['params']['endDate'] = p.json['data']['endDate']
    postData["jsonrpc"] = "2.0"
    return requests.post(UNTIS_URL.format(server = postbody.json['server'], loginName = postbody.json['loginName']), data = json.dumps(postData), cookies = {"JSESSIONID": p.json['data']['JSESSIONID']}).json()

@app.route('/subjects', methods=['POST'])
def getSubjectsRoute():
    r = getSubjects(postbody)
    if "error" in r:
        return {'error':r['error']}
    return json.dumps(r['result'])

def getSubjects(p):
    postData = {}
    postData["id"] = "ID"
    postData["method"] = "getSubjects"
    postData["jsonrpc"] = "2.0"
    return requests.post(UNTIS_URL.format(server = postbody.json['server'], loginName = postbody.json['loginName']), data = json.dumps(postData), cookies = {"JSESSIONID": p.json['data']['JSESSIONID']}).json()

@app.route('/userData', methods=['POST'])
def getStudentInfo():
    return requests.get('https://neilo.webuntis.com/WebUntis/api/rest/view/v1/app/data', 
    cookies={"JSESSIONID": postbody.json['data']['JSESSIONID']}, headers={'Authorization': getBearerAuth(postbody)}).json()

def getBearerAuth(p):
    return 'Bearer ' + requests.get('https://neilo.webuntis.com/WebUntis/api/token/new', cookies = {"JSESSIONID": p.json['data']['JSESSIONID']}).text

def getUserID(p):
    r = requests.get('https://neilo.webuntis.com/WebUntis/api/rest/view/v1/app/data', 
    cookies={"JSESSIONID": p.json['data']['JSESSIONID']}, headers={'Authorization': getBearerAuth(postbody)}).json()
    if 'user' not in r:
        return False
    return r['user']['person']['id']

def getUserType(p):
    r = requests.get('https://neilo.webuntis.com/WebUntis/api/profile/general', cookies={"JSESSIONID": p.json['data']['JSESSIONID']}, headers={'accept':'application/json'}).json()
    if 'data' not in r:
        return False
    return r['data']['profile']['userRoleId']

@app.route('/search', methods=['POST'])
def searchSchoolRoute():
    return searchSchool(postbody)

def searchSchool(p):
    postData  = {"id":"wu_schulsuche-1635432671032","method":"searchSchool","params":[{"search":p.json['search']}],"jsonrpc":"2.0"}
    return requests.post('https://mobile.webuntis.com/ms/schoolquery2', json=postData).json()['result']

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
    return requests.post('https://tickets.oebb.at/api/hafas/v4/timetable', json=journey, headers={'AccessToken':ScottyLogin()}).json()
    
@app.route('/journey', methods=['GET'])
def showJourney():
    return json.loads(open('Journey.json', 'r').read())

# ---------------------------------------------------------------------------------------------------------------------------------------------#

@app.route('/prepared/firstLesson', methods=['POST'])
def getLesson():
    table = getTable(postbody)
    
    if "error" in table:
        return table['error']
    if len(table) == 0:
        return {'error':'You probably don\'t have school that day!' }

    erg = defaultdict(list)
    for t in table['result']: 
        print(t)
        if('code' in t):
            if(t['code'] == 'cancelled'): 
                continue  
        erg[t['date']].append(t['startTime'])
    for k, v in erg.items():
        erg[k] = min(v)
    return erg

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
    app.run(host='0.0.0.0',port=5000, threaded = True, debug=True)