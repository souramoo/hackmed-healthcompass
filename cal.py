from __future__ import print_function
import httplib2
import os

from apiclient import discovery
import oauth2client
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

import datetime, time
import pytz
import json

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None
    
print(flags)

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/calendar-python-quickstart.json
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
    print(cal_dict[cal])
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
            the_datetime = tz.localize(datetime.datetime(now.year, now.month, now.day, hours, mins+1))
            the_datetime2 = tz.localize(datetime.datetime(now.year, now.month, now.day, hours+1, mins+9))
            if isFree(service, cal, the_datetime, the_datetime2):
                a.append({"name": calname, "time": the_datetime.strftime("%Y-%m-%dT%H:%M:%SZ")})
                
    tom = datetime.date.today() + datetime.timedelta(days=1)
    for hours in range(9, 16):
        for mins in range(0, 60, 10):
            the_datetime = tz.localize(datetime.datetime(tom.year, tom.month, tom.day, hours, mins+1))
            the_datetime2 = tz.localize(datetime.datetime(tom.year, tom.month, tom.day, hours+1, mins+9))
            if isFree(service, cal, the_datetime, the_datetime2):
                a.append({"name": calname, "time": the_datetime.strftime("%Y-%m-%dT%H:%M:%SZ")})
    return json.dumps(a)

    
medcentres = [('21akti4jb49iv29jiuf0mjr5p8@group.calendar.google.com', 'Porter Brook Medical Centre', 'ChIJpZPvtGSCeUgRaWE7aMvStvg'),
              ('fduj2a3a0mdrrmtpi8en0jemsk@group.calendar.google.com', 'University Of Sheffield Health Centre', 'ChIJ_cbxtHiCeUgRK_eX8gO8cqs')]


def triggerCall():
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('calendar', 'v3', http=http)
    
    a = []
    
    for (cal, calname, pid) in medcentres:
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
                    callPeopleAbout({"name": calname, "time": tdt.strftime("%Y-%m-%dT%H:%M:%SZ"), "place_id": pid, "calid": cal})
                    # instantiate call
                    return
                    j += datetime.timedelta(minutes=10)
                i += 1


import sqlite3                
def callPeopleAbout(freetime):
    conn = sqlite3.connect('alerts.db')
    c = conn.cursor()
    a = 0
    c.execute('SELECT * FROM alerts')
    for row in c.fetchall():
        accepted = False
        c.execute("DELETE FROM alerts WHERE id="+str(row[0]))
        # call, do they accept?
        if accepted:
            # add to calendar
            name = "Souradip"
            credentials = get_credentials()
            http = credentials.authorize(httplib2.Http())
            service = discovery.build('calendar', 'v3', http=http)
            event = {
                'summary': name + ' appointment',
                'location': '',
                'description': row[4],
                'start': {
                'dateTime': freetime['time'],
                'timeZone': 'Europe/London',
                },
                'end': {
                'dateTime': (datetime.datetime.strptime(freetime['time'], "%Y-%m-%dT%H:%M:%SZ") + datetime.timedelta(minutes=10)).strftime("%Y-%m-%dT%H:%M:%SZ"),
                'timeZone': 'Europe/London',
                },
                'reminders': {
                'useDefault': False,
                },
            }
            event = service.events().insert(calendarId=freetime['calid'], body=event).execute()
    conn.commit()
    conn.close()
    pass

import time
def main():
    while True:
        triggerCall()
        time.sleep(5)
    
""" 
def main():
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('calendar', 'v3', http=http)
    
    cal = '21akti4jb49iv29jiuf0mjr5p8@group.calendar.google.com'
    calname = ''
    pid = ''
    
    tz = pytz.timezone('Europe/London')
    now = datetime.datetime.now() + datetime.timedelta(days=1)
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
    a = []
    while i < len(cal_dict[cal]['busy']):
        st = datetime.datetime.strptime(cal_dict[cal]['busy'][i]["end"], "%Y-%m-%dT%H:%M:%SZ")
        #print(st)
        try:
            en = datetime.datetime.strptime(cal_dict[cal]['busy'][i+1]["start"], "%Y-%m-%dT%H:%M:%SZ")
        except:
            en = the_datetime2.replace(tzinfo=None)
        j = datetime.timedelta(0)
        #print(en)
        while st + j < en:
            tdt = st + j
            a.append({"name": calname, "time": tdt.strftime("%Y-%m-%dT%H:%M:%SZ"), "place_id": pid})
            #print(a)
            j += datetime.timedelta(minutes=10)
            #print(j)
        i += 1
    print(a)
    #    print("today"+str(hours)+":"+str(mins))
"""    

if __name__ == '__main__':
    main()