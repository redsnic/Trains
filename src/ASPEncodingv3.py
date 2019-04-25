'''
Created on 9 mar 2019

@author: redsnic
''' 
 
from ClingoInterface import ClingoInterface 
from InputReader import InputReader 
import sys
import time

if __name__ == '__main__':
    startTime = int(round(time.time() * 1000))
    CI = ClingoInterface.ClingoInterface()
    CI.addName("Esercizio 1 'Train', di Rossi Nicolo' 129807")
    CI.addDescription("Versione 3")
    
    Reader = InputReader()
    
    # adding input information
    # actions domain
    CI.addPredicateType("parking", 3)
    CI.addPredicateType("stopping", 3)
    CI.addPredicateType("moving", 4)
    # routes that can be taken when a train is at a given station
    CI.addPredicateType("local_routes", 2)
    # route information
    CI.addPredicateType("len", 2)  
    CI.addPredicateType("from", 2) 
    CI.addPredicateType("to", 2)
    CI.addPredicateType("id", 2)
    CI.addPredicateType("route", 1) 
    # station information
    CI.addPredicateType("capacity", 2)
    CI.addPredicateType("station", 1)
    # train information
    CI.addPredicateType("train", 1)
    CI.addPredicateType("usable_trains", 1)
    CI.addPredicateType("time", 1)
    CI.addPredicateType("final", 1)
    CI.addPredicateType("park", 1)      # stations with deposit
    CI.addPredicateType("stop_only", 1) # stations without deposit
    
    # direct information
    CI.addPredicateType("direct", 2)
    CI.addPredicateType("ok_direct", 2)
    
    # --- ASP CODE PREPARATION
    
    # --- INPUT FACTS GENERATION 
    timeLen = Reader.time
    for line in Reader.prepareASPLinesV3(timeLen):
        CI.addProgramLine(line)
    
    # --- SEARCH SPACE CREATION
    # look for the best number of train to be used
    CI.addProgramLine("1{ max_trains(T) : usable_trains(T) }1.")
    CI.addProgramLine("train(TRAIN) :- usable_trains(TRAIN), TRAIN<=MAX, max_trains(MAX).")
    # prepare the inital state so that all the trains are in a deposit
    CI.addProgramLine("1{ parking(1, TRAIN, STATION): park(STATION)  }1 :- train(TRAIN).")
    # elimination of out of order trains (it eliminates the possible permutations of the trains' IDs) 
    CI.addProgramLine(":- parking(1, TR1, S1), parking(1, TR2, S2), train(TR1), train(TR2), park(S1), park(S2), TR1>TR2, S1<S2.")
    # prepares the following steps
    # from the deposit
    CI.addProgramLine("1{ stopping(TIME+1,TRAIN,STATION); parking(TIME+1,TRAIN,STATION) }1 :- TIME<FIN, final(FIN), parking(TIME, TRAIN, STATION), time(TIME), train(TRAIN), park(STATION).")
    # from a stop (if a station has a deposit or not)
    CI.addProgramLine("1{ parking(TIME+1,TRAIN,STATION); moving(TIME+1, TRAIN, ROUTE, 1) : local_routes(STATION, ROUTE), TIME+LEN<FIN, len(ROUTE, LEN)   }1 :- TIME<FIN, final(FIN), stopping(TIME, TRAIN, STATION), time(TIME), train(TRAIN), park(STATION).")
    # note: the train does not move if it is impossible to end the route in time
    CI.addProgramLine("1{ moving(TIME+1, TRAIN, ROUTE, 1) : local_routes(STATION, ROUTE), TIME+LEN<FIN, len(ROUTE, LEN) }1 :- TIME<FIN, final(FIN), stopping(TIME, TRAIN, STATION), time(TIME), train(TRAIN), stop_only(STATION).")
    # moving
    # while moving
    CI.addProgramLine("moving(TIME+1, TRAIN, ROUTE, POSITION+1) :- ")
    CI.addProgramLine("        TIME<FIN, final(FIN), moving(TIME, TRAIN, ROUTE, POSITION), time(POSITION), time(TIME), train(TRAIN), route(ROUTE), POSITION<LENGTH, len(ROUTE, LENGTH).")
    # when arriving
    CI.addProgramLine("1{ stopping(TIME+1, TRAIN, NEXT_STATION) : to(ROUTE, NEXT_STATION); ")
    CI.addProgramLine("   moving(TIME+1, TRAIN, NEXT_ROUTE, 1) : to(ROUTE, NEXT_STATION), local_routes(NEXT_STATION, NEXT_ROUTE), TIME+LEN<FIN, len(NEXT_ROUTE, LEN)  }1:- ")
    CI.addProgramLine("        TIME<FIN, final(FIN), moving(TIME, TRAIN, ROUTE, POSITION), time(POSITION), time(TIME), train(TRAIN), route(ROUTE), POSITION=LENGTH, len(ROUTE, LENGTH).") 

    # --- CONSTRAINTS FOR THE BASE PROBLEM
    # eliminate cases in which a train is leaving the station and another one is arriving 
    CI.addProgramLine(":- stopping(TIME, TRAIN, STATION), moving(TIME, ROUTE, STATION, 1), from(ROUTE,STATION), route(ROUTE), station(STATION), train(TRAIN).")
    # eliminate the case in which two trains are leaving the same station 
    CI.addProgramLine(":- moving(TIME, TRAIN1, ROUTE1, 1), moving(TIME, TRAIN2, ROUTE2, 1), from(ROUTE1,STATION), from(ROUTE2,STATION), route(ROUTE1), route(ROUTE2), station(STATION), train(TRAIN1), train(TRAIN2), TRAIN1!=TRAIN2.")
        
    # - eliminate cases in which two trains are on the same route at the same time
    CI.addProgramLine(":- moving(TIME, TRAIN1, ROUTE1, POS1), moving(TIME, TRAIN2, ROUTE2, POS2), time(POS1), time(POS2), route(ROUTE1), route(ROUTE2),")
    CI.addProgramLine("                id(ROUTE1,ID1), id(ROUTE2,ID2), ID1=ID2, train(TRAIN1), train(TRAIN2), TRAIN1!=TRAIN2.")

    # - eliminate cases in which two trains are stopping at the same station
    CI.addProgramLine(":- stopping(TIME, TRAIN1, STATION), stopping(TIME, TRAIN2, STATION), station(STATION), train(TRAIN1), train(TRAIN2), time(TIME), TRAIN1 != TRAIN2.")
    
    # - eliminate cases in which there are too many trains in a deposit
    CI.addProgramLine("usage(TIME, STATION, S) :-  park(STATION), time(TIME), S=#count{ TR : parking(TI,TR,ST), train(TR), time(TI), park(ST), ST=STATION, TI=TIME }.")
    CI.addProgramLine(":- CON>CAP, capacity(STATION, CAP), usage(TIME,STATION,CON), park(STATION), time(TIME).")
    
    # - eliminate cases in which a train enters a station before the temporal unit gap
    CI.addProgramLine(":- moving(TIME, TRAIN1, ROUTE1, POS1), moving(TIME+1,TRAIN1,ROUTE2,POS1), stopping(TIME, TRAIN2, DES), to(ROUTE1, DES), from(ROUTE2, DES), ")
    CI.addProgramLine("   train(TRAIN1), train(TRAIN2), route(ROUTE1), route(ROUTE2), time(POS1), time(POS2), route(DES), time(TIME).") 
    # - eliminate cases in which a train stops at a station before the temporal unit gap
    CI.addProgramLine(":- stopping(TIME, TRAIN1, STATION), stopping(TIME+1, TRAIN2, STATION), station(STATION), time(TIME), train(TRAIN1), train(TRAIN2).")


    # --- FINAL STATE
    # 1 - all the trains are in a station (additional cut)
    CI.addProgramLine(":- moving(FIN, TRAIN, ROUTE, DUR), final(FIN), time(DUR), train(TRAIN), route(ROUTE).")
    CI.addProgramLine(":- stopping(FIN, TRAIN, STATION), final(FIN), train(TRAIN), station(STATION).")
    # 2 - the number of train in each deposit is equal at the initial and final steps
    CI.addProgramLine(":- CINI!=CFIN, park(STAT), CINI = #count{ TRAIN : parking(1,TRAIN,STATION), train(TRAIN), station(STATION), STATION=STAT },")
    CI.addProgramLine("                           CFIN = #count{ TRAIN : parking(FIN,TRAIN,STATION), train(TRAIN), station(STATION), final(FIN), STATION=STAT }.")
    
    
    # stopping must be the last or the first action of a train reaching a station 
    CI.addProgramLine(":- parking(TIME, TRAIN, STATION), stopping(TIME+1, TRAIN, STATION), parking(TIME+2, TRAIN, STATION), time(TIME), train(TRAIN),")
    CI.addProgramLine("   park(STATION).")
    
    # --- OBJECTIVE FUNCTION
    CI.addProgramLine("linked(A,B) :- A!=B, station(A), station(B), train(TRAIN), time(T1), time(T2), T1<T2, stopping(T1, TRAIN, A), stopping(T2, TRAIN, B).")
    CI.addProgramLine("answer(S) :- S=#count{ A,B : linked(A,B), station(A), station(B), A!=B }.")
    CI.addProgramLine("#maximize{ S : answer(S) }.")
    
    # --- MANAGE DIRECTS
    CI.addProgramLine("ok_direct(A,B) :-  station(A), station(B), direct(A,B), train(TRAIN), time(T1), time(T2), T1<T2, stopping(T1, TRAIN, A), stopping(T2, TRAIN, B),")
    CI.addProgramLine("CNT=#count{ C : stopping(T3, T, C), T3>T1, T3<T2, time(T3), station(C), train(T), T=TRAIN }, CNT=0.")
    CI.addProgramLine(":- direct(A,B), not ok_direct(A,B).")
    
    # --- MANAGE MINIMUM NUMBER OF CONNECTIONS
    # compute return intervals for each train (if required)
    CI.addProgramLine("interval(TRAIN, A, START, STOP) :- station(A), station(B), min_conn(A,B,K), stopping(START, TRAIN, A), train(TRAIN), time(START), time(STOP), ")
    CI.addProgramLine("        STOP=#min{ TIME : time(TIME), TIME>START, stopping(TIME, TRAIN, A) ; FIN : final(FIN) }.")
    
    CI.addProgramLine(":-  min_conn(A,B,K), station(A), station(B), K>C, C=#count{ START, TRAIN : interval(TRAIN, A, START, STOP ),   ")
    CI.addProgramLine(" train(TRAIN), time(START), time(STOP), stopping(STOPTIME, TRAIN, B), time(STOPTIME), STOPTIME>START, STOPTIME<STOP}.")

    # --- MANAGE INTERMEDIATE STOPS
    # compute return intervals for each train (if required)
    CI.addProgramLine("interval(TRAIN, A, START, STOP) :- station(A), station(B), pathReq(A,B,ID), stopping(START, TRAIN, A), train(TRAIN), time(START), time(STOP), ")
    CI.addProgramLine("        STOP=#min{ TIME : time(TIME), TIME>START, stopping(TIME, TRAIN, A) ; FIN : final(FIN) }.")
    
    # compute the pass by intervals for two stations (if necessary)
    CI.addProgramLine("in_path( TRAIN, A, B, START, STOP) :- train(TRAIN), pathReq(A,B,ID), station(A), station(B), interval(TRAIN, A, START, MAXRANGE), ")
    CI.addProgramLine("         STOP=#min{ STP : stopping(STP, TRAIN, B), STP>START, STP<=MAXRANGE }.")
    
    # prepare path constraints
    for constraint in Reader.pathRequests:
        # parte generale
        CI.addProgramLine("ok(" + constraint["ID"] + ") :- pathReq(" + constraint["SOURCE"] + "," + constraint["DESTINATION"] +"," + constraint["ID"] + "), ")
        CI.addProgramLine("          station(" + constraint["SOURCE"] + "), station(" + constraint["DESTINATION"] + "),")
        CI.addProgramLine("          in_path(TRAIN," + constraint["SOURCE"] + "," + constraint["DESTINATION"] + ",START,STOP), train(TRAIN), time(START), time(STOP)")
        # manage intermediate steps
        ID = 1
        for stop in constraint["STOPS"]:
            CI.addProgramLine(", stopping(TIME"+ str(ID) + ", TRAIN, " + str(stop) + "), time(TIME"+ str(ID) + "), TIME"+ str(ID) + "<STOP, TIME"+ str(ID) + ">START")
            ID+=1
        CI.addProgramLine(".")   
        # remove cases without the required path
        CI.addProgramLine(":- not ok(" + constraint["ID"] + "), pathReq(" + constraint["SOURCE"] + "," + constraint["DESTINATION"] + "," + constraint["ID"] + "), station(" + constraint["SOURCE"] + "), station(" + constraint["DESTINATION"] + ").")
    
    # --- EXECUTE
    CI.run()

    # --- OUTPUT
    try:
        parking = CI.results("parking", 3, len(CI.answers)-1)
        moving = CI.results("moving", 4, len(CI.answers)-1)
        stopping = CI.results("stopping", 3, len(CI.answers)-1)
        links = CI.results("linked", 2, len(CI.answers)-1)
        ans = int(CI.results("answer", 1, len(CI.answers)-1)[0][0])
        trains = int(CI.results("max_trains", 1, len(CI.answers)-1)[0][0])
        
        parking = sorted(map(lambda el: ( int(el[0]), int(el[1]), Reader.stations[int(el[2])-1][0], "PARKS" ), parking))
        stopping = sorted(map(lambda el: ( int(el[0]), int(el[1]), Reader.stations[int(el[2])-1][0], "STOPS" ), stopping))
        moving = sorted(map(lambda el: ( int(el[0]), int(el[1]), Reader.routes[int(el[2])-1], int(el[3]), "MOVES" ), moving))
        links =  sorted(map(lambda el: (  Reader.stations[int(el[0])-1][0],  Reader.stations[int(el[1])-1][0]), links))
        
        output = ""

        for t in range(trains):
            for el in [ el for el in sorted(parking + stopping + moving) if int(el[1]) == t+1]:
                output+=str(el)
                output+="\n"
        output += "ANS := " + str(ans) + "\n"
        print(output)
        f = open(sys.argv[1]+".solASP", "w")
        f.write(output)
        stopTime = int(round(time.time() * 1000))
        f.write("Execution Time: " + str(stopTime-startTime))
        f.close()
                
        
    except Exception:
        f = open(sys.argv[1]+".solASP", "w")
        f.write("No solutions or Error\n")
        stopTime = int(round(time.time() * 1000))
        f.write("Execution Time: " + str(stopTime-startTime))
        f.close()
    
    #print(CI)
    