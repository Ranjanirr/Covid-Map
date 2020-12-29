import dataIO
from params import *

def movingAverage(values, window):
    x = np.convolve(values, np.ones(window), "valid")/window
    return x

def getGrowthByMethod(region, method, dth_c, infec_c, dth_b, infec_b, refDate):
    if method == "A":
        midDate = refDate - datetime.timedelta(days=int(lag/2))
        R = dataIO.getEffRepFromData(region, midDate)
        G = R ** (1 / serialInterval)
    elif method == "B":
        G_total = infec_c / infec_b if infec_b != 0 else infec_c
        G = G_total ** (1 / lag)
    elif method == "C":
        G_total = dth_c / dth_b if dth_b != 0 else dth_c
        G = G_total ** (1 / lag)
    else:
        print("Unknown method in getGrowthByMethod")
        exit()

    return G


def getTotalInfectionsInRegion(refDate, region, methodsToAvgOver, tqspace=lag):

    laggedDate = refDate - datetime.timedelta(days=lag)

    dth_c = dataIO.getEntryFromCTPData(region, refDate, "deathIncrease")
    infec_c = dataIO.getEntryFromCTPData(region, refDate, "positiveIncrease")
    dth_b = dataIO.getEntryFromCTPData(region, laggedDate, "deathIncrease")
    infec_b = dataIO.getEntryFromCTPData(region, laggedDate, "positiveIncrease")

    #print("info ", dth_c, infec_c, dth_b, infec_b)

    if dth_c < 0 or infec_c < 0:
        print("DATA ERROR: daily data for", region, "on or around", refDate, "is negative, result invalid, suggest using later date", dth_c, infec_c)
        dth_c = max(dth_c, 0); infec_c = max(infec_c, 0)
    if dth_b < 0 or infec_b < 0:
        print("DATA ERROR: daily data for", region, "on or around", laggedDate, "is negative, suggest using later date")
        dth_b = max(dth_b, 0); infec_b = max(infec_b, 0)

    laggedPhi = dth_c / IFR

    cumPhi = 0
    for M in methodsToAvgOver:
        G = getGrowthByMethod(region, M, dth_c, infec_c, dth_b, infec_b, refDate)
        phi_c = laggedPhi * (G*(G ** lag - G ** (lag - tqspace)) / (G - 1)) if G != 1 else tqspace*laggedPhi

        cumPhi += phi_c

    avgPhi = cumPhi/len(methodsToAvgOver)
    return avgPhi

def getInfectionsOnRefDateInRegion(refDate, region, methodsToAvgOver, tqspace=lag):

    laggedDate = refDate - datetime.timedelta(days=lag)

    dth_c = dataIO.getEntryFromCTPData(region, refDate, "deathIncrease")
    infec_c = dataIO.getEntryFromCTPData(region, refDate, "positiveIncrease")
    dth_b = dataIO.getEntryFromCTPData(region, laggedDate, "deathIncrease")
    infec_b = dataIO.getEntryFromCTPData(region, laggedDate, "positiveIncrease")

    if dth_c < 0 or infec_c < 0:
        print("DATA ERROR: daily data for", region, "on or around", refDate, "is negative, suggest using later date", dth_c, infec_c)
        dth_c = max(dth_c, 0); infec_c = max(infec_c, 0)
    if dth_b < 0 or infec_b < 0:
        print("DATA ERROR: daily data for", region, "on or around", laggedDate, "is negative, suggest using later date")
        dth_b = max(dth_b, 0); infec_b = max(infec_b, 0)
        #exit()

    laggedPhi = dth_c / IFR

    cumInf = 0
    for M in methodsToAvgOver:
        G = getGrowthByMethod(region, M, dth_c, infec_c, dth_b, infec_b, refDate)
        phi_ref = laggedPhi * (G ** lag)  if G != 1 else laggedPhi

        cumInf += phi_ref

    avgRefInf = cumInf/len(methodsToAvgOver)
    return avgRefInf

def getInfecProbability(region, ptspace, mspace, methods, tqspace=lag, overrideDate = NULLL):

    if not isinstance(methods, list):
        methods = [methods]

    refDate = overrideDate if overrideDate != NULLL else userParams["consideredDate"]
    phi_i = getTotalInfectionsInRegion(refDate, region, methods, tqspace)

    p_i = (phi_i / (statePopulation[region])) * ptspace

    pim = 1.0 - (1.0 - p_i) ** mspace

    return pim

def getPhi_i(region, ptspace, mspace, methods, tqspace=lag, overrideDate = NULLL):

    if not isinstance(methods, list):
        methods = [methods]

    refDate = overrideDate if overrideDate != NULLL else userParams["consideredDate"]
    phi_i = getTotalInfectionsInRegion(refDate, region, methods, tqspace)

    return phi_i


def getContactsBudget(region, ptspace, pcspace, methods, tqspace=lag, overrideDate=NULLL):

    if not isinstance(methods, list):
        methods = [methods]

    refDate = overrideDate if overrideDate != NULLL else userParams["consideredDate"]
    phi_i = getTotalInfectionsInRegion(refDate, region, methods, tqspace)

    numerator = (1 - pcspace)
    denominator = 1 - ( (phi_i / (statePopulation[region])) * ptspace)

    if phi_i == 0:
        return "NO LIMIT", -1
    else:
        M = np.log(numerator) / np.log(denominator)
        return "LIMITED", M






