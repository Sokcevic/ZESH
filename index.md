# ZESH

Here you can find a documentation for this API

## Untis
### /login
- Methods: POST
- RequestBody: { "user":"...", "password":"..." }
- returns: klasseId, personId, personType, sessionId

Tries to login with the given credentials

### /table
- Methods: POST
- RequestBody: { "startDate": "20201028", "endDate":"20201028", "JSESSIONID":JSESSIONID}
- returns: timeTable

### /subjects
- Methods: POST
- RequestBody: {"JSESSIONID":JSESSIONID}
- Returns: Information about subjects (name, id, ...)

### /prepared/firstLesson
- Methods: POST
- RequestBody: {"startDate": "20201028", "endDate":"20201028", "JSESSIONID":JSESSIONID}
- returns: The time when the first lesson starts

### /prepared/timetable
- Methods: POST
- RequestBody: { "startDate": "20201028", "endDate":"20201028", "JSESSIONID":JSESSIONID}
- returns: The TimeTable with names fr the subjects instead of ids

## ÖBB

### /station
- Methods: POST
- RequestBody: { "name":"StationName", "count": 123 }
- returns:  A number of stations, equal to count, that match the StationName parameter.

### /route
- Methods: POST
- RequestBody: see /journey. To change parameters, just put the key and the new value you want to have in the postbody. The from and to parameters are necessary. The from and to parameters are supposed to have data, that is returned by /station.
- returns:  multiple routes from A to B


### /journey
- Methods: GET
- returns:  The journey json file which contains the Data send to receive route information. Here the parameters '''from''' and '''to''' are left blank. These are necessary for the programm to work so make sure to fill them in.