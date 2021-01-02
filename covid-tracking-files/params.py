import numpy as np
import datetime
import pandas as pd

covid19StatesDataURL = "https://covidtracking.com/api/v1/states/daily.csv"
rtLiveURL = "https://d14wlfuexuxgcm.cloudfront.net/covid/rt.csv"
lag = 24
IFR = 0.0064
serialInterval = 4.2

userParams = {
    "consideredDate" : datetime.date(2020, 10, 5),
    "dateOfLastUpd"  : "2020-12-29",
    "earliestDate"   : "2020-04-01",
    "selectedStates" : ["MA", "TX"],
    "focusState"     : "MA",
    "history"        : 30,
    "avgOverDays"    : 3,
    "timeToQuar"     : lag,
    "TP"             : 0.1,
    "contacts"       : 100,
    "comfortProb"    : 0.05,
    "outputType"     : "console",
    "jsfile"         : "results.js"
}

externalData = {
    "ctpFrame"       : pd.DataFrame(),
    "rtLiveFrame"    : pd.DataFrame(),
    "popFrame"        : pd.DataFrame()
}

statePopulation = {}

methodsToAvgOver = ["A", "B", "C"]
focusState = "MA"

statesToExclude = ["PR"]

mrange = np.linspace(1, 200, 50)
p_t_range = np.linspace(0.005, 0.2, 150)
tqrange = np.linspace(24, 0, 24)
pcrange = np.linspace(0.01, 0.1, 10)

NULLL = -1








