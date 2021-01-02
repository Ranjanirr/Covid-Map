import matplotlib.pyplot as plt
import os
from params import *
from argparse import ArgumentParser
import urllib.request

counter = 1

SAVE = False
latexTable = False
gridOn = True

def convert_Y_M_D(yyyy_mm_dd):
    return datetime.date.fromisoformat(yyyy_mm_dd)

def getEffRepFromData(region, date):
    rtl = externalData["rtLiveFrame"]
    dateStr = date.strftime('%Y-%m-%d')
    entry = rtl.loc[(rtl.date == dateStr) & (rtl.region == region)]["mean"]
    entryValue = float(entry.to_string(index=False))
    return entryValue


def getEntryFromCTPData(state, date, colKey, avgOverDays=NULLL):

    if avgOverDays == NULLL: avgOverDays = userParams["avgOverDays"]
    if date < convert_Y_M_D(userParams["earliestDate"]) or date > convert_Y_M_D(userParams["dateOfLastUpd"]):
        print("ERROR: No data for date ", date, "exiting...")
        exit()
    else:
        ctp = externalData["ctpFrame"]

        #lastDateInWindow = date + datetime.timedelta(days=int(daysToAvgOver/2))
        lastDateInWindow = date
        summ=0; count = 0
        for j in range(avgOverDays):
            d = lastDateInWindow - datetime.timedelta(days=j)
            dInt = int(d.strftime('%Y%m%d'))
            entry = ctp.loc[(ctp.date == dInt) & (ctp.state == state)][colKey]
            if not entry.empty:
                entryValue = int(float(entry.to_string(index=False)))
                summ += entryValue
                count += 1
            else:
                print("Entry is empty: ", dInt, state, colKey)
        if summ == 0: print(colKey, "for", state, "on", date, "averaged over", avgOverDays, "days is zero")
        return summ/count

def initStatePopulations(popFrame):
    df = popFrame.loc[popFrame["STATE"] != 0]
    abbrevList = df["STATECODE"].tolist()
    popList = df["POPESTIMATE2019"].tolist()

    for i in range(len(abbrevList)):
        statePopulation[abbrevList[i]] = int(popList[i])


def showPlot(title, xlabel, ylabel):
    global counter

    plt.legend(loc="upper right")
    plt.grid(gridOn)
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)

    if SAVE:
        fileStr = title.replace(" ", "-")
        fileStr = fileStr.replace("%","")
        fileStr = fileStr.replace("=", "-")
        fileStr = fileStr.replace(":", "")

        directory = "Plots/" + str(datetime.date.today())
        os.makedirs(directory, exist_ok=True)
        os.chdir(directory)
        plt.savefig("fig" + str(counter) + "-" + fileStr + ".png", format="PNG")
        plt.clf()
        counter += 1
    else:
        plt.show()

def initData(update=False):

    directory = "Data/"
    os.makedirs(directory, exist_ok=True)

    if update:
        updateConfirm = input("Proceeding to update data csv files. Please confirm (y/n)[n]: ")

        if updateConfirm == "y" or updateConfirm == "Y":
            print("Updating ...")
            ctpPath = directory + "ctp-" + str(datetime.date.today()) + ".csv"
            rtPath = directory + "rt-" + str(datetime.date.today()) + ".csv"
            urllib.request.urlretrieve(covid19StatesDataURL, ctpPath)
            urllib.request.urlretrieve(rtLiveURL, rtPath)
            userParams["dateOfLastUpd"] = datetime.date.today().isoformat()
            userParams["consideredDate"] = datetime.date.today() - datetime.timedelta(1)
        else:
            print("OK, got it... will not pull data. For now, using latest available")

            ctpFile, ctpDate =  getLatestCSVFile(directory, "ctp-")
            rtFile, rtDate = getLatestCSVFile(directory, "rt-")
            ctpPath = directory + ctpFile
            rtPath = directory + rtFile
            userParams["dateOfLastUpd"] = ctpDate.isoformat()
            userParams["consideredDate"] = ctpDate - datetime.timedelta(1)
    else:
        dateOfLastUpd = userParams["dateOfLastUpd"]
        print("Using data pulled on ", dateOfLastUpd, "use option -updateAsof YYYY-MM-DD to change")

        ctpPath = directory + "ctp-" + str(dateOfLastUpd) + ".csv"
        rtPath = directory + "rt-" + str(dateOfLastUpd) + ".csv"

    print("Covid Tracking Project file is: ", ctpPath, "Rtlive file is: ", rtPath)

    externalData["ctpFrame"] = pd.read_csv(ctpPath)
    externalData["rtLiveFrame"] = pd.read_csv(rtPath)
    externalData["popFrame"] = pd.read_csv("Data/census-state-pop-abbrev.csv")

    initStatePopulations(externalData["popFrame"])

def getLatestCSVFile(direc, prefix):

    latestDate = datetime.date(2020, 1, 1)
    latestCSVFile = " "
    for filename in os.listdir(direc):
        if filename.endswith(".csv") and filename.startswith(prefix):
            d = filename[len(prefix) : (len(filename)-len(".csv"))]
            newDate = convert_Y_M_D(d)
            if newDate > latestDate:
                latestDate = newDate
                latestCSVFile = filename

    return latestCSVFile, latestDate


def parseCLI():
    parser = ArgumentParser(description="Area- and Time-specific Infection Probability Model")

    # parser.add_argument("-noupdateData", action="store_true", help="Fetch latest data from Covid tracking and rtlive sites")
    parser.add_argument("-updateData", action="store_true", help="Fetch latest data from Covid tracking and rtlive sites")
    parser.add_argument("-updateAsOf", type=str, help="Use data files pulled on")

    parser.add_argument("-interactive", action="store_true", help="Interactive mode with user prompted input")
    parser.add_argument("-tabulate", action="store_true", help="Tabulate methods, avg infection and cont. budg")

    parser.add_argument("-dataview", type=str,
                        help="View COVID19 data trends, space seperated quoted list of subset of (positiveIncrease, deathIncrease, percentPositive")
    parser.add_argument("-plot", type=str,
                        help="Plot studies as specified, space separated quoted list of subset of (CompareMethods, InfProb, QuarantineVsNot, ContactBudget, Evolution)")
    parser.add_argument("-js", action="store_true", help="Print out table to be readable as a Javascript object")

    parser.add_argument("-states", help="US states of interest, space separated string of state abbrev",
                        default="GA CA AZ FL")
    #parser.add_argument("-consideredDate", help="Date of interest YYYY-MM-DD", default="2020-08-12")
    parser.add_argument("-consideredDate", type=str, help="Date of interest YYYY-MM-DD")
    parser.add_argument("-history", type=int, help="Days history to plot over", default=30)
    parser.add_argument("-avgOverDays", type=int, help= "Days to average over", default=3)

    parser.add_argument("-TransmissionProbability", type=float, default=0.1)
    parser.add_argument("-NumContacts", default=100)
    parser.add_argument("-ComfortProbability", default=0.05)
    parser.add_argument("-TimeToQuar", type=int, default=lag)

    parser.add_argument("-methodsShow", action="store_true", help="For tabulating, show individual method results in addition to average")
    parser.add_argument("-perMil", action="store_true", help="Show results on a per-million population basis (note, for -t, some are already per mil)")

    args = parser.parse_args()

    if args.interactive:
        return getPromptedInput()

    return args

# def parseCLI():
#     parser = ArgumentParser(description="Area- and Time-specific Infection Probability Model")
#
#     parser.add_argument("-noupdateData", action="store_true", help="Fetch latest data from Covid tracking and rtlive sites")
#     parser.add_argument("-updateAsOf", type=str, help="Use data files pulled on")
#
#     parser.add_argument("-interactive", action="store_true", help="Interactive mode with user prompted input")
#     parser.add_argument("-tabulate", action="store_true", help="Tabulate methods, avg infection and cont. budg")
#
#     parser.add_argument("-dataview", type=str,
#                         help="View COVID19 data trends, space seperated quoted list of subset of (positiveIncrease, deathIncrease, percentPositive")
#     parser.add_argument("-plot", type=str,
#                         help="Plot studies as specified, space separated quoted list of subset of (CompareMethods, InfProb, QuarantineVsNot, ContactBudget, Evolution)")
#     parser.add_argument("-js", action="store_true", help="Print out table to be readable as a Javascript object")
#
#     parser.add_argument("-states", help="US states of interest, space separated string of state abbrev",
#                         default="GA CA AZ FL")
#     #parser.add_argument("-consideredDate", help="Date of interest YYYY-MM-DD", default="2020-08-12")
#     parser.add_argument("-consideredDate", type=str, help="Date of interest YYYY-MM-DD")
#     parser.add_argument("-history", type=int, help="Days history to plot over", default=30)
#     parser.add_argument("-avgOverDays", type=int, help= "Days to average over", default=3)
#
#     parser.add_argument("-TransmissionProbability", type=float, default=0.1)
#     parser.add_argument("-NumContacts", default=100)
#     parser.add_argument("-ComfortProbability", default=0.05)
#     parser.add_argument("-TimeToQuar", type=int, default=lag)
#
#     parser.add_argument("-methodsShow", action="store_true", help="For tabulating, show individual method results in addition to average")
#     parser.add_argument("-perMil", action="store_true", help="Show results on a per-million population basis (note, for -t, some are already per mil)")
#
#     args = parser.parse_args()
#
#     if args.interactive:
#         return getPromptedInput()
#
#     return args

def getPromptedInput():
    print("Prompted Input")
    exit()
    return 0