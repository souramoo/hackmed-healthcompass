from flask import Flask
import requests, re, urllib

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