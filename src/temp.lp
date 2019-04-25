%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%% Esercizio 1 'Train', di Rossi Nicolo' 129807 %%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Description:
% Versione 3
%%% Input facts:
% id/2
% station/1
% final/1
% stopping/3
% parking/3
% local_routes/2
% park/1
% len/2
% route/1
% capacity/2
% usable_trains/1
% to/2
% time/1
% moving/4
% direct/2
% from/2
% ok_direct/2
% stop_only/1
% train/1
time(1..40).
final(40).
station(1..6).
usable_trains(1..1).
capacity(1,1).
park(1).
capacity(2,0).
stop_only(2).
capacity(3,0).
stop_only(3).
capacity(4,0).
stop_only(4).
capacity(5,0).
stop_only(5).
capacity(6,0).
stop_only(6).
route(1).
from(1,1).
local_routes(1,1).
to(1,2).
len(1,1).
id(1,1).
route(2).
from(2,2).
local_routes(2,2).
to(2,1).
len(2,1).
id(2,1).
route(3).
from(3,1).
local_routes(1,3).
to(3,4).
len(3,15).
id(3,2).
route(4).
from(4,4).
local_routes(4,4).
to(4,1).
len(4,15).
id(4,2).
route(5).
from(5,1).
local_routes(1,5).
to(5,6).
len(5,1).
id(5,3).
route(6).
from(6,6).
local_routes(6,6).
to(6,1).
len(6,1).
id(6,3).
route(7).
from(7,2).
local_routes(2,7).
to(7,3).
len(7,1).
id(7,4).
route(8).
from(8,3).
local_routes(3,8).
to(8,2).
len(8,1).
id(8,4).
route(9).
from(9,3).
local_routes(3,9).
to(9,4).
len(9,1).
id(9,5).
route(10).
from(10,4).
local_routes(4,10).
to(10,3).
len(10,1).
id(10,5).
route(11).
from(11,4).
local_routes(4,11).
to(11,5).
len(11,1).
id(11,6).
route(12).
from(12,5).
local_routes(5,12).
to(12,4).
len(12,1).
id(12,6).
route(13).
from(13,5).
local_routes(5,13).
to(13,6).
len(13,1).
id(13,7).
route(14).
from(14,6).
local_routes(6,14).
to(14,5).
len(14,1).
id(14,7).
direct(4,1).
direct(1,4).
1{ max_trains(T) : usable_trains(T) }1.
train(TRAIN) :- usable_trains(TRAIN), TRAIN<=MAX, max_trains(MAX).
1{ parking(1, TRAIN, STATION): park(STATION)  }1 :- train(TRAIN).
:- parking(1, TR1, S1), parking(1, TR2, S2), train(TR1), train(TR2), park(S1), park(S2), TR1>TR2, S1<S2.
1{ stopping(TIME+1,TRAIN,STATION); parking(TIME+1,TRAIN,STATION) }1 :- TIME<FIN, final(FIN), parking(TIME, TRAIN, STATION), time(TIME), train(TRAIN), park(STATION).
1{ parking(TIME+1,TRAIN,STATION); moving(TIME+1, TRAIN, ROUTE, 1) : local_routes(STATION, ROUTE), TIME+LEN<FIN, len(ROUTE, LEN)   }1 :- TIME<FIN, final(FIN), stopping(TIME, TRAIN, STATION), time(TIME), train(TRAIN), park(STATION).
1{ moving(TIME+1, TRAIN, ROUTE, 1) : local_routes(STATION, ROUTE), TIME+LEN<FIN, len(ROUTE, LEN) }1 :- TIME<FIN, final(FIN), stopping(TIME, TRAIN, STATION), time(TIME), train(TRAIN), stop_only(STATION).
moving(TIME+1, TRAIN, ROUTE, POSITION+1) :- 
        TIME<FIN, final(FIN), moving(TIME, TRAIN, ROUTE, POSITION), time(POSITION), time(TIME), train(TRAIN), route(ROUTE), POSITION<LENGTH, len(ROUTE, LENGTH).
1{ stopping(TIME+1, TRAIN, NEXT_STATION) : to(ROUTE, NEXT_STATION); 
   moving(TIME+1, TRAIN, NEXT_ROUTE, 1) : to(ROUTE, NEXT_STATION), local_routes(NEXT_STATION, NEXT_ROUTE), TIME+LEN<FIN, len(NEXT_ROUTE, LEN)  }1:- 
        TIME<FIN, final(FIN), moving(TIME, TRAIN, ROUTE, POSITION), time(POSITION), time(TIME), train(TRAIN), route(ROUTE), POSITION=LENGTH, len(ROUTE, LENGTH).
:- stopping(TIME, TRAIN, STATION), moving(TIME, ROUTE, STATION, 1), from(ROUTE,STATION), route(ROUTE), station(STATION), train(TRAIN).
:- moving(TIME, TRAIN1, ROUTE1, 1), moving(TIME, TRAIN2, ROUTE2, 1), from(ROUTE1,STATION), from(ROUTE2,STATION), route(ROUTE1), route(ROUTE2), station(STATION), train(TRAIN1), train(TRAIN2), TRAIN1!=TRAIN2.
:- moving(TIME, TRAIN1, ROUTE1, POS1), moving(TIME, TRAIN2, ROUTE2, POS2), time(POS1), time(POS2), route(ROUTE1), route(ROUTE2),
                id(ROUTE1,ID1), id(ROUTE2,ID2), ID1=ID2, train(TRAIN1), train(TRAIN2), TRAIN1!=TRAIN2.
:- stopping(TIME, TRAIN1, STATION), stopping(TIME, TRAIN2, STATION), station(STATION), train(TRAIN1), train(TRAIN2), time(TIME), TRAIN1 != TRAIN2.
usage(TIME, STATION, S) :-  park(STATION), time(TIME), S=#count{ TR : parking(TI,TR,ST), train(TR), time(TI), park(ST), ST=STATION, TI=TIME }.
:- CON>CAP, capacity(STATION, CAP), usage(TIME,STATION,CON), park(STATION), time(TIME).
:- moving(TIME, TRAIN1, ROUTE1, POS1), moving(TIME+1,TRAIN1,ROUTE2,POS1), stopping(TIME, TRAIN2, DES), to(ROUTE1, DES), from(ROUTE2, DES), 
   train(TRAIN1), train(TRAIN2), route(ROUTE1), route(ROUTE2), time(POS1), time(POS2), route(DES), time(TIME).
:- stopping(TIME, TRAIN1, STATION), stopping(TIME+1, TRAIN2, STATION), station(STATION), time(TIME), train(TRAIN1), train(TRAIN2).
:- moving(FIN, TRAIN, ROUTE, DUR), final(FIN), time(DUR), train(TRAIN), route(ROUTE).
:- stopping(FIN, TRAIN, STATION), final(FIN), train(TRAIN), station(STATION).
:- CINI!=CFIN, park(STAT), CINI = #count{ TRAIN : parking(1,TRAIN,STATION), train(TRAIN), station(STATION), STATION=STAT },
                           CFIN = #count{ TRAIN : parking(FIN,TRAIN,STATION), train(TRAIN), station(STATION), final(FIN), STATION=STAT }.
:- parking(TIME, TRAIN, STATION), stopping(TIME+1, TRAIN, STATION), parking(TIME+2, TRAIN, STATION), time(TIME), train(TRAIN),
   park(STATION).
linked(A,B) :- A!=B, station(A), station(B), train(TRAIN), time(T1), time(T2), T1<T2, stopping(T1, TRAIN, A), stopping(T2, TRAIN, B).
answer(S) :- S=#count{ A,B : linked(A,B), station(A), station(B), A!=B }.
#maximize{ S : answer(S) }.
ok_direct(A,B) :-  station(A), station(B), direct(A,B), train(TRAIN), time(T1), time(T2), T1<T2, stopping(T1, TRAIN, A), stopping(T2, TRAIN, B),
CNT=#count{ C : stopping(T3, T, C), T3>T1, T3<T2, time(T3), station(C), train(T), T=TRAIN }, CNT=0.
:- direct(A,B), not ok_direct(A,B).
interval(TRAIN, A, START, STOP) :- station(A), station(B), min_conn(A,B,K), stopping(START, TRAIN, A), train(TRAIN), time(START), time(STOP), 
        STOP=#min{ TIME : time(TIME), TIME>START, stopping(TIME, TRAIN, A) ; FIN : final(FIN) }.
:-  min_conn(A,B,K), station(A), station(B), K>C, C=#count{ START, TRAIN : interval(TRAIN, A, START, STOP ),   
 train(TRAIN), time(START), time(STOP), stopping(STOPTIME, TRAIN, B), time(STOPTIME), STOPTIME>START, STOPTIME<STOP}.
interval(TRAIN, A, START, STOP) :- station(A), station(B), pathReq(A,B,ID), stopping(START, TRAIN, A), train(TRAIN), time(START), time(STOP), 
        STOP=#min{ TIME : time(TIME), TIME>START, stopping(TIME, TRAIN, A) ; FIN : final(FIN) }.
in_path( TRAIN, A, B, START, STOP) :- train(TRAIN), pathReq(A,B,ID), station(A), station(B), interval(TRAIN, A, START, MAXRANGE), 
         STOP=#min{ STP : stopping(STP, TRAIN, B), STP>START, STP<=MAXRANGE }.
