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


app = Flask(__name__)

@app.route("/")
def hello2():
    return "hello"

@app.route("/p/<problem>")
def hello(problem):
    r = requests.get('https://www.nhs.uk/Search/?q='+problem)
    p = re.compile("<li data-fb-result=https://www.nhs.uk/conditions/(.+?)>")
    uu = "https://www.nhs.uk/conditions/" + p.search(r.content.decode("utf-8")).group(1)
    r = requests.get(uu)
    if "pharmacist can help" in r.content.decode("utf-8"):
        return "1"
    else:
        return "0"
        
@app.route("/wi/<problem>")
def wi(problem):
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
        
#import cal
SCOPES = 'https://www.googleapis.com/auth/calendar.readonly'
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
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials

def isFree(service, cal, ts, te):
    body = {
        "timeMin": ts.isoformat(),
        "timeMax": te.isoformat(),
        "timeZone": 'Europe/London',
        "items": [{"id": cal}]
       }
    eventsResult = service.freebusy().query(body=body).execute()
    cal_dict = eventsResult[u'calendars']
    return not cal_dict[cal]['busy']
    
def getFree(cal, calname):
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('calendar', 'v3', http=http)
    a=[]
    
    tz = pytz.timezone('Europe/London')
    now = datetime.datetime.now()
    for hours in range(9, 17):
        for mins in range(0, 60, 10):
            the_datetime = tz.localize(datetime.datetime(now.year, now.month, now.day, hours, mins))
            the_datetime2 = tz.localize(datetime.datetime(now.year, now.month, now.day, hours+1, mins+9))
            if isFree(service, cal, the_datetime, the_datetime2):
                a.append({"name": calname, "time": the_datetime.strftime("%Y-%m-%dT%H:%M:%SZ")})
                
    tom = datetime.date.today() + datetime.timedelta(days=1)
    for hours in range(9, 16):
        for mins in range(0, 60, 10):
            the_datetime = tz.localize(datetime.datetime(tom.year, tom.month, tom.day, hours, mins))
            the_datetime2 = tz.localize(datetime.datetime(tom.year, tom.month, tom.day, hours+1, mins+9))
            if isFree(service, cal, the_datetime, the_datetime2):
                a.append({"name": calname, "time": the_datetime.strftime("%Y-%m-%dT%H:%M:%SZ")})
    return json.dumps(a)

@app.route("/c/")
def freetimes():
    # fduj2a3a0mdrrmtpi8en0jemsk@group.calendar.google.com - University Health Service
    # 21akti4jb49iv29jiuf0mjr5p8@group.calendar.google.com - Upper Thorpe Medical Centre
    # for each calendar
    #    iterate through ten minute intervals
    #        if free, say so
    #    if not, say so
    return getFree("21akti4jb49iv29jiuf0mjr5p8@group.calendar.google.com", "Upper Thorpe Medical Centre")
    pass

        
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response
    
if __name__ == '__main__':
    app.run(threaded=True)