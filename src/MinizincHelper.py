'''
Created on 20 feb 2019

@author: redsnic
'''


# --- from STACK OVERFLOW, set timout for a function

from functools import wraps
import errno
import os
import signal

class TimeoutError(Exception):
    pass

def timeout(seconds=10, error_message=os.strerror(errno.ETIME)):
    def decorator(func):
        def _handle_timeout(signum, frame):
            raise TimeoutError(error_message)

        def wrapper(*args, **kwargs):
            signal.signal(signal.SIGALRM, _handle_timeout)
            signal.alarm(seconds)
            try:
                result = func(*args, **kwargs)
            finally:
                signal.alarm(0)
            return result

        return wraps(func)(wrapper)

    return decorator
# ---------------------------------------

import subprocess 
import json
import os
import itertools
import time

class MinizincHelper(object):
    '''
    class to manage the input and the "execution" of MiniZinc models
    --- for benchmarks the "solve" directive must be unique ad of one line
    --- the section in which to add the arbitrary code must be surrounded by %#INPUT#% (and should be unique)
        the code in this section is removed before the execution and it can be used for testing 
    --- it is possible to load the model by file or to create it directly in python
    '''
    



    def runBenchmark(self, nRip, variables, type_var="int",mode="satisfy", options="default", varChoicheModes = None, constraintChoiceModes = None):
        '''
        run Benchmark over all possible varchoices and constraintchoices
        nRip: number of points for each mode
        variables: varibles field for annotation
        mode: satisfy or maximize/minimize(fobj) 
        '''
        if not (options in ["custom","all","default"]) :
            raise RuntimeError("invalid option: " + options)
        if (varChoicheModes == None or constraintChoiceModes == None) and not (options in ["all","default"] ):
            raise RuntimeError("both varchoiches and constraintchoices must be set")
        
        VarChoiches = ["input_order", "occurrence", "first_fail", "anti_first_fail"]
        VarChoiches+= ["most_constrained", "dom_w_deg", "max_regret", "smallest", "largest"]
        ConstraintChoiches  = ["indomain", "indomain_max", "indomain_median"]
        ConstraintChoiches += ["indomain_min", "indomain_random", "indomain_reverse_split", "indomain_split"]
            
        BenchmarkOutput = {}
    
        if options != "all":
            VarChoiches = varChoicheModes
            ConstraintChoiches = constraintChoiceModes
    
            
        if (options in ["custom","all"]):
            solveLine0 = "solve :: " + type_var + "_search(" + variables + ","
            for vc in VarChoiches:
                solveLine1 = solveLine0 + vc +","
                for cc in ConstraintChoiches:
                    solveLine2 = solveLine1 + cc + ", complete) " + mode + ";"
                    BenchmarkOutput[vc +","+cc] = {}
                    print(vc +","+cc)
                    for _ in range(nRip):
                        try:
                            self.run_timeout(solveLine2)
                        
                            dic = self.returnStatistics()
                            for k, v in dic.items():
                                try:
                                    BenchmarkOutput[vc +","+cc][k]
                                except KeyError:
                                    BenchmarkOutput[vc +","+cc][k] = []
                                BenchmarkOutput[vc +","+cc][k].append(v)
                        except TimeoutError:
                            print("TIMEOUT!")
                            print(self.PID)
                            if self.PID != None:
                                time.sleep(5)
                                self.PID.kill()
                    for key, val in BenchmarkOutput.items():
                        try:
                            print(key + ":\t" + str(val["runtime"][0]))
                        except:
                            print(key + ":\t" + "TIMEOUT!")
                            
        else: # default mode
            solveLine = "solve " + mode + ";" 
            BenchmarkOutput["default"] = {} 
            for _ in range(nRip): 
                self.run(solveLine)
                dic = self.returnStatistics()  
                for k, v in dic.items():
                    try:
                        BenchmarkOutput["default"][k]
                    except KeyError:
                        BenchmarkOutput["default"][k] = []
                    BenchmarkOutput["default"][k].append(v) 
                   
        
        
        self.benchmarkResults = BenchmarkOutput
        return self.benchmarkResults
        
    @timeout(5)
    def run_timeout(self,x):
        self.run(x)

    def addLine(self, line):
        self.program.append(line)
        
    def addInput(self, inputLines):
        self.input = inputLines
        
    def run(self, solveLine=""):
        '''
        Launch minizinc on the current program
        '''
        # input
        f = open("input.mzn", "w")
        # program
        inputspace = False
        for l in self.program:
            if l.startswith("%#INPUT#%") and not inputspace:
                inputspace = True
                # input
                f.write(l+"\n")
                for inLine in self.input:
                    f.write(inLine+"\n")
            elif l.startswith("%#INPUT#%") and inputspace:
                inputspace = False
                f.write(l+"\n")
            elif inputspace:
                pass
            else:
                f.write(l+"\n")

        # solve line
        if solveLine == "":
            f.write(self.solveLine)
        else:
            f.write(solveLine)
        f.close()
        # execution
        self.PID = subprocess.Popen(["minizinc", "--solver", "Gecode", "--output-objective", "-o", "solutions.txt", "-s","--output-mode", "json", "input.mzn"])
        self.PID.wait()
        # output
        self.solutions = []
        self.statistics = {}
        currentSolution = ""
        try:
            f = open("solutions.txt")
            for l in f.readlines():
                # divide solutions
                if(l.startswith('-')):
                    self.solutions.append(json.loads(currentSolution))
                    currentSolution = "" 
                # get statistics
                elif(l.startswith('%%')):
                    name = l[4:l.index(':')]
                    vals = l[l.index(':')+1:].split()
                    if name == "runtime" or name == "solvetime":
                        self.statistics[name] = float(vals[1][1:])
                    else:
                        self.statistics[name] = float(vals[0])
                # read solutions (json format)
                else:
                    currentSolution = currentSolution + l
            if len(self.solutions) == 0:
                print("No solutions?")
            if len(self.solutions) != 0 and len(self.solutions[len(self.solutions)-1]) == 0:
                # remove last element if empty
                self.solutions = self.solutions[0:len(self.solutions)-1]  
            f.close()
            os.remove("solutions.txt")
        except IOError:
            pass
        os.remove("input.mzn")
        
        
    def returnStatistics(self):
        '''
        returns a dictionary containing the statistics of this execution
        '''
        return self.statistics
        
    def returnOut(self):
        '''
        returns a dictionary withe variables value
        '''
        return self.solutions
    
    def printOut(self):
        '''
        print each solution on the stdout
        '''
        if self.solutions != []:
            for lis in self.solutions:
                for key, content in lis.items():
                    print(str(key) + " : " + str(content))
                print("----------")
            print(self.statistics)
    
    def printProgram(self):
        # program
        inputspace = False
        for l in self.program:
            if l.startswith("%#INPUT#%") and not inputspace:
                inputspace = True
                # input
                print(l)
                for inLine in self.input:
                    print(inLine)
            elif l.startswith("%#INPUT#%") and inputspace:
                inputspace = False
                print(l)
            elif inputspace:
                pass
            else:
                print(l)
        

    def __init__(self, coreProgram=""):
        '''
        Constructor: "solve" line must be unique and a single line
        '''
        self.input = []
        self.coreProgramName = coreProgram
        self.program = [];
        inputSpace = False
        if (coreProgram != ""):
            f = open(coreProgram)
            for line in f.readlines():
                if line.startswith("%#INPUT#%") or inputSpace:
                    self.input.append(line.replace("\n", ""))
                    inputSpace = (not inputSpace)
                if line.startswith("solve"):
                    self.solveLine = line
                else:
                    self.program.append(line.replace("\n", ""))
            f.close()
            
if __name__ == "__main__":
    M = MinizincHelper("/home/redsnic/Minizinc/Sudoku.mzn")
    M.run()
    M.printOut()
            
            
            
        