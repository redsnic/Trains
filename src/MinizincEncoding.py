'''
Created on 11 mar 2019

@author: redsnic
''' 
from MinizincHelper import MinizincHelper
from InputReader import InputReader 


if __name__ == "__main__":
    M = MinizincHelper("/home/redsnic/Minizinc/Treni.mzn")
    Reader = InputReader()
    M.addInput(Reader.prepareMINIZINCLines(13))
    print("executing...")
    M.printProgram()
    M.run()
    Dict = M.returnOut()
    M.printOut()
    
    s = ""
    for line in Dict[len(Dict)-1]["Linked"]:
        for el in line:
            if el == True:
                s+="1 "
            else:
                s+="0 "
        s+="\n"
    print(s)
    
    s=""
    for time in Dict[len(Dict)-1]["Stopping"]:
        for train in time:
            for el in train:
                if el == True:
                    s+="1 "
                else:
                    s+="0 "
            s+="\n"
        s+="\n"
    print(s)          