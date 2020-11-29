import datetime
import matplotlib.pyplot as plt
import csv
import os
from params import *
from argparse import ArgumentParser
import urllib.request

counter = 1

SAVE = False
latexTable = False
gridOn = True

# def convertCTP(yyyymmdd):
#     return datetime.date( int(yyyymmdd[0:4]), int(yyyymmdd[4:6]), int(yyyymmdd[6:8]) )

def convert_Y_M_D(yyyy_mm_dd):
    d = yyyy_mm_dd.split("-")
    return datetime.date( int(d[0]), int(d[1]), int(d[2]) )

# def getEffRepFromData(rawRows, region, date):
#     for row in rawRows:
#         if row["region"] == region and convert_Y_M_D(row["date"]) == date:
#             return float(row["mean"])

def getEffRepFromData(rawRows, region, date):
    rtl = externalData["rtLiveFrame"]
    dateStr = date.strftime('%Y-%m-%d')
    entry = rtl.loc[(rtl.date == dateStr) & (rtl.region == region)]["mean"]
    entryValue = float(entry.to_string(index=False))
    return entryValue


# def getEntryFromCTPData(ctpRows, state, date, colKey):
#
#     daysToAvgOver = userParams["avgOverDays"]
#     lastDateInWindow = date + datetime.timedelta(days=int(daysToAvgOver/2))
#     summ=0; count = 0
#     for row in ctpRows:
#         for j in range(daysToAvgOver):
#             d = lastDateInWindow - datetime.timedelta(days=j)
#             #print("Getting data for date ", d, "for state ", state)
#             if d < convert_Y_M_D(userParams["earliestDate"]) or d > convert_Y_M_D(userParams["dateOfLastUpd"]):
#                 print("ERROR: No data for date ", d, "exiting...")
#                 exit()
#             else:
#                 if row["state"] == state and convertCTP(row["date"]) == d:
#                     if row[colKey] != "":
#                         summ += int(row[colKey])
#                         count += 1
#
#     if summ == 0: print(colKey, "for", state, "on", date, "averaged over", daysToAvgOver, "days is zero")
#     return summ/count

# def getEntryFromCTPDataALT(ctpRows, state, date, colKey):
#
#     if date < convert_Y_M_D(userParams["earliestDate"]) or date > convert_Y_M_D(userParams["dateOfLastUpd"]):
#         print("ERROR: No data for date ", date, "exiting...")
#         exit()
#     else:
#         ctp = externalData["ctpFrame"]
#         ctp["date"] = pd.to_datetime(ctp["date"], format='%Y%m%d')
#
#         #lastDateInWindow = date + datetime.timedelta(days=int(daysToAvgOver/2))
#         lastDateInWindow = date
#         summ=0; count = 0
#         for j in range(userParams["avgOverDays"]):
#             d = lastDateInWindow - datetime.timedelta(days=j)
#             entry = ctp.loc[(ctp["date"] == d) & (ctp.state == state)][colKey]
#
#             if not entry.empty:
#                 entryValue = int(float(entry.to_string(index=False)))
#                 summ += entryValue
#                 count += 1
#             else:
#                 print("Entry is empty: ", d, state, colKey)
#
#         if summ == 0: print(colKey, "for", state, "on", date, "averaged over", userParams["avgOverDays"], "days is zero")
#         return summ/count

def getEntryFromCTPData(ctpRows, state, date, colKey):

    if date < convert_Y_M_D(userParams["earliestDate"]) or date > convert_Y_M_D(userParams["dateOfLastUpd"]):
        print("ERROR: No data for date ", date, "exiting...")
        exit()
    else:
        ctp = externalData["ctpFrame"]

        #lastDateInWindow = date + datetime.timedelta(days=int(daysToAvgOver/2))
        lastDateInWindow = date
        summ=0; count = 0
        for j in range(userParams["avgOverDays"]):
            d = lastDateInWindow - datetime.timedelta(days=j)
            dInt = int(d.strftime('%Y%m%d'))
            entry = ctp.loc[(ctp.date == dInt) & (ctp.state == state)][colKey]
            if not entry.empty:
                entryValue = int(float(entry.to_string(index=False)))
                summ += entryValue
                count += 1
            else:
                print("Entry is empty: ", dInt, state, colKey)

        if summ == 0: print(colKey, "for", state, "on", date, "averaged over", userParams["avgOverDays"], "days is zero")
        return summ/count


def initStatePopulations(popRows):
    for row in popRows:
        if row["STATE"] != "0":
            statePopulation[row["STATECODE"]] = int(row["POPESTIMATE2019"])

def readData(filename, store):
    input_file = csv.DictReader(open(filename))
    for row in input_file:
        store.append(row)

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
    #os.chdir(directory)

    if update:
        updateConfirm = input("Proceeding to update data csv files. Please confirm (y/n)[n]: ")
        if updateConfirm == "y" or updateConfirm == "Y":
            print("Updating ...")
            ctpFile = directory + "ctp-" + str(datetime.date.today()) + ".csv"
            rtFile = directory + "rt-" + str(datetime.date.today()) + ".csv"
            urllib.request.urlretrieve(covid19StatesDataURL, ctpFile)
            urllib.request.urlretrieve(rtLiveURL, rtFile)
            userParams["dateOfLastUpd"] = datetime.date.today().isoformat()
        else:
            print("Use -noupdate option to use existing data files. Exiting ..")
            exit()
    else:
        dateOfLastUpd = userParams["dateOfLastUpd"]
        print("Using data pulled on ", dateOfLastUpd, "use option -updateAsof YYYY-MM-DD to change")

        ctpFile = directory + "ctp-" + str(dateOfLastUpd) + ".csv"
        rtFile = directory + "rt-" + str(dateOfLastUpd) + ".csv"

    print("Covid Tracking Project file is: ", ctpFile, "Rtlive file is: ", rtFile)

    externalData["ctpFrame"] = pd.read_csv(ctpFile)
    externalData["rtLiveFrame"] = pd.read_csv(rtFile)
    externalData["popFrame"] = pd.read_csv("Data/census-state-pop-abbrev.csv")

    # readData(ctpFile, ctpRows)
    # readData(rtFile, rtliveRows)
    readData("Data/census-state-pop-abbrev.csv", popRows)

    initStatePopulations(popRows)


def parseCLI():
    parser = ArgumentParser(description="Area- and Time-specific Infection Probability Model")

    parser.add_argument("-noupdateData", action="store_true", help="Fetch latest data from Covid tracking and rtlive sites")
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

    args = parser.parse_args()

    if args.interactive:
        return getPromptedInput()

    return args

def getPromptedInput():
    print("Prompted Input")
    exit()
    return 0