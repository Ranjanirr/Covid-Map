from flask import Flask, render_template
from studies import *
import time
import os
# If `entrypoint` is not defined in app.yaml, App Engine will look for an app                                                                             # called `app` in `main.py`.                                                                                                                                                          
app = Flask(__name__, static_folder="/tmp")
#app = Flask(__name__)                                                                                                                                                                
bypass=False
alwaysUpdate=False

@app.route("/", methods=["GET"])
def webmapper():

    print("Cached time is", resultsCache["lastUpdate"])
    print("Time now is", datetime.datetime.now())
    if (datetime.datetime.now() - resultsCache["lastUpdate"] < datetime.timedelta(hours=24)) and not alwaysUpdate:
        print("Outputting from cache")
        userParams["outputType"] = "js"
        outputResults(resultsCache["results"], False, [])
    else:
        print("Updating data\n")
        externalData["ctpFrame"] = pd.read_csv(covid19StatesDataURL)
        externalData["rtLiveFrame"] = pd.read_csv(rtLiveURL)
        externalData["popFrame"] = pd.read_csv("Data/census-state-pop-abbrev.csv")

        print("Finished updating data, time now is", datetime.datetime.now())
        
        userParams["dateOfLastUpd"] = datetime.date.today().isoformat()
        userParams["consideredDate"] = datetime.date.today() - datetime.timedelta(1)
        
        dataIO.initStatePopulations(externalData["popFrame"])
        
        userParams["selectedStates"] = [k for k in list(statePopulation.keys()) if k not in statesToExclude]
        userParams["outputType"] = "js"
        userParams["jsfile"] = "/tmp/results.js"

        print("\nTabulating for states\n", userParams["selectedStates"])
        tabulateStateResults(userParams["selectedStates"])

        print("Finished tabulating, time now is", datetime.datetime.now())

        
    return render_template("covidmap-inline.html")


if __name__ == "__main__":
    # Used when running locally only. When deploying to Google App                                                                                            # Engine, a webserver process such as Gunicorn will serve the app. This                                                                                   # can be configured by adding an `entrypoint` to app.yaml.                                                                                                                        
    app.run(host="localhost", port=8080, debug=True)
    print("Finished app run, time now is", datetime.datetime.now())
