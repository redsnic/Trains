'''
Created on 9 mar 2019

@author: redsnic
''' 
 
from ClingoInterface import ClingoInterface 
from InputReader import InputReader 

if __name__ == '__main__':
    CI = ClingoInterface.ClingoInterface()
    CI.addName("Esercizio 1 'Train', di Rossi Nicolo' 129807")
    CI.addDescription("Versione 3")
    
    Reader = InputReader()
    
    # aggiunta delle informazioni sui predicati per l'output
    # actions domain
    CI.addPredicateType("parking", 3)
    CI.addPredicateType("stopping", 3)
    CI.addPredicateType("moving", 4)
    # indica le tratte percorribili a partire dalla data stazione
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
    CI.addPredicateType("park", 1) # indica le stazioni con parcheggio
    CI.addPredicateType("stop_only", 1) # indica le stazioni senza parcheggio
    
    # direct information
    CI.addPredicateType("direct", 2)
    CI.addPredicateType("ok_direct", 2)
    
    # --- PREPARAZIONE DEL CODICE ASP
    
    # --- GENERAZIONE DEI FATTI PER L'INPUT   
    timeLen = 22
    for line in Reader.prepareASPLinesV3(timeLen):
        CI.addProgramLine(line)
    
    # --- CREAZIONE DELLO SPAZIO DI RICERCA
    # individua il miglior numero di treni da impiegare
    CI.addProgramLine("1{ max_trains(T) : usable_trains(T) }1.")
    CI.addProgramLine("train(TRAIN) :- usable_trains(TRAIN), TRAIN<=MAX, max_trains(MAX).")
    # preparazione dello stato iniziale (ogni treno e' in un parcheggio
    CI.addProgramLine("1{ parking(1, TRAIN, STATION): park(STATION)  }1 :- train(TRAIN).")
    # elimina i casi fuori ordine (elimina possibili permutazioni di treni nelle stazioni iniziali) 
    CI.addProgramLine(":- parking(1, TR1, S1), parking(1, TR2, S2), train(TR1), train(TR2), park(S1), park(S2), TR1>TR2, S1<S2.")
    # prepara i passi successivi
    # dal parcheggio tolgo moving(TIME+1, TRAIN, ROUTE, 0) : local_routes(STATION, ROUTE) in quato i passeggeri devono essere caricati prima di uscire dalla stazione
    CI.addProgramLine("1{ stopping(TIME+1,TRAIN,STATION); parking(TIME+1,TRAIN,STATION) }1 :- TIME<FIN, final(FIN), parking(TIME, TRAIN, STATION), time(TIME), train(TRAIN), park(STATION).")
    # dalla fermata (se la stazione ha o no il parcheggio)
    CI.addProgramLine("1{ parking(TIME+1,TRAIN,STATION); moving(TIME+1, TRAIN, ROUTE, 1) : local_routes(STATION, ROUTE), TIME+LEN<FIN, len(ROUTE, LEN)   }1 :- TIME<FIN, final(FIN), stopping(TIME, TRAIN, STATION), time(TIME), train(TRAIN), park(STATION).")
    #                                                                                     non partire se non e' possibile
    CI.addProgramLine("1{ moving(TIME+1, TRAIN, ROUTE, 1) : local_routes(STATION, ROUTE), TIME+LEN<FIN, len(ROUTE, LEN) }1 :- TIME<FIN, final(FIN), stopping(TIME, TRAIN, STATION), time(TIME), train(TRAIN), stop_only(STATION).")
    # della tratta
    # in transito
    CI.addProgramLine("moving(TIME+1, TRAIN, ROUTE, POSITION+1) :- ")
    CI.addProgramLine("        TIME<FIN, final(FIN), moving(TIME, TRAIN, ROUTE, POSITION), time(POSITION), time(TIME), train(TRAIN), route(ROUTE), POSITION<LENGTH, len(ROUTE, LENGTH).")
    # in arrivo (tolgo  parking(TIME+1, TRAIN, NEXT_STATION) : to(ROUTE, NEXT_STATION); in quanto i passeggeri devono essere scaricati prima di mettere il treno in deposito
    CI.addProgramLine("1{ stopping(TIME+1, TRAIN, NEXT_STATION) : to(ROUTE, NEXT_STATION); ")
    CI.addProgramLine("   moving(TIME+1, TRAIN, NEXT_ROUTE, 1) : to(ROUTE, NEXT_STATION), local_routes(NEXT_STATION, NEXT_ROUTE), TIME+LEN<FIN, len(NEXT_ROUTE, LEN)  }1:- ")
    CI.addProgramLine("        TIME<FIN, final(FIN), moving(TIME, TRAIN, ROUTE, POSITION), time(POSITION), time(TIME), train(TRAIN), route(ROUTE), POSITION=LENGTH, len(ROUTE, LENGTH).") 

    # --- VINCOLI PER IL PROBLEMA DI BASE SENZA RICHIESTE
    # - elimina i casi in cui non lasco libera la stazione una unita' temporale
    # elimino i casi in cui un treno e' in fermata su una stazione e un altro e' appena partito 
    CI.addProgramLine(":- stopping(TIME, TRAIN, STATION), moving(TIME, ROUTE, STATION, 1), from(ROUTE,STATION), route(ROUTE), station(STATION), train(TRAIN).")
    # elimino i casi in cui due treni stanno partendo in contemporanea dalla stazione
    CI.addProgramLine(":- moving(TIME, TRAIN1, ROUTE1, 1), moving(TIME, TRAIN2, ROUTE2, 1), from(ROUTE1,STATION), from(ROUTE2,STATION), route(ROUTE1), route(ROUTE2), station(STATION), train(TRAIN1), train(TRAIN2), TRAIN1!=TRAIN2.")
        
    # - elimina i casi in cui ci sono due tratte occupate allo stesso tempo
    CI.addProgramLine(":- moving(TIME, TRAIN1, ROUTE1, POS1), moving(TIME, TRAIN2, ROUTE2, POS2), time(POS1), time(POS2), route(ROUTE1), route(ROUTE2),")
    CI.addProgramLine("                id(ROUTE1,ID1), id(ROUTE2,ID2), ID1=ID2, train(TRAIN1), train(TRAIN2), TRAIN1!=TRAIN2.")

    # - elimina i casi in cui ci sono due treni in fermata nella stessa stazione
    CI.addProgramLine(":- stopping(TIME, TRAIN1, STATION), stopping(TIME, TRAIN2, STATION), station(STATION), train(TRAIN1), train(TRAIN2), time(TIME), TRAIN1 != TRAIN2.")
    
    # - elimina i casi in cui ci sono troppi treni in una stazione (eventualmente migliorabile restringendo il dominio alle sole stazioni con parcheggio  --> potrebbe essere usato anche in altri casi!)
    CI.addProgramLine("usage(TIME, STATION, S) :-  park(STATION), time(TIME), S=#count{ TR : parking(TI,TR,ST), train(TR), time(TI), park(ST), ST=STATION, TI=TIME }.")
    CI.addProgramLine(":- CON>CAP, capacity(STATION, CAP), usage(TIME,STATION,CON), park(STATION), time(TIME).")
    
    
    # --- STATO FINALE
    # 1 - tutti i treni sono in una stazione (non sono necessari se richiedo gli stessi conteggi)
    CI.addProgramLine(":- moving(FIN, TRAIN, ROUTE, DUR), final(FIN), time(DUR), train(TRAIN), route(ROUTE).")
    CI.addProgramLine(":- stopping(FIN, TRAIN, STATION), final(FIN), train(TRAIN), station(STATION).")
    # 2 - e i conteggi sono uguali a quelli nello stato iniziale
    CI.addProgramLine(":- CINI!=CFIN, park(STAT), CINI = #count{ TRAIN : parking(1,TRAIN,STATION), train(TRAIN), station(STATION), STATION=STAT },")
    CI.addProgramLine("                           CFIN = #count{ TRAIN : parking(FIN,TRAIN,STATION), train(TRAIN), station(STATION), final(FIN), STATION=STAT }.")
    
    
    # --- ALTRE REGOLE PER LA SIMMETRIA
    # lo stop e' l'ultima o la prima azione di una parcheggiata (forse non si puo' forzare cosi', ma in realta' anche si', voglio comunque far scendere i passeggeri)
    CI.addProgramLine(":- parking(TIME, TRAIN, STATION), stopping(TIME+1, TRAIN, STATION), parking(TIME+2, TRAIN, STATION), time(TIME), train(TRAIN),")
    CI.addProgramLine("   park(STATION).")
    
    
    
    # --- FUNZIONE OBIETTIVO
    CI.addProgramLine("linked(A,B) :- A!=B, station(A), station(B), train(TRAIN), time(T1), time(T2), T1<T2, stopping(T1, TRAIN, A), stopping(T2, TRAIN, B).")
    CI.addProgramLine("answer(S) :- S=#count{ A,B : linked(A,B), station(A), station(B), A!=B }.")
    CI.addProgramLine("#maximize{ S : answer(S) }.")
    
    
    
    # --- GESTIONE DEI DIRETTI
    CI.addProgramLine("ok_direct(A,B) :-  station(A), station(B), direct(A,B), train(TRAIN), time(T1), time(T2), T1<T2, stopping(T1, TRAIN, A), stopping(T2, TRAIN, B),")
    CI.addProgramLine("CNT=#count{ C : stopping(T3, T, C), T3>T1, T3<T2, time(T3), station(C), train(T), T=TRAIN }, CNT=0.")
    CI.addProgramLine(":- direct(A,B), not ok_direct(A,B).")
    
    
    
    # --- GESTIONE MINIMO NUMERO DI COLLEGAMENTI
    # calcola gli intervalli di ritorno per ogni treno (per cui questo e' necessario)
    CI.addProgramLine("interval(TRAIN, A, START, STOP) :- station(A), station(B), min_conn(A,B,K), stopping(START, TRAIN, A), train(TRAIN), time(START), time(STOP), ")
    CI.addProgramLine("        STOP=#min{ TIME : time(TIME), TIME>START, stopping(TIME, TRAIN, A) ; FIN : final(FIN) }.")
    
    CI.addProgramLine(":-  min_conn(A,B,K), station(A), station(B), K>C, C=#count{ START, TRAIN : interval(TRAIN, A, START, STOP ),   ")
    CI.addProgramLine(" train(TRAIN), time(START), time(STOP), stopping(STOPTIME, TRAIN, B), time(STOPTIME), STOPTIME>START, STOPTIME<STOP}.")


     
    # --- GESTIONE DELLE FERMATE INTERMEDIE RICHIESTE
    # calcola gli intervalli di ritorno per ogni treno (per cui questo e' necessario)
    CI.addProgramLine("interval(TRAIN, A, START, STOP) :- station(A), station(B), pathReq(A,B,ID), stopping(START, TRAIN, A), train(TRAIN), time(START), time(STOP), ")
    CI.addProgramLine("        STOP=#min{ TIME : time(TIME), TIME>START, stopping(TIME, TRAIN, A) ; FIN : final(FIN) }.")
    
    # calcola gli intervalli di passaggio tra le due stazioni interessate
    CI.addProgramLine("in_path( TRAIN, A, B, START, STOP) :- train(TRAIN), pathReq(A,B,ID), station(A), station(B), interval(TRAIN, A, START, MAXRANGE), ")
    CI.addProgramLine("         STOP=#min{ STP : stopping(STP, TRAIN, B), STP>START, STP<MAXRANGE }.")
    
    # prepara i vincoli di percorso
    for constraint in Reader.pathRequests:
        # parte generale
        CI.addProgramLine("ok(" + constraint["ID"] + ") :- pathReq(" + constraint["SOURCE"] + "," + constraint["DESTINATION"] +"," + constraint["ID"] + "), ")
        CI.addProgramLine("          station(" + constraint["SOURCE"] + "), station(" + constraint["DESTINATION"] + "),")
        CI.addProgramLine("          in_path(TRAIN," + constraint["SOURCE"] + "," + constraint["DESTINATION"] + ",START,STOP), train(TRAIN), time(START), time(STOP)")
        # imposizione dei passaggi intermedi
        ID = 1
        for stop in constraint["STOPS"]:
            CI.addProgramLine(", stopping(TIME"+ str(ID) + ", TRAIN, " + str(stop) + "), time(TIME"+ str(ID) + "), TIME"+ str(ID) + "<STOP, TIME"+ str(ID) + ">START")
            ID+=1
        CI.addProgramLine(".")   
        # remove cases in which there is not a satisfing path 
        CI.addProgramLine(":- not ok(" + constraint["ID"] + "), pathReq(" + constraint["SOURCE"] + "," + constraint["DESTINATION"] + "," + constraint["ID"] + "), station(" + constraint["SOURCE"] + "), station(" + constraint["DESTINATION"] + ").")
    
    # --- ESECUZIONE
    CI.run()

    # --- DATI DA VISUALIZZARE NELL'OUTPUT
    try:
        parking = CI.results("parking", 3, len(CI.answers)-1)
        moving = CI.results("moving", 4, len(CI.answers)-1)
        stopping = CI.results("stopping", 3, len(CI.answers)-1)
        links = CI.results("linked", 2, len(CI.answers)-1)
        ans = int(CI.results("answer", 1, len(CI.answers)-1)[0][0])
        trains = int(CI.results("max_trains", 1, len(CI.answers)-1)[0][0])
        #for el in CI.answers:
        #    print(el["status/3"])
        
        parking = sorted(map(lambda el: ( int(el[0]), int(el[1]), Reader.stations[int(el[2])-1][0], "PARKS" ), parking))
        stopping = sorted(map(lambda el: ( int(el[0]), int(el[1]), Reader.stations[int(el[2])-1][0], "STOPS" ), stopping))
        moving = sorted(map(lambda el: ( int(el[0]), int(el[1]), Reader.routes[int(el[2])-1], int(el[3]), "MOVES" ), moving))
        links =  sorted(map(lambda el: (  Reader.stations[int(el[0])-1][0],  Reader.stations[int(el[1])-1][0]), links))
        
        
        for t in range(trains):
            for el in [ el for el in sorted(parking + stopping + moving) if int(el[1]) == t+1]:
                print(el)
                
        print(ans)
    except Exception:
        print("No answer!")
    
    # --- FORMATTAZIONE DELL'OUTPUT
    #for el in sorted([ (int(l[0]), int(l[1]), l[2]) for l in status  ]):
    #    print("TRENO:" + str(el[0]) + " TEMPO: " + str(el[1]) + " AZIONE: " + Reader.translateAction(int(el[2])) + " ID : " + el[2])
    #print(CI.results("answer", 1, len(CI.answers)-1))
    #print([ map(Reader.translateAction,map(int,l)) for l in  CI.results("linked", 2, len(CI.answers)-1)  ])
    print(CI)
    