'''
Created on 11 mar 2019

@author: redsnic 

calls the solver for the MiniZinc model execution and prints the output 
''' 
import MinizincHelper
from InputReader import InputReader 

def pretty_printer(answer, Reader):
    out = ""
    for train in range(len(answer["Stopping"][0])):
        for time in range(len(answer["Stopping"])):
            if int(answer["Stopping"][time][train]) > 0:
                out += ("(" + str(time+1) + ", " + str(train+1) + ", '" + Reader.translate(answer["Stopping"][time][train]) + "', 'STOPS')\n" )
            elif int(answer["Moving"][time][train]) > 0:
                out += ("(" + str(time+1) + ", " + str(train+1) + ", '" + Reader.translateRoute(answer["Moving"][time][train]) + "', 'MOVES')\n" )
            elif int(answer["Parking"][time][train]) > 0:
                out += ("(" + str(time+1) + ", " + str(train+1) + ", '" + Reader.translate(answer["Parking"][time][train]) + "', 'PARKS')\n" )
    out += "ANS := " + str(answer["ans"]) + "\n"
    return out


import sys
import time


if __name__ == "__main__":
    startTime = int(round(time.time() * 1000))

    M = MinizincHelper.MinizincHelper("mzn/Treni.mzn") # load mzn encoding
    Reader = InputReader()
    M.addInput(Reader.prepareMINIZINCLines(Reader.time))
    print("executing...")
    #M.printProgram()
    M.run()
    Dict = M.returnOut()
    M.printOut()

    f = open(sys.argv[1]+".solMZN", "w")
    
    try:
        resp = pretty_printer( Dict[len(Dict)-1], Reader )
        f.write(resp)  
    except Exception:
        f.write("No solutions or Error\n") # one of: No solution, OUT_OF_RAM, model error

    stopTime = int(round(time.time() * 1000))
    f.write("Execution Time: " + str(stopTime-startTime))

    f.close()