'''
Created on 18 feb 2019

@author: redsnic
'''

from sys import stdin

def gt0(x):
    if x > 0:
        return True
    else:
        return False

class InputReader(object):
    '''
    Class for reading input for the "train" problem.
    It also provides the interfaces to format the input for the MiniZinc and ASP models.
    ###
    INPUT FORMAT
    ###
    timeUnits                                            // a number
    % stations
    ListOfUsedStations [name capacity]                   // capacity is the number of slots that has the station's deposit
    % routes
    ListOfRoutes [source destination len1 <len2>]        // len2 should be present if the route is made of two rails
    % requests                                           // optional
    requestType Args
    direct source destination                            // request a direct from source to destination
    minumum source destination nOfConnections            // request that source and destination are connected at least nOfConnections times
    link source destination [list of intermediate stops] // requests that source and destination are connected by a train that makes the following intermediate stops
    '''
    def translate(self, what):
        '''
        returns the station name from its identifier
        '''
        return self.stationNameDecoder[what-1]

    def translateRoute(self, what):
        '''
        returns the route name from its identifier
        '''
        return self.routes[what-1]

    def addEdge(self, start, stop, weights):
        '''
        adds am edge to the graph describing the rail system
        '''
        if len(weights)>2 or len(weights)==0:
            raise RuntimeError("Error: wrong ammount of weights specified for: " + start + " " + stop)
        if start == stop:
            raise RuntimeError("Error: self loops are not admitted for: " + start + " " + stop)
        # keep lex order
        if start < stop:
            swap = start
            start = stop
            stop = swap
        try:
            self.adjList[start]
            try:
                self.adjList[start][stop]
                raise RuntimeError("Multiple definitions for: "+ start + " " + stop)
            except KeyError:
                # node exists, add edge
                self.adjList[start][stop] = weights
                
        except KeyError:
            # node does not exist, add edge
            self.adjList[start]= {}
            self.adjList[start][stop] = weights
             
    def addStation(self, name, capacity):
        '''
        adds a a station (node) to the rail system (graph)
        '''
        if name in self.stations:
            raise RuntimeError("Station " + name + " defined multiple times")
        self.stations.append((name, capacity))

    def addDirectRequest(self, start, stop):
        '''
        stores a direct request if unique
        '''
        if (start, stop) in self.directReqs:
            raise RuntimeError("Direct from " + start + " to " + stop + " defined multiple times")
        self.directReqs.append((start, stop))
    
    def addMinRequest(self, start, stop, number):
        '''
        adds a minimum connection request if unique
        '''
        if start < stop:
            swap = start
            start = stop
            stop = swap
        for req in self.minReqs:
            if (start, stop, number) == req:
                raise RuntimeError("Minimum number of links already set for route from " + start + " to " + stop)
        self.minReqs.append((start, stop, number))
        
        
    def addLinkRequest(self, start, stop, intermediate):
        '''
        adds a link request 
        '''
        self.linkReqs.append((start,stop,intermediate))
        
    def checkIntegrity(self):
        '''
        checks if the input information are valid
        '''
        if self.time <= 0:
            raise RuntimeError("Wrong time value: " + self.time)
        stationNames = [name for (name, _) in self.stations]
        # check directs
        for (start, stop) in self.directReqs:
            if not(start in stationNames):
                raise RuntimeError("Undefined station: " + start)
            if not(stop in stationNames):
                raise RuntimeError("Undefined station: " + stop)
        # check min connections
        for (start, stop, _) in  self.minReqs:
            if not(start in stationNames):
                raise RuntimeError("Undefined station: " + start)
            if not(stop in stationNames):
                raise RuntimeError("Undefined station: " + stop)
        # check links
        for (start, stop, inter) in self.linkReqs:
            if not(start in stationNames):
                raise RuntimeError("Undefined station: " + start)
            if not(stop in stationNames):
                raise RuntimeError("Undefined station: " + stop)
            for station in inter:
                if not(station in stationNames):
                    raise RuntimeError("Undefined station: " + station)
    
    
    def printer(self):
        '''
        print input informations and description 
        the produced rail system is presented as a .dot formatted graph
        '''
        # graph
        print("DOT format graph:")
        print("graph G {")
        # nodes
        for (name, capacity) in self.stations:
            print(name + ' [label="' + name + ": " + capacity + '"]')
        # edges
        for start, stopDict in self.adjList.items():
            for stop, weights in stopDict.items():
                if len(weights) == 2:
                    print(start + " -- " + stop + ' [label="' + str(weights[0]) + "/" +  str(weights[1]) + '"] [splines=false] [color="black:invis:black"]')
                else:
                    print(start + " -- " + stop + ' [label="' + str(weights[0]) + '"] [splines=false]')
        print("}")
        # requests
        # directs 
        print("Direct train requests:")
        if len(self.directReqs) == 0:
            print("None")
        for (start, stop) in self.directReqs:
            print("from " + start + " to " + stop)
        # minimum
        print("minimum links for two stations:")
        if len(self.minReqs) == 0:
            print("None")
        for (start, stop, num) in self.minReqs:
            print(str(num) + " trains from " + start + " to " + stop )
        # links
        print("tours requested:")
        if len(self.linkReqs) == 0:
            print("None")
        for (start, stop, l) in self.linkReqs:
            print("from " + start + " to " + stop + " passing by " + " ".join(l))  

    
    # ASP (V3)
    def prepareASPLinesV3(self, time):
        '''
        formats the input for the ASP model
        '''
        l = [] # list of lines to be added to the minizinc code 
        
        # general
        l.append("time(1.."+str(time)+").")
        l.append("final("+str(time)+").")
        l.append("station(1.." + str(len(self.stations)) + ").")
        l.append("usable_trains(1.." +  str(sum([ int(y) for (_,y) in self.stations ]))  + ").")
        
        # stations
        ind = 1
        for el in [ y for (_,y) in self.stations]:
            l.append("capacity(" + str(ind) + "," + str(el) + ").")
            if int(el) > 0:
                l.append("park(" + str(ind) + ").")
            else:
                l.append("stop_only(" + str(ind) + ").")
            ind+=1

        fromList = [] 
        toList = [] 
        lenList = []
        IDList = []

        # prepare translators and encodings

        self.stationNameTranslator = {}
        self.stationNameDecoder = []
        ind = 1
        for s in self.stations:
            self.stationNameTranslator[s[0]] = ind
            self.stationNameDecoder.append(s[0])
            ind += 1
        
        self.routes = []
        identifier = 1

        # prepare lists
        for i in range(len(self.stations)):
            for j in range(i+1,len(self.stations)):
                for k in range(2):
                    try:
                        lenList.append(self.adjList[max(self.stations[i][0],self.stations[j][0])][min(self.stations[i][0],self.stations[j][0])][k])
                        lenList.append(self.adjList[max(self.stations[i][0],self.stations[j][0])][min(self.stations[i][0],self.stations[j][0])][k])
                        fromList.append(i+1)
                        toList.append(j+1)
                        IDList.append(identifier)
                        fromList.append(j+1)
                        toList.append(i+1)
                        IDList.append(identifier)
                        self.routes.append(self.translate(i+1) +"->"+ self.translate(j+1))
                        self.routes.append(self.translate(j+1) +"->"+ self.translate(i+1))
                        identifier += 1
                    except KeyError:
                        pass
                    except IndexError:
                        pass
                            
        for i in range(len(fromList)):
            l.append("route(" + str(i+1) + ").")
            l.append("from(" + str(i+1) + "," + str(fromList[i]) +").")
            l.append("local_routes(" + str(fromList[i]) + "," + str(i+1) + ").")  # adjList
            l.append("to(" + str(i+1) + "," + str(toList[i]) +").")
            l.append("len(" + str(i+1) + "," + str(lenList[i]) +").")
            l.append("id(" + str(i+1) + "," + str(IDList[i]) +").")
        
        for direct in self.directReqs:
            l.append("direct(" + str(self.stationNameTranslator[direct[0]]) +"," + str(self.stationNameTranslator[direct[1]]) + ").")
            
        for minReq in self.minReqs:
            l.append("min_conn(" + str(self.stationNameTranslator[minReq[0]]) + "," + str(self.stationNameTranslator[minReq[1]]) + "," + str(minReq[2]) + ")." )
            
        ind = 1
        self.pathRequests = []
        for pathReq in self.linkReqs:
            dic = {}
            dic["SOURCE"] = str(self.stationNameTranslator[pathReq[0]])
            dic["DESTINATION"] = str(self.stationNameTranslator[pathReq[1]])
            dic["STOPS"] = tuple( [str(self.stationNameTranslator[el]) for el in pathReq[2]] )
            dic["ID"] = str(ind)
            l.append("pathReq("+ dic["SOURCE"] + "," + dic["DESTINATION"] + "," + str(ind) +").")
            ind+=1
            self.pathRequests.append(dic)
            
        return l

    
    # MINIZINC
    def prepareMINIZINCLines(self, time):
        '''
        formats the input for the MiniZinc model
        '''
        l = []
        l.append("Final="+ str(time) +";")
        l.append("nStations=" + str(len(self.stations)) + ";")
        l.append("maxTrains=" + str(  sum([ int(y) for (_,y) in self.stations ])) + ";")
        l.append("Capacities=[" + ",".join([ y for (_,y) in self.stations]) + "];")
        l.append("WithParking=[" + ",".join([str(gt0(y)).lower()  for (_,y) in self.stations]) + "];")
        
        fromList = [] 
        toList = [] 
        lenList = []
        IDList = []
        
        self.stationNameTranslator = {}
        self.stationNameDecoder = []
        ind = 1
        for s in self.stations:
            self.stationNameTranslator[s[0]] = ind
            self.stationNameDecoder.append(s[0])
            ind += 1

        self.routes = []
        identifier = 1
        # prepare lists
        for i in range(len(self.stations)):
            for j in range(i+1,len(self.stations)):
                for k in range(2):
                    try:
                        lenList.append(self.adjList[max(self.stations[i][0],self.stations[j][0])][min(self.stations[i][0],self.stations[j][0])][k])
                        lenList.append(self.adjList[max(self.stations[i][0],self.stations[j][0])][min(self.stations[i][0],self.stations[j][0])][k])
                        fromList.append(i+1)
                        toList.append(j+1)
                        IDList.append(identifier)
                        fromList.append(j+1)
                        toList.append(i+1)
                        IDList.append(identifier)
                        self.routes.append(self.translate(i+1) +"->"+ self.translate(j+1))
                        self.routes.append(self.translate(j+1) +"->"+ self.translate(i+1))
                        identifier += 1
                    except KeyError:
                        pass
                    except IndexError:
                        pass
                            
        
        l.append("nRoutes="+ str(len(fromList)) +";")
        l.append("From=[" + ",".join(map(str,fromList)) + "];")
        l.append("To=[" + ",".join(map(str,toList)) + "];")
        l.append("Length=[" + ",".join(map(str,lenList)) + "];")
        l.append("Id=[" + ",".join(map(str,IDList)) + "];")
        
        lines = []
        for i in range(len(self.stations)):
            els = []
            for j in range(len(fromList)):
                if fromList[j] == i+1:
                    els.append("true")
                else:
                        els.append("false")
            lines.append(",".join(els))  
            
        l.append("Connected=[|" + "|".join(lines) + "|];")
        

        DirecReqTable = []
        for i in range(len(self.stations)):
            DirecReqTable.append([])
            for j in range(len(self.stations)):
                DirecReqTable[i].append(False)
        
        for direct in self.directReqs:
            DirecReqTable[self.stationNameTranslator[direct[0]]-1][self.stationNameTranslator[direct[1]]-1] = True
        l.append("Directs=[|" + "|".join([",".join([str(x).lower() for x in y]) for y in DirecReqTable]) + "|];")


        MinReqTable = []
        for i in range(len(self.stations)):
            MinReqTable.append([])
            for j in range(len(self.stations)):
                MinReqTable[i].append(0)

        for minReq in self.minReqs:
            MinReqTable[self.stationNameTranslator[minReq[0]]-1][self.stationNameTranslator[minReq[1]]-1] = minReq[2]
        l.append("Min=[|" + "|".join([",".join([str(x) for x in y]) for y in MinReqTable]) + "|];")
            
        
        ind = 1
        self.pathRequests = []

        pathReqTable = []
        for i in range(len(self.stations)):
            pathReqTable.append([])
            for j in range(len(self.stations)):
                pathReqTable[i].append(str(0)) 

        pathServiceTable = []     

        for pathReq in self.linkReqs:
            dic = {}
            dic["SOURCE"]      = str(self.stationNameTranslator[pathReq[0]])
            dic["DESTINATION"] = str(self.stationNameTranslator[pathReq[1]])
            dic["STOPS"]       = [str(self.stationNameTranslator[el]) for el in pathReq[2]] 
            dic["ID"]          = str(ind)

            pathReqTable[int(dic["SOURCE"])-1][int(dic["DESTINATION"])-1] = dic["ID"]

            service = []
            for i in range(len(self.stations)):
                service.append(False)

            print(dic["STOPS"])
            for i in range(len(self.stations)):
                if str(i+1) in dic["STOPS"]:
                    service[i] = True
                    

            pathServiceTable.append(service)

            ind+=1
            self.pathRequests.append(dic)

        l.append("array [STATIONS, STATIONS] of int: PathRQ;")
        l.append("PathRQ=[|" + "|".join([",".join([str(x).lower() for x in y]) for y in pathReqTable]) + "|];")
        l.append("par int: idLimit="+str(len(pathServiceTable))+";")
        l.append("array [1..idLimit, STATIONS] of int: Services;")
        l.append("Services=array2d(1.."+str(len(pathServiceTable))+", STATIONS,[") 
        lines = []
        for line in pathServiceTable:
            lines.append(",".join([str(k).lower() for k in line]))
        l.append(",".join(lines))
        l.append("]);")  

        return l
        
        
    def __init__(self):
        '''
        Constructor, legge il file di input dallo STDIN
        '''
        self.adjList    = {}
        self.stations   = []
        self.directReqs = []
        self.minReqs    = []
        self.linkReqs   = []
        
        # READ input
        mode = "NOMODESET"
        self.time = -1
        for line in stdin:
            if line.startswith("#") or len(line.split()) == 0:
                continue
            elif mode == "NOMODESET" and self.time == -1 and len(line.split()) == 1:
                self.time = int(line.split()[0])
            elif line.startswith("%"):
                mode = line.split()[1].upper() 
            else: 
                line = [s.upper() for s in line.split()]
                
                if mode == "ROUTES":
                    # Format:     start    stop      weights(max 2)
                    self.addEdge(line[0], line[1], map(int, line[2:]))
                elif mode == "STATIONS":
                    # Format:        name    capacity
                    self.addStation(line[0], line[1])
                elif mode == "REQUESTS":
                    if line[0] == "DIRECT" or line[0] == "D":
                        # Format:              start    stop
                        self.addDirectRequest(line[1], line[2])
                    elif line[0] == "MINIMUM" or line[0] == "M":
                        # Format:           start    stop   no. of connections
                        self.addMinRequest(line[1], line[2], int(line[3]))
                    elif line[0] == "LINK" or line[0] == "L":
                        # Format:           start    stop    list of necessary stops
                        self.addLinkRequest(line[1], line[2],       line[3:])
                    else:
                        raise RuntimeError("Undefined type of request: " + line)
                else:
                    raise RuntimeError("Unknown mode set: " + " ".join(line)) 
                        
        self.checkIntegrity()
    
      
if __name__ == "__main__":
    IN = InputReader()
    IN.printer()
    
    
