include "globals.mzn";

%-- PARAMETERS

par int: maxTrains;
par int: nRoutes;

par int: nStations;
par int: Final;

%-- SETS

set of 1..nStations:STATIONS=1..nStations;
set of 1..nRoutes:ROUTES=1..nRoutes;
set of 1..Final:TIME=1..Final;
set of 1..maxTrains:TRAINS=1..maxTrains;

%-- PARAM ARRAYS

array [ROUTES] of STATIONS:From;
array [ROUTES] of STATIONS:To;
array [ROUTES] of ROUTES:Id;
array [ROUTES] of int:Length;
array [STATIONS, ROUTES] of bool: Connected;
array [STATIONS] of int: Capacities;
array [STATIONS] of bool: WithParking;
array [STATIONS,STATIONS] of bool: Directs;
array [STATIONS,STATIONS] of int: Min;
 

%-- VARS
% choose the number of used trains
var 1..maxTrains: usedTrains;
constraint (usedTrains>0 /\ usedTrains<=maxTrains);

array [TIME, TRAINS] of var 0..nStations: Parking;
array [TIME, TRAINS] of var 0..nStations: Stopping;
array [TIME, TRAINS] of var 0..nRoutes: Moving;
array [TIME, TRAINS] of var 0..Final: Distance;


%#INPUT#%
Final=10;
nStations=2;
maxTrains=1;
Capacities=[1,0];
WithParking=[true,true];
nRoutes=4;
From=[1,2,1,2];
To=[2,1,2,1];
Length=[0,0,0,0];
Id=[1,1,2,2];
Connected=[|true,false,true,false|false,true,false,true|];
%#INPUT#%

% do not use more than usedTrains 
constraint forall(time in TIME, train in TRAINS)
      ((train > usedTrains)->(Parking[time,train] = 0 /\
        Stopping[time,train] = 0 /\
        Moving[time,train] = 0 /\ 
        Distance[time, train] = 0));

% constraint the trains to be in a single place at a time
constraint forall(time in TIME, train in TRAINS)
      ((train <= usedTrains)->(Stopping[time,train]>0 <-> Parking[time,train]=0 /\ Moving[time,train]=0));
constraint forall(time in TIME, train in TRAINS)
      ((train < usedTrains)->(Parking[time,train] >0 <-> Stopping[time,train]=0 /\ Moving[time,train]=0));
constraint forall(time in TIME, train in TRAINS)
      ((train <= usedTrains)->(Moving[time,train] >0 <-> Parking[time,train]=0 /\ Stopping[time,train]=0));
constraint forall(time in TIME, train in TRAINS)
      ((train <= usedTrains)->(Stopping[time,train] > 0 -> Distance[time,train] = 0));
constraint forall(time in TIME, train in TRAINS)
      ((train < usedTrains)->(Parking[time,train] > 0 -> Distance[time,train]  = 0));
constraint forall(time in TIME, train in TRAINS)
      ((train <= usedTrains)->(Distance[time,train] = 0 <-> Moving[time,train]  = 0));      
      
% movment constraints

constraint forall(time in 1..Final-1, train in TRAINS)
    ((train <= usedTrains)->(
       Parking[time,train] > 0 -> ((Parking[time+1,train] = Parking[time,train]) \/ (Stopping[time+1,train] = Parking[time,train]))
    ));      

constraint forall(time in 1..Final-1, train in TRAINS)
    ((train <= usedTrains)->(
       Stopping[time,train] > 0 -> ((Parking[time+1,train] = Stopping[time,train]) \/
                             exists(r in ROUTES where Connected[Stopping[time,train], r] /\ time+Length[r]<Final)
                                   (Moving[time+1,train] = r /\ Distance[time+1,train] = 1))
    ));                     
      
constraint forall(time in 1..Final-1, train in TRAINS)
    ((train <= usedTrains)->(
       Moving[time,train] > 0 -> 
                          if Distance[time,train] < Length[Moving[time,train]] then 
                                       Moving[time+1,train]=Moving[time,train]   /\ Distance[time+1,train]  = Distance[time,train]+1 
                          else 
                                (exists(r in ROUTES where Connected[To[Moving[time,train]], r] /\ time+Length[r]<Final)
                                      (Moving[time+1,train] = r /\ Distance[time+1,train] = 1)) 
                                \/ (Stopping[time+1,train] = To[Moving[time,train]]) 
                          endif
    ));  



% not too many trains in any park
constraint forall(time in TIME, station in STATIONS)
           (sum(train in TRAINS)(Parking[time,train]==station) <= Capacities[station]);

% stating conf = stop conf
constraint forall(station in STATIONS)
           (sum(train in TRAINS)(Parking[1, train]==station) == sum(train in TRAINS)(Parking[Final, train]==station));                         
    
% starting configuration    
constraint forall(train in TRAINS)
           ((train<=usedTrains)->(exists(station in STATIONS)(Parking[1, train]=station /\ Capacities[station]>0)));      

% cannot have another train stopping at a station or another train passing by it within the next time unit a train stopped at this station
constraint forall(time in TIME, t1 in TRAINS)
                 (Stopping[time,t1] > 0 -> not exists(t2 in TRAINS)( t1!=t2 /\ Moving[time,t2] > 0 /\ Distance[time,t2] == 1 /\ From[Moving[time,t2]] == Stopping[time,t1]));
constraint forall(time in TIME, t1 in TRAINS)
                 (Stopping[time,t1] > 0 -> not exists(t2 in TRAINS)( t1!=t2 /\ Stopping[time,t1] == Stopping[time+1,t2]));
                      

% cannot have two trains leaving a station at the same time
constraint forall(time in TIME, t1 in TRAINS)
                 (Moving[time,t1] > 0 -> not exists(t2 in TRAINS)( t1!=t2 /\ From[Moving[time,t1]] == From[Moving[time,t2]] /\ Distance[time,t1] == Distance[time,t2] /\ Distance[time,t1] == 1 ));


% cannot have two trains at the same station at the same time 
constraint forall(time in TIME)(alldifferent_except_0(([ Stopping[time,train] | train in TRAINS])));

% cannot have two trains on the same route at the same time
constraint forall(time in TIME)(alldifferent_except_0(([ if Moving[time,train]>0 then Id[Moving[time,train]] else 0 endif | train in TRAINS])));

% a train can enter a deposit only after a move
constraint forall(time in 3..Final, train in TRAINS)
                 ((train <= usedTrains) ->
                      (Parking[time,train] > 0 -> Parking[time-1,train] > 0 \/ (Stopping[time-1,train] > 0 /\ Moving[time-2,train]>0))
                 );


% --- ADDITIONAL REQUESTS

% DIRECTS

constraint forall(a in STATIONS, b in STATIONS)(Directs[a,b] -> 
                                          exists(train in TRAINS, t1,t2 in TIME)
                                                ( t1<=t2 /\ Stopping[t1,train]=a /\ Stopping[t2,train]=b /\ not exists(t3 in TIME)
                                                                                                                ( t3<t2 /\ t3>t1 /\ Stopping[t3,train]>0) )
                                                );


% MINIMUM

constraint forall(a in STATIONS, b in STATIONS)( (Min[a,b] > 0) -> 
                                          Min[a,b]<=sum(train in TRAINS, t1,t2 in TIME)
                                                          (bool2int(t1<=t2 /\ Stopping[t1,train]=a /\ Stopping[t2,train]=b /\
                                                                 ( not exists(t3 in TIME)(t3<t2 /\ t3>t1 /\ (Parking[t3,train]>0 \/ Stopping[t3,train]=a \/ Stopping[t3,train]=b))))));

% PATHS

constraint forall(a in STATIONS, b in STATIONS)( (PathRQ[a,b] > 0) -> 
                                                exists(train in TRAINS, t1,t2 in TIME) 
                                                      (Stopping[t1,train]=a /\ Stopping[t2,train]=b /\ t1<t2 /\
                                                      (forall(inter in STATIONS)
                                                             ( (Services[PathRQ[a,b],inter]=1) -> exists(t3 in TIME)
                                                                                                    (Stopping[t3,train]=inter /\ t3>t1 /\ t3<t2)))));

% additional cuts
constraint forall(a in STATIONS, b in STATIONS)( (PathRQ[a,b] > 0) -> 
                                                exists(train in TRAINS, t1,t2 in TIME) 
                                                      (Stopping[t1,train]=a /\ Stopping[t2,train]=b /\ t1<t2));

constraint forall(idt in 1..idLimit, inter in STATIONS)( (Services[idt,inter]=1) -> exists(train in TRAINS, t in TIME)(Stopping[t,train]=inter));

% OBJ function


array [STATIONS, STATIONS] of var bool: Linked;
constraint forall(s in STATIONS)(not Linked[s,s]);
constraint forall(s1,s2 in STATIONS)
  (
    (s1!=s2) -> ( (not exists(train in TRAINS, t1,t2 in TIME)
                             (t1<t2 /\ Stopping[t1,train]>0 /\ Stopping[t1,train]==s1 /\ Stopping[t2,train]==s2)) -> not Linked[s1,s2])
  );


var int: ans;
constraint ans = sum(Linked);
solve maximize ans;







 


