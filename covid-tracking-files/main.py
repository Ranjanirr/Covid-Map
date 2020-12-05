from studies import *

args = dataIO.parseCLI()

if args.consideredDate:
    userParams["consideredDate"] = dataIO.convert_Y_M_D(args.consideredDate)
else:
    userParams["consideredDate"] = dataIO.convert_Y_M_D(userParams["dateOfLastUpd"]) - datetime.timedelta(1)

if args.updateAsOf:
    userParams["dateOfLastUpd"] = args.updateAsOf
    userParams["consideredDate"] = dataIO.convert_Y_M_D(userParams["dateOfLastUpd"]) - datetime.timedelta(1)

noUpdateNeeded = args.noupdateData or args.updateAsOf
dataIO.initData(not noUpdateNeeded)

userParams["history"] = args.history
userParams["avgOverDays"] = args.avgOverDays
userParams["jsObj"] = args.js

print("\nAnalysis for considered date:", userParams["consideredDate"].strftime("%m/%d/%Y"))
print("Each data item averaged over the last ", userParams["avgOverDays"], "days")

userParams["TP"] = args.TransmissionProbability
userParams["contacts"] = args.NumContacts
userParams["comfortProb"] = args.ComfortProbability
userParams["timeToQuar"] = args.TimeToQuar

listOfStates = list(statePopulation.keys())
allStates = [k for k in listOfStates if k not in statesToExclude]
userParams["selectedStates"] = allStates if args.states == "all" else [k for k in args.states.split()]

if (args.plot or args.dataview) and len(userParams["selectedStates"]) > 6:
    print("Too many states to plot, exiting...")
    exit()

if args.dataview:
    stats = [k for k in args.dataview.split()]
    startDate = userParams["consideredDate"] - datetime.timedelta(args.history)
    drange = np.linspace(0, args.history, (args.history + 1))
    for s in stats:
        print("Viewing", s, "for states", args.states)
        plotSpecificDataForStates(startDate, drange, userParams["selectedStates"], s, args.perMil)

if args.tabulate:
    print("Tabulating for states", userParams["selectedStates"])
    tabulateStateResults(userParams["selectedStates"], args.methodsShow)
    #tabulateRoleInfProbabilities(userParams["selectedStates"])

if args.plot:
    studiesAll = ["CompareMethods", "InfProb", "QuarantineVsNot", "ContactBudget", "Evolution"]
    studiesToDo = studiesAll if args.plot == "all" else [k for k in args.plot.split()]
    print("Plotting for states", userParams["selectedStates"], "studies: ", studiesToDo)

    selectedStates = userParams["selectedStates"]
    consideredDate = userParams["consideredDate"]

    if "CompareMethods" in studiesToDo:
        study_pim_vs_m_CompareMethodsForGivenRegion(focusState, mrange, methodsToAvgOver)
        study_pim_vs_p_t_CompareMethodsForGivenRegion(focusState, p_t_range, methodsToAvgOver)

    if "InfProb" in studiesToDo:
        study_pim_vs_m_CompareRegions(selectedStates, mrange, methodsToAvgOver)
        study_pim_vs_m_Compare_p_t(focusState, mrange, methodsToAvgOver, [0.01, 0.05, 0.1])
    # # # ##### don't include study_pim_vs_p_t_CompareRegions(selectedStates, p_t_range, methodsToAvgOver)

    if "QuarantineVsNot" in studiesToDo:
        study_pim_vs_m_CompareQuar(focusState, mrange, methodsToAvgOver, [lag, userParams["timeToQuar"]])
        study_pim_vs_tq_CompareRegions(selectedStates, tqrange, methodsToAvgOver)

    if "ContactBudget" in studiesToDo:
        study_Mpc_vs_p_t_ComparePc(focusState, p_t_range, methodsToAvgOver, [0.01, 0.1])
        study_Mpc_vs_pc_CompareRegions(selectedStates, pcrange, methodsToAvgOver)

    if "Evolution" in studiesToDo:
        #study_pim_vs_m_compareDays(focusState, mrange, ["A"], [consideredDate, consideredDate - datetime.timedelta(args.history)])
        drange = np.linspace(0, userParams["history"], userParams["history"]+1)
        study_pim_vs_days_CompareRegions(selectedStates, drange, ["A"])
        #study_pim_vs_days_CompareRegions(selectedStates, drange, ["A"], movAvgWin=1)
