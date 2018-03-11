from flask import Flask
import requests, re, urllib
import httplib2
import os

from apiclient import discovery
import oauth2client
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

import datetime
import pytz
import json

flags = []
medcentres = [('21akti4jb49iv29jiuf0mjr5p8@group.calendar.google.com', 'Porter Brook Medical Centre', 'ChIJpZPvtGSCeUgRaWE7aMvStvg'),
              ('fduj2a3a0mdrrmtpi8en0jemsk@group.calendar.google.com', 'University Of Sheffield Health Centre', 'ChIJ_cbxtHiCeUgRK_eX8gO8cqs')]

app = Flask(__name__)

@app.route("/")
def hello2():
    return "hello"

@app.route("/p/<problem>")
def hello(problem):
    try:
        bias = 0
        r = requests.get('https://www.nhs.uk/Search/?q='+problem)
        p = re.compile("<li data-fb-result=https://www.nhs.uk/conditions/(.+?)>")
        uu = "https://www.nhs.uk/conditions/" + p.search(r.content.decode("utf-8")).group(1)
        r = requests.get(uu)
        if "pharmacist can help" in r.content.decode("utf-8"):
            bias = 1
        else:
            r = requests.get('https://www.nhs.uk/nhsengland/aboutnhsservices/pharmacists/pages/pharmacistsandchemists.aspx')
            if urllib.parse.unquote(problem.lower()) in r.content.decode("utf-8").lower():
                bias = 1
        if bias == 1:
            return "1"
        else:
            return "0"
    except:
        return "0 error"
        
@app.route("/wi/<problem>")
def wi(problem):
    try:
        bias = 0
        r = requests.get('https://www.nhs.uk/Search/?q='+problem)
        p = re.compile("<li data-fb-result=https://www.nhs.uk/conditions/(.+?)>")
        uu = "https://www.nhs.uk/conditions/" + p.search(r.content.decode("utf-8")).group(1)
        r = requests.get(uu)
        print(uu)
        if "walk-in" in r.content.decode("utf-8"):
            bias = 1
        else:
            r = requests.get('https://www.nhs.uk/NHSEngland/AboutNHSservices/Emergencyandurgentcareservices/Pages/Walk-incentresSummary.aspx')
            if urllib.parse.unquote(problem.lower()) in r.content.decode("utf-8").lower():
                bias = 1
        if bias == 1:
            return "1"
        else:
            return "0"
    except:
        return "0 error"
        
#import cal
SCOPES = 'https://www.googleapis.com/auth/calendar'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Google Calendar API Python Quickstart'

def get_credentials():
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'calendar-python-quickstart.json')

    store = oauth2client.file.Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        credentials = tools.run_flow(flow, store, {"logging_level": "DEBUG"})
        print('Storing credentials to ' + credential_path)
    return credentials


@app.route("/c/")
def freetimes():
    # fduj2a3a0mdrrmtpi8en0jemsk@group.calendar.google.com - University Health Service
    # 21akti4jb49iv29jiuf0mjr5p8@group.calendar.google.com - Upper Thorpe Medical Centre
    # for each calendar
    #    iterate through ten minute intervals
    #        if free, say so
    #    if not, say so
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('calendar', 'v3', http=http)
    
    a = []
    
    for (cal, calname, pid) in medcentres:
        print(calname)
        tz = pytz.timezone('Europe/London')
        dd = 0
        while dd < 2:
            now = datetime.datetime.now() + datetime.timedelta(days=dd)
            dd += 1
            the_datetime = tz.localize(datetime.datetime(now.year, now.month, now.day, 9, 0))
            the_datetime2 = tz.localize(datetime.datetime(now.year, now.month, now.day, 17, 0))
            body = {
                "timeMin": the_datetime.isoformat(),
                "timeMax": the_datetime2.isoformat(),
                "timeZone": 'Europe/London',
                "items": [{"id": cal}]
               }
            eventsResult = service.freebusy().query(body=body).execute()
            cal_dict = eventsResult[u'calendars']
            i = 0
            while i < len(cal_dict[cal]['busy']):
                st = datetime.datetime.strptime(cal_dict[cal]['busy'][i]["end"], "%Y-%m-%dT%H:%M:%SZ")
                try:
                    en = datetime.datetime.strptime(cal_dict[cal]['busy'][i+1]["start"], "%Y-%m-%dT%H:%M:%SZ")
                except:
                    en = the_datetime2.replace(tzinfo=None)
                j = datetime.timedelta(0)
                while st + j < en:
                    tdt = st + j
                    a.append({"name": calname, "time": tdt.strftime("%Y-%m-%dT%H:%M:%SZ"), "place_id": pid, "calid": cal})
                    j += datetime.timedelta(minutes=10)
                i += 1
    return json.dumps(a)
    
@app.route("/book/<calid>/<time>/<complaint>/")
def book(time, calid, complaint):
    name = "Souradip"
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('calendar', 'v3', http=http)
    event = {
        'summary': name + ' appointment',
        'location': '',
        'description': complaint,
        'start': {
        'dateTime': time,
        'timeZone': 'Europe/London',
        },
        'end': {
        'dateTime': (datetime.datetime.strptime(time, "%Y-%m-%dT%H:%M:%SZ") + datetime.timedelta(minutes=10)).strftime("%Y-%m-%dT%H:%M:%SZ"),
        'timeZone': 'Europe/London',
        },
        'reminders': {
        'useDefault': False,
        },
    }
    event = service.events().insert(calendarId=calid, body=event).execute()
    #return 'Event created: %s' % (event.get('htmlLink'))
    locname = ""
    for a in medcentres:
        if a[0] == calid:
            locname = a[1]
    return "{\"status\": \"done\", \"loc\": \""+locname+"\"}"

        
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response
    
if __name__ == '__main__':
    app.run(threaded=True)