'''
Created on 11 mar 2019

@author: redsnic 

calls the solver for the MiniZinc model execution and prints the output 
''' 

import MinizincHelper
from InputReader import InputReader 
import sys
import time


if __name__ == "__main__":
    startTime = int(round(time.time() * 1000))

    M = MinizincHelper.MinizincHelper("mzn/Treni.mzn") # load mzn encoding
    Reader = InputReader()
    M.addInput(Reader.prepareMINIZINCLines(Reader.time))
    print("executing...")
    #M.printProgram()
    dic = M.runBenchmark(1, "Moving", type_var="int",mode="maximize ans", options="all")