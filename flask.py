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
