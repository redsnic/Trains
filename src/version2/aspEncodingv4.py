
from ASPHelper import ASPHelper
from ClingoInterface import ClingoInterface 

def p(x):
    return "\"" + str(x) + "\"" 

def initializeFacts(AS,CI):
    CI.addPredicateType("station", 1)
    for station in AS.stationsNames:
        CI.addProgramLine("station("+p(station)+").")
    CI.addPredicateType("time", 1)
    CI.addProgramLine("time(0.." + str(AS.time) + ").")
    CI.addPredicateType("maxTime",1)
    CI.addProgramLine("maxTime(" + str(AS.time) + ").")
    CI.addPredicateType("edge", 2)
    CI.addPredicateType("max_load", 3)
    CI.addPredicateType("len", 3)  # forces symmetric duration!
    CI.addPredicateType("same_route", 4)
    for source, linkedStations in AS.adjList.items():
        for destination, weights in linkedStations.items():
            CI.addProgramLine("max_load("+p(source)+","+p(destination)+","+str(len(weights))+").")
            CI.addProgramLine("linked("+p(source)+","+p(destination)+").")
            print(source, destination, weights, "!")
            CI.addProgramLine("len("+p(source)+","+p(destination)+","+str(weights[0])+").")
            CI.addProgramLine("same_route("+p(source)+","+p(destination)+","+p(source)+","+p(destination)+ ").")
            CI.addProgramLine("same_route("+p(destination)+","+p(source)+","+p(source)+","+p(destination)+ ").")
            CI.addProgramLine("same_route("+p(source)+","+p(destination)+","+p(destination)+","+p(source)+ ").")
            CI.addProgramLine("same_route("+p(destination)+","+p(source)+","+p(destination)+","+p(source)+ ").")
    # prepare trains
    maxTrains = 0
    CI.addPredicateType("park",1)
    CI.addPredicateType("stop", 1)
    CI.addPredicateType("same_stop", 2)
    for station in AS.stationsNames:
        if station.endswith("_park"):
            CI.addProgramLine("park("+p(station)+").")
            space = 0
            try: 
                space = len(AS.adjList[station][station])
            except KeyError:
                pass
            maxTrains+=space
        elif station.endswith("_stopIN") or station.endswith("_stopOUT"):
            CI.addProgramLine("stop("+p(station)+").")
        else:
            CI.addProgramLine("same_stop("+p(station+"_stopIN")+","+p(station+"_stopOUT")+").")

    CI.addPredicateType("max_trains", 1)
    CI.addProgramLine("max_tr(1.." + str(maxTrains) + ").")
    CI.addProgramLine("1{max_trains(MAXT) : max_tr(MAXT) }1.") # choose number of used trains
    CI.addProgramLine("train(X):- max_tr(X), max_trains(Y), X<=Y, X>=0.")           # prepare trains
    CI.addProgramLine("1{ moving(0,X,P,P) : park(P) }1:- train(X).")  # choose a starting station
    CI.addProgramLine(":- moving(0,X,S1,S1), moving(0,X,S2,S2), train(X), park(S1), park(S2), S1!=S2.") # cannot have a train in multiple locations

    

def prepareSearchSpace(AS,CI):
    CI.addProgramLine("% Prepare search space (train paths)")
    CI.addProgramLine("")
    CI.addProgramLine("1{ moving(TIME+LSD,TRAIN,DESTINATION,NEXT) : linked(DESTINATION,NEXT), len(DESTINATION,NEXT,LDN) }1 :-")
    CI.addProgramLine("                  len(SOURCE,DESTINATION,LSD), moving(TIME,TRAIN,SOURCE,DESTINATION), station(SOURCE), station(DESTINATION), time(TIME), train(TRAIN), TIME<MT, maxTime(MT).")
    CI.addProgramLine("")
 
def requireSameEnd(AS,CI):
    CI.addProgramLine("% Require same intial and final state (note: can reach a park only from a 1 lenght edge)")
    CI.addProgramLine(":- INI = #count{ T : moving(0,T,P,P), train(T), park(P) }, FIN = #count{ T : moving(MT-1, T, P, P ), train(T), park(P), maxTime(MT)}, FIN!=INI.")
    CI.addProgramLine("")

def noCollisions(AS,CI):
    CI.addProgramLine("% Remove collisions")
    CI.addProgramLine("% 1 binary")
    CI.addProgramLine(":- moving(TM1,TR1,S1,D1), moving(TM2,TR2, S2, D2), time(TM1), time(TM2), train(TR1), train(TR2), station(S1), station(S2), station(D1), station(D2), ")
    CI.addProgramLine("       same_route(S1,D1,S2,D2), TM1<=TM2, TM1+L1>=TM2, len(S1,D1,L1), len(S2,D2,L2),") # the opposite should not be necessary
    CI.addProgramLine("       max_load(S1,D1,1), TR1 != TR2.")
    CI.addProgramLine("")
    CI.addProgramLine("")
    CI.addProgramLine("% 2 binaries")
    CI.addProgramLine(":- moving(TM1,TR1,S1,D1), moving(TM2,TR2, S2, D2), time(TM1), time(TM2), train(TR1), train(TR2), station(S1), station(S2), station(D1), station(D2), ")
    CI.addProgramLine("   moving(TM3,TR3,S3,D3), train(TR3), time(TM3), station(S3), station(D3), same_route(S2,D2,S3,D3),")
    CI.addProgramLine("       same_route(S1,D1,S2,D2), TM1<=TM2, TM1+L1>=TM2, len(S1,D1,L1), len(S2,D2,L2), len(S3,D3,L3),") # the opposite should not be necessary
    CI.addProgramLine("       TM2<=TM3, TM2+L3>=TM3, max_load(S1,D1,2), TR1 != TR2, TR2 != TR3 , TR3 != TR1.")
    CI.addProgramLine("")

def notTooManyParked(AS,CI):
    CI.addProgramLine("")
    CI.addProgramLine("% Check if too many trains parked")
    CI.addProgramLine("parking(TIME, TRAIN, STATION) :- moving(TIME,TRAIN,X,STATION), park(STATION), station(X), time(TIME), train(TRAIN).")
    CI.addProgramLine(":- NT>CPT, NT = #count{ TRAIN : parking(TIME, TRAIN, STAT), train(TRAIN), time(TIME)}, park(STATION), STAT=STATION, max_load(STATION,STATION,CPT).")
    CI.addProgramLine("")

def noCollisionAtStation(AS,CI):
    CI.addProgramLine("% Remove problems with the doubly defined stops")
    CI.addProgramLine(":- moving(TM1,TR1,S1,D1), moving(TM2,TR2, S2, D2), time(TM1), time(TM2), train(TR1), train(TR2), station(S1), station(S2), station(D1), station(D2), same_stop(S1,S2), TR1 != TR2.")
    CI.addProgramLine(":- moving(TM1,TR1,S1,D1), moving(TM2,TR2, S2, D2), time(TM1), time(TM2), train(TR1), train(TR2), station(S1), station(S2), station(D1), station(D2), same_stop(S1,D2), TR1 != TR2.")
    CI.addProgramLine(":- moving(TM1,TR1,S1,D1), moving(TM2,TR2, S2, D2), time(TM1), time(TM2), train(TR1), train(TR2), station(S1), station(S2), station(D1), station(D2), same_stop(D1,S2), TR1 != TR2.")
    CI.addProgramLine(":- moving(TM1,TR1,S1,D1), moving(TM2,TR2, S2, D2), time(TM1), time(TM2), train(TR1), train(TR2), station(S1), station(S2), station(D1), station(D2), same_stop(D1,D2), TR1 != TR2.")

def defineGoal(AS,CI):
    CI.addProgramLine("% GOAL!")
    for source in AS.stationsNames:
        if source.endswith("_park"):
            pass
        elif source.endswith("_stopIN") or source.endswith("_stopOUT"):
            pass
        else:
            for dest in AS.stationsNames:
                if dest.endswith("_park"):
                    pass
                elif dest.endswith("_stopIN") or dest.endswith("_stopOUT"):
                    pass
                elif source != dest:
                    CI.addProgramLine("conn(" + p(source) +","+ p(dest) + ") :- ")
                    CI.addProgramLine("   moving(TM1,TR," + p(source+"_stopIN") +",D1), moving(TM2,TR, S2, " + p(dest+"_stopIN") +"), TM1<TM2, time(TM1), time(TM2), train(TR), station(S2), station(D1).")
                    CI.addProgramLine("conn(" + p(source) +","+ p(dest) + ") :- ")
                    CI.addProgramLine("   moving(TM1,TR," + p(source+"_stopOUT") +",D1), moving(TM2,TR, S2, " + p(dest+"_stopIN") +"), TM1<TM2, time(TM1), time(TM2), train(TR), station(S2), station(D1).")
    CI.addProgramLine("goal(S) :-  S=#count{ A,B : conn(A,B), station(A), station(B), A != B }.")
    CI.addProgramLine("#maximize{ S : goal(S) }.")
    

if __name__ == "__main__":
    AS = ASPHelper() 
    CI = ClingoInterface.ClingoInterface()
    CI.addDescription("Trains version 4...")
    initializeFacts(AS,CI)
    prepareSearchSpace(AS,CI)
    requireSameEnd(AS,CI)
    noCollisions(AS,CI)
    notTooManyParked(AS,CI)
    defineGoal(AS,CI)
    CI.run()
    #AS.toDot()
    #print(CI)