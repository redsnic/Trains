


from InputReader import InputReader

class ASPHelper():

    def toDot(self):
        print("digraph G{")
        print("\n".join([x for x in self.stationsNames]))
        for a, l in self.adjList.items():
            for b, w in l.items():
                print( a + "->" + b + " [label=\""+str(len(w))+" ; "+ str(w[0]) +"\"]")
        print("}")
 
    def addReverse(self):
        for a, l in self.adjList.items():
            for b, x in l.items():
                try:
                    self.adjList[b]
                except KeyError:
                    self.adjList[b] = {}
                self.adjList[b][a] = x

    def expandStations(self):
        for (station, capacity) in self.stationsNames:
            # STOP IN and STOP OUT are used to force stop after exiting the park and to avoid trains that moves from stop to park multiple times
            try :
                self.adjList[station]
            except KeyError:
                self.adjList[station] = {}
            
            if int(capacity) > 0:

                self.adjList[station+"_stopIN"]  = self.adjList[station].copy()  # new stop node copy of station transit node
                self.adjList[station+"_stopOUT"] =  self.adjList[station].copy() # new stop node copy of station transit node
                
                self.adjList[station+"_stopIN"][station+"_park"] = [1]

                self.adjList[station+"_park"] = {}                                               # new park node
                self.adjList[station+"_park"][station+"_park"] = [1 for _ in range(int(capacity))]    # self loop (up to capacity trains) 
                self.adjList[station+"_park"][station+"_stopOUT"] = [1]                          # back to stop

                self.adjList[station][station+"_stopIN"] = [1]                # add transit node to stop edge
            else:
                # if there is not a paking there is no need to add it
                self.adjList[station+"_stopIN"]  = self.adjList[station].copy()  # new stop node copy of station transit node
                self.adjList[station][station+"_stopIN"] = [1]                   # add transit node to stop edge
            
        old = [x for x in self.stationsNames]
        for (station, capacity) in old:
            self.stationsNames.append( (station+"_stopIN",0) )
            self.stationsNames.append( (station+"_stopOUT",0) )
            self.stationsNames.append( (station+"_park",0) )

        self.stationsNames = [ x for (x,_) in self.stationsNames ] # keep only names


    def __init__(self):
        IN = InputReader()

        self.stationsNames   = IN.stations
        self.adjList  = IN.adjList
        self.addReverse()
        # add additional nodes for station management  
        self.expandStations()
        
        # read time
        self.time    = IN.time
        
        # prepare requests
        self.directReqs = IN.directReqs
        self.minReqs    = IN.minReqs
        self.linkReqs   = IN.linkReqs

if __name__=="__main__":
    print("test")