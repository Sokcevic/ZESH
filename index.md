# ZESH 

Here you can find a documentation for this API

## /login
- Methods: POST
- RequestBody: { "user":"...", "password":"..." }
- returns: klasseId, personId, personType, sessionId

Tries to login with the given credentials

## /table
- Methods: POST
- RequestBody: { "id":personId, "type":personType, "JSESSIONID":JSESSIONID}
- returns: timeTable

## /subjects
- Methods: POST
- RequestBody: {"JSESSIONID":JSESSIONID}
- Returns: Information about subjects (name, id, ...)

## /prepared/firstLesson
- Methods: POST
- RequestBody: { "id":personId, "type":personType, "JSESSIONID":JSESSIONID}
- returns: The time when the first lesson starts

## /prepared/timeTable
- Methods: POST
- RequestBody: { "id":personId, "type":personType, "JSESSIONID":JSESSIONID}
- returns: The TimeTable with names fr the subjects instead of ids