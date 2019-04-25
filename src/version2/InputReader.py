'''
Created on 18 feb 2019

@author: redsnic
'''

from sys import stdin

class InputReader(object):
    '''
    Classe per la lettura dell'input e la generazione dei fatti per Minizinc e ASP
    '''
    def addEdge(self, start, stop, weights):
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
        if name in self.stations:
            raise RuntimeError("Station " + name + " defined multiple times")
        self.stations.append((name, capacity))

    def addDirectRequest(self, start, stop):
        #adjust order
        if (start, stop) in self.directReqs:
            raise RuntimeError("Direct from " + start + " to " + stop + " defined multiple times")
        self.directReqs.append((start, stop))
    
    def addMinRequest(self, start, stop, number):
        #adjust order
        if start < stop:
            swap = start
            start = stop
            stop = swap
        for req in self.minReqs:
            if (start, stop, number) == req:
                raise RuntimeError("Minimum number of links already set for route from " + start + " to " + stop)
        self.minReqs.append((start, stop, number))
        
        
    def addLinkRequest(self, start, stop, intermediate):
        #adjust order
        self.linkReqs.append((start,stop,intermediate))
        
    def checkIntegrity(self):
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
        Print input in dot format
        '''
        # graph
        print("DOT format graph:")
        print("graph G {")
        #    nodes
        for (name, capacity) in self.stations:
            print(name + ' [label="' + name + ": " + capacity + '"]')
        #    edges
        for start, stopDict in self.adjList.items():
            for stop, weights in stopDict.items():
                if len(weights) == 2:
                    print(start + " -- " + stop + ' [label="' + str(weights[0]) + "/" +  str(weights[1]) + '"] [splines=false] [color="black:invis:black"]')
                else:
                    print(start + " -- " + stop + ' [label="' + str(weights[0]) + '"] [splines=false]')
        print("}")
        # requests
        #    directs
        print("* Time Ticks: " + str(self.time))
        print("* Direct train requests:")
        for (start, stop) in self.directReqs:
            print("from " + start + " to " + stop)
        #    minimum
        print("* minimum links for two stations:")
        for (start, stop, num) in self.minReqs:
            print(str(num) + " trains from " + start + " to " + stop )
        #    links
        print("* tours requested:")
        for (start, stop, l) in self.linkReqs:
            print("from " + start + " to " + stop + " passing by " + " ".join(l))  
    
    
    # ASP (V3)
    def prepareASPLinesV3(self, time):
        l = [] 
        
        l.append("time(1.."+str(time)+").")
        l.append("final("+str(time)+").")
        l.append("station(1.." + str(len(self.stations)) + ").")
        l.append("usable_trains(1.." +  str(sum([ int(y) for (_,y) in self.stations ]))  + ").")
        
        # capacities
        ind = 1
        for el in [ y for (_,y) in self.stations]:
            l.append("capacity(" + str(ind) + "," + str(el) + ").")
            if int(el) > 0:
                l.append("park(" + str(ind) + ").")
            else:
                l.append("stop_only(" + str(ind) + ").")
            ind+=1

        # come stop (evito conversioni in caso)
        fromList = [] 
        toList = [] 
        lenList = []
        IDList = []
        
        self.routes = []
        identifier = 1
        # prepare lists
        for i in range(len(self.stations)):
            for j in range(i+1,len(self.stations)):
                for k in range(2):
                    try:
                        lenList.append(self.adjList[max(self.stations[i][0],self.stations[j][0])][min(self.stations[i][0],self.stations[j][0])][k]/5)
                        lenList.append(self.adjList[max(self.stations[i][0],self.stations[j][0])][min(self.stations[i][0],self.stations[j][0])][k]/5)
                        fromList.append(i+1)
                        toList.append(j+1)
                        IDList.append(identifier)
                        fromList.append(j+1)
                        toList.append(i+1)
                        IDList.append(identifier)
                        self.routes.append(str(i+1) +"->"+ str(j+1))
                        self.routes.append(str(j+1) +"->"+ str(i+1))
                        identifier += 1
                    except KeyError:
                        pass
                    except IndexError:
                        pass
                            
        
        for i in range(len(fromList)):
            l.append("route(" + str(i+1) + ").")
            l.append("from(" + str(i+1) + "," + str(fromList[i]) +").")
            l.append("local_routes(" + str(fromList[i]) + "," + str(i+1) + ").")  # e' possibile partire per una tratta che parte dalla posizione indicata (stazione, tratta)
            l.append("to(" + str(i+1) + "," + str(toList[i]) +").")
            l.append("len(" + str(i+1) + "," + str(lenList[i]) +").")
            l.append("id(" + str(i+1) + "," + str(IDList[i]) +").")
        
        
        stationNameTranslator = {}
        ind = 1
        for s in self.stations:
            stationNameTranslator[s[0]] = ind
            ind += 1
        
        for direct in self.directReqs:
            l.append("direct(" + str(stationNameTranslator[direct[0]]) +"," + str(stationNameTranslator[direct[1]]) + ").")
            
        for minReq in self.minReqs:
            l.append("min_conn(" + str(stationNameTranslator[minReq[0]]) + "," + str(stationNameTranslator[minReq[1]]) + "," + str(minReq[2]) + ")." )
            
        ind = 1
        self.pathRequests = []
        for pathReq in self.linkReqs:
            dic = {}
            dic["SOURCE"] = str(stationNameTranslator[pathReq[0]])
            dic["DESTINATION"] = str(stationNameTranslator[pathReq[1]])
            dic["STOPS"] = tuple( [str(stationNameTranslator[el]) for el in pathReq[2]] )
            dic["ID"] = str(ind)
            l.append("pathReq("+ dic["SOURCE"] + "," + dic["DESTINATION"] + "," + str(ind) +").")
            ind+=1
            self.pathRequests.append(dic)
            
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
        
        #READ input
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
    
    
