from flask import Flask
import requests, re

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
    r = requests.get('https://www.nhs.uk/Search/?q='+problem)
    p = re.compile("<li data-fb-result=https://www.nhs.uk/conditions/(.+?)>")
    uu = "https://www.nhs.uk/conditions/" + p.search(r.content.decode("utf-8")).group(1)
    r = requests.get(uu)
    if "walk-in centre" in r.content.decode("utf-8"):
        return "1"
    else:
        return "0"
        
def is_free(ts, te):
    pass
        
@app.route("/c/")
def freetimes():
    # fduj2a3a0mdrrmtpi8en0jemsk@group.calendar.google.com - University Health Service
    # 21akti4jb49iv29jiuf0mjr5p8@group.calendar.google.com - Upper Thorpe Medical Centre
    # for each calendar
    #    iterate through ten minute intervals
    #        if free, say so
    #    if not, say so
    pass

        
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response
    
if __name__ == '__main__':
    app.run(threaded=True)