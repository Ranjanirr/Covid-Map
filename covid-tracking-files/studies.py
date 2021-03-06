
import dataIO
from collections import OrderedDict
from tabulate import tabulate
from params import *
import model
import json
if userParams["outputType"] == "console":
    import matplotlib.pyplot as plt

counter = 1
gridOn = True
SAVE = False

methColors = {
    "A": "b",
    "B": "c",
    "C": "r"
}

def tabulateStateResults(states, showMethods=False):

    results = OrderedDict()
    results["State"] = []
    if showMethods:
        for m in methodsToAvgOver: results[m+"(%)"] = []

    results["Cases"] = []; results["Deaths"] = []; results["IncidenceRate"] = []
    results["InfChance"] = []; results["ContactBudget"] = [];
    #results["ActiveInf"] = []; results["infOnDate"] = []

    diffAvg = {x:0 for x in methodsToAvgOver}
    odds = {x:0 for x in methodsToAvgOver}
    for s in states:
        results["State"].append(s)

        cumCases = dataIO.getEntryFromCTPData(s, userParams["consideredDate"], "positive")
        cumCasesPerMil = float(cumCases)*1000000.0 / statePopulation[s]
        results["Cases"].append(int(cumCasesPerMil))

        cumDeaths = dataIO.getEntryFromCTPData(s, userParams["consideredDate"], "death")
        cumDeathsPerMil = float(cumDeaths)*1000000.0 / statePopulation[s]
        results["Deaths"].append(int(cumDeathsPerMil))

        infectionsOverPast14Days = dataIO.getEntryFromCTPData(s, userParams["consideredDate"], "positiveIncrease", 14)
        incidenceRate = (1000000.0*infectionsOverPast14Days)/statePopulation[s]
        results["IncidenceRate"].append(int(incidenceRate*100)/100.0)

        oddsAvg = 100 * model.getInfecProbability(s, userParams["TP"], userParams["contacts"], methodsToAvgOver, tqspace=userParams["timeToQuar"])
        # results["InfProb(%)"].append(oddsAvg)
        results["InfChance"].append(str(int(oddsAvg*100)/100.0)+"%")

        outcome, maxM = model.getContactsBudget(s, userParams["TP"], userParams["comfortProb"], methodsToAvgOver,
                                                tqspace=userParams["timeToQuar"])
        if outcome != "NO LIMIT":
            results["ContactBudget"].append(int(maxM))
        else:
            results["ContactBudget"].append(outcome)

        # activeInfections = model.getPhi_i(s, userParams["TP"], userParams["contacts"], ["A"], tqspace=userParams["timeToQuar"])
        # results["ActiveInf"].append(ceil(activeInfections))
        #
        # infOnDate = model.getInfectionsOnRefDateInRegion(userParams["consideredDate"], s, ["A"], tqspace=lag)
        # results["infOnDate"].append(ceil(infOnDate))

        if showMethods:
            for method in methodsToAvgOver:
                odds[method] = 100 * model.getInfecProbability(s, userParams["TP"], userParams["contacts"], method)
                diffAvg[method] += (odds[method] - oddsAvg)

                results[method+"(%)"].append(odds[method])

    resultsCache["results"] = results
    resultsCache["lastUpdate"] = datetime.datetime.now()
    print("Cached results at", resultsCache["lastUpdate"])

    outputResults(results, showMethods, diffAvg)

def outputResults(results, showMethods, diffAvg):

    print("\nNOTE: CASES, DEATHS AND INCIDENCE RATE ARE PER MILLION PEOPLE")
    print("NOTE: CASES and DEATHS are CUMULATIVE; INCIDENCE RATE IS AVG CASES OVER LAST 14 DAYS\n")

    tableStr = tabulate(results, headers="keys", floatfmt=".2f")

    if userParams["outputType"] == "htmlreturn":
        webStr = tableStr.replace("\n", "<br/>")
        newWebStr = "<pre>" + webStr + "</pre>"
        return newWebStr
    else:
        print(tableStr)
        if showMethods: print("\nOver/under estimate:", ["{:.2f}".format(diffAvg[m]) for m in methodsToAvgOver])

        if userParams["outputType"] == "js":
            resStr = json.dumps(results)
            jsStr = "results = " + resStr + ";"
            with open(userParams["jsfile"], "w+") as jf:
                print("Dumping results.js into jsfile\n")
                #json.dump(results, jf)
                print(jsStr, file=jf)

            # print("\n...Confirming what I wrote:\n")
            # with open("/tmp/results.js", "r") as cf:
            #     print(cf.read())

def study_pim_vs_m_CompareMethodsForGivenRegion(region, mspace, methodList):
    for method in methodList:
        pim = model.getInfecProbability(region, userParams["TP"], mspace, method)
        plt.plot(mspace, pim, methColors[method], label="Method-" + method)

    figTitle = "Infection Prob vs contacts for " + region + ": p_t=" + str(int(userParams["TP"]*100)) + "%"
    showPlot(figTitle, "Number of contacts (m)", "Infection probability")

def study_pim_vs_p_t_CompareMethodsForGivenRegion(region, ptspace, methodList):
    for method in methodList:
        pim = model.getInfecProbability(region, ptspace, userParams["contacts"], method)
        plt.plot(ptspace, pim, methColors[method], label="Method-" + method)

    figTitle = "Infection Prob vs Transfer Prob for " + region + ": " + str(userParams["contacts"]) + " contacts"
    showPlot(figTitle, "Transfer probability (p_t)", "Infection probability")

##########

def study_pim_vs_m_CompareRegions(regionList, mspace, methods):
    for region in regionList:
        pim = model.getInfecProbability(region, userParams["TP"], mspace, methods)
        #plt.plot(mspace, pim, regColors[region], label=region)
        plt.plot(mspace, pim, label=region)

    figTitle = "Infection Probability vs contacts:"  + " p_t=" + str(int(userParams["TP"]*100)) + "%"
    showPlot(figTitle, "Number of contacts (m)", "Infection probability")

def study_pim_vs_m_Compare_p_t(region, mspace, methods, p_t_values):
    for pt in p_t_values:
        pim = model.getInfecProbability(region, pt, mspace, methods)
        plt.plot(mspace, pim, label="p_t = " + str(pt))

    figTitle = "Infection Probability vs contacts for " + region + " for different p_t values"
    showPlot(figTitle, "Number of contacts (m)", "Infection probability")

# def study_pim_vs_p_t_CompareRegions(regionList, ptspace, method):
#     for region in regionList:
#         pim = getInfecProbability(region, ptspace, userParams["contacts"], method)
#         plt.plot(ptspace, pim, regColors[region], label=region)
#
#     figTitle = "Infection Probability vs Transfer Prob " + ": " + str(userParams["contacts"]) + " contacts"
#     plt.title(figTitle)
#     plt.xlabel("Transfer probability (p_t)")
#     plt.ylabel("Infection probability")
#
#     showPlot(figTitle)

##########

def study_pim_vs_m_CompareQuar(region, mspace, methods, quarValues):
    for tq in quarValues:
        pim = model.getInfecProbability(region, userParams["TP"], mspace, methods, tq)
        plt.plot(mspace, pim, label=["No Quar" if tq==lag else "Quar aft 5d"])

    figTitle = "Infection Probability vs contacts for " + region + ": p_t=" + str(int(userParams["TP"] * 100)) + "%"
    showPlot(figTitle, "Number of contacts (m)", "Infection probability")

def study_pim_vs_tq_CompareRegions(regionList, tqspace, methods):
    for region in regionList:
        pim = model.getInfecProbability(region, userParams["TP"], userParams["contacts"], methods, tqspace)
        plt.plot(tqspace, pim, label=region)

    figTitle = "Infection Probability vs days-to-quarantine " + ": p_t=" + str(int(userParams["TP"] * 100)) + "%"
    plt.xlim(24,0)
    showPlot(figTitle, "Days to quarantine (t_q)", "Infection probability")

##########

def study_Mpc_vs_pc_CompareRegions(regionList, pcspace, methods):
    for region in regionList:
        outcome, Mpc = model.getContactsBudget(region, userParams["TP"], pcspace, methods)
        if outcome != "NO LIMIT":
            plt.plot(pcspace, Mpc, label=region)
        else:
            print("Contact budget not limited for", region)

    figTitle = "Contacts budget vs comfort probability " + ": p_t=" + str(int(userParams["TP"] * 100)) + "%"
    showPlot(figTitle, "Comfort probability (p_c)", "Contacts budget")

def study_Mpc_vs_p_t_ComparePc(region, ptspace, methods, pcValues):
    for pc in pcValues:
        outcome, Mpc = model.getContactsBudget(region, ptspace, pc, methods)
        if outcome != "NO LIMIT":
            plt.plot(ptspace, Mpc, label="p_c="+str(pc))
        else:
            print("Contact budget not limited for", region)

    figTitle = "Contacts budget vs transfer probability for " + region
    showPlot(figTitle, "Transfer probability (p_t)", "Contacts budget")

##########

def study_pim_vs_m_compareDays(region, mspace, methods, dateValues):
    for date in dateValues:
        pim = model.getInfecProbability(region, userParams["TP"], mspace, methods, userParams["timeToQuar"], date)
        plt.plot(mspace, pim, label=date)

    figTitle = "Infection Probability vs contacts for " + region + ": p_t=" + str(int(userParams["TP"] * 100)) + "%"
    showPlot(figTitle, "Number of contacts (m)",  "Infection probability")


def study_pim_vs_days_CompareRegions(regionList, drange, methods):
    movAvgWin = userParams["avgOverDays"]
    for region in regionList:
        pims = []
        for d in drange:
            refDate = userParams["consideredDate"] - datetime.timedelta(days=d)
            pim = model.getInfecProbability(region, userParams["TP"], userParams["contacts"], methods, userParams["timeToQuar"], refDate)
            pims.append(pim)

        pims.reverse()
        pimsMA = model.movingAverage(pims, movAvgWin)

        plt.plot(drange[(movAvgWin-1):], pimsMA, label=region)

    figTitle = "Infection Prob. history " + ": " + str(userParams["contacts"]) + " contacts" + " p_t=" + \
               str(int(userParams["TP"] * 100)) + "%, " + str(movAvgWin) + " day avg"
    showPlot(figTitle, "Days since" + str(userParams["consideredDate"] - datetime.timedelta(days=userParams["history"])),
                    "Infection probability")

#############################################################################################


def tabulateRoleInfProbabilities(states):
    scenarioVals = {
        "Grocery Store Shopper": (500, 15),
        "Grocery Store Cashier": (200, 100),
        "Warehouse Worker": (100, 50),
        "Meatpacking Worker": (10, 50),
        "Subway Rider": (75, 30),
        "Takeout Cashier": (200, 30),
        "Non ER Nurse": (20, 20)
    }

    for p in scenarioVals.keys():
        print(p, " & ", "1/" + str(scenarioVals[p][0]), " & ", scenarioVals[p][1], end="  ")
        for s in states:
            pim = model.getInfecProbability(s, 1 / scenarioVals[p][0], scenarioVals[p][1], methodsToAvgOver)
            print(" & ", "{:.2f}".format(100 * pim) + "\%", "  ", end="")

        print("\\\\ \hline")

def plotSpecificDataForStates(startDate, drange, states, parameter, perMil=False):

    for s in states:
        yvalues = []
        for d in drange:
            date = startDate + datetime.timedelta(days=d)
            if parameter == "percentPositive":
                posInc = dataIO.getEntryFromCTPData(s, date, "positiveIncrease")
                negInc = dataIO.getEntryFromCTPData(s, date, "negativeIncrease")
                yval = 100.0*posInc/(posInc + negInc)
            else:
                yval = dataIO.getEntryFromCTPData(s, date, parameter)

            if perMil:
                yvalues.append((float(yval)*1000000.0)/statePopulation[s])
            else:
                yvalues.append(yval)
        plt.plot(drange, yvalues, label=s)

    showPlot(parameter, "days", "value")

#######################################################################

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
