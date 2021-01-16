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

    print("In webmapper\n")

    #f, d = dataIO.getLatestCSVFile("Data/", "ctp-")

    # deltaSecsForUpdate = 24 * 3600
    # updateNow = True
    #
    # try:
    #     modTimeSinceEpoch = os.path.getmtime("/tmp/results.js")
    #     print("time since epoch:", modTimeSinceEpoch)
    #     if (time.time() - modTimeSinceEpoch) < deltaSecsForUpdate:
    #         updateNow = False
    # except OSError:
    #     updateNow = True
    #     print("No file found\n")

    if (datetime.datetime.now() - resultsCache["lastUpdate"] < datetime.timedelta(hours=6)) and not alwaysUpdate:
        print("Outputting from cache")
        outputResults(resultsCache["results"], False, [])
    else:
    #     print("Too early")
    #
    # update = updateNow or alwaysUpdate
    # print("Update is", update)
    #
    # if (not bypass) and update:
        print("Updating data\n")
        externalData["ctpFrame"] = pd.read_csv(covid19StatesDataURL)
        externalData["rtLiveFrame"] = pd.read_csv(rtLiveURL)
        externalData["popFrame"] = pd.read_csv("Data/census-state-pop-abbrev.csv")
        
        userParams["dateOfLastUpd"] = datetime.date.today().isoformat()
        userParams["consideredDate"] = datetime.date.today() - datetime.timedelta(1)
        
        dataIO.initStatePopulations(externalData["popFrame"])
        
        userParams["selectedStates"] = [k for k in list(statePopulation.keys()) if k not in statesToExclude]
        userParams["outputType"] = "js"
        userParams["jsfile"] = "/tmp/results.js"

        print("\nTabulating for states\n", userParams["selectedStates"])
        tabulateStateResults(userParams["selectedStates"])

        
    return render_template("covidmap-inline.html")


if __name__ == "__main__":
    # Used when running locally only. When deploying to Google App                                                                                            # Engine, a webserver process such as Gunicorn will serve the app. This                                                                                   # can be configured by adding an `entrypoint` to app.yaml.                                                                                                                        
    app.run(host="localhost", port=8080, debug=True)
