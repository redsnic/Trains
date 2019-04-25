'''
Created on 17 dic 2018

@author: redsnic
'''

import fileinput
from subprocess import call
 
class ClingoInterface(object):
    '''
    Interface to the Clingo solver
    Allows python to generate models and solve them with clingo and then manipulate the output
    (allow also to load a model (complete or patrtial) from a separate file)
    '''
    def addPredicateType(self, name, arity):
        '''
        adds a predicate to the header of used predicates (not that important in general if not for facts)
        '''
        try:
            self.predicates[name+"/"+str(arity)]
            print("Error: name " + name + " defined multiple times!")
        except KeyError:
            self.predicates[name+"/"+str(arity)] = (arity, [])
    
    def addFact(self, name, params):
        '''
       adds a fact for a given predicate
        --- arity is automatically extracted ---
        '''
        try:
            if len(params) == self.predicates[name+"/"+str(len(params))][0]:
                self.predicates[name+"/"+str(len(params))][1].append(params)
            else:
                print("Error: predicate not found " + name+"/"+str(len(params)) + "!")
                print("arguments given : " + str(params))
        except KeyError:
            print("Error: prdicate undefined!")    

    def _prepareHeader(self):
        '''
        adds the model name to the header
        '''
        if self.name == "":
            return ""        
        header =  "".join(["%" for _ in range(8+len(self.name))]) + "\n"
        header += "%%% " + self.name + " %%%\n"
        header += "".join(["%" for _ in range(8+len(self.name))]) + "\n"
        return header
    
    def _prepareDescription(self):
        '''
        adds an header with the description of the model
        '''
        if self.description == "":
            return ""
        header = "% Description:\n"
        for line in self.description.split("\n"):
            header += "% "+ line + "\n" 
        return header

    def _packText(self):
        '''
        prepares the model for its solution with clingo 
        '''
        text = self._prepareHeader()
        text+= self._prepareDescription()
        text+= "%%% Input facts:\n" 
        for (name,tup) in self.predicates.items():
            text+= "% " + name + "\n"
            for params in tup[1]:
                text+= name[:name.find("/")] + "(" + ",".join(map(str,params)) + ").\n"
        for line in self.program:
            text += line + "\n"
        return text  
                
    def _getname(self, pred):
        '''
        extract the output predicates
        '''
        return pred[:pred.find("(")]
    
    def _getvals(self, pred):
        '''
        extracts the list of output predicates arguments
        '''
        return pred[pred.find("(")+1:len(pred)-1].split(",")    

    def _prepareAnswers(self, answers):
        '''
        prepare dictionaries to store the answers 
        extracted from clingo's output
        '''
        self.answers = []
        for l in answers:
            self.answers.append({})
            for pred in l:
                if(pred.find("(") != -1):
                    name = self._getname(pred)
                    vals = self._getvals(pred)
                else:
                    name = pred
                    vals = []
                try:
                    self.answers[len(self.answers)-1][name+"/"+str(len(vals))].append(vals)
                except KeyError:
                    self.answers[len(self.answers)-1][name+"/"+str(len(vals))] = []
                    self.answers[len(self.answers)-1][name+"/"+str(len(vals))].append(vals)
                
    def results(self, name, arity, solnum=0):
        '''
        returns a list of the values of the predicate present in the model "solnum"
        '''
        try:
            return self.answers[solnum][name+"/"+str(arity)]
        except KeyError:
            return []
        except IndexError:
            return []
    
    def show(self, name, arity, solnum=0):
        '''
        prints the results for a given predicate
        '''
        print( name + ":" + str(sorted(self.results(name, arity, solnum))) )
        

    def run(self, mode=""):
        '''
        Execute clingo and store answers
        modes: 
        auto  : Select configuration based on problem type
        frumpy: Use conservative defaults
        jumpy : Use aggressive defaults
        tweety: Use defaults geared towards asp problems
        handy : Use defaults geared towards large problems
        crafty: Use defaults geared towards crafted problems
        trendy: Use defaults geared towards industrial problems
        many  : Use default portfolio to configure solver(s)
        '''
        program_text = self._packText()
        outfile = open(self.filename, "w")
        outfile.write(program_text)
        outfile.close()
        print("grounding + solving...")
        if mode == "":
            call(["clingo", "-t", "8", self.filename], stdout=open("temOut.ans", 'wb'))
        else:
            call(["clingo", "-t", "8", "-configuration="+mode, "--time-limit=300", self.filename], stdout=open("temOut.ans", 'wb'))
        f = open("temOut.ans")
        for line in f.readlines():
            print(line)
        print("done!")
        lines = []
        for line in fileinput.input("temOut.ans"):
            lines.append(line)
        lines = lines[3:]
        if lines[0].startswith("UNSATISFIABLE"):
            self.isSat = False
        else:
            self.isSat = True
        answers = []
        i = 0
        while lines[i].startswith("Answer") or  lines[i].startswith("Optimization"):
            if lines[i].startswith("Optimization"):
                i+=1
            else:
                answers.append(lines[i+1].split())
                i+=2
                print(lines[i+1])
        self._prepareAnswers(answers)
        
    def __str__(self):
        '''
        print program
        '''
        return self._packText()
        
    def addDescription(self, description):
        '''
        add description comment to the program
        '''
        self.description = description
        
    def addName(self, name):
        '''
        add program name for comments
        '''
        self.name = name

    def addProgramLine(self, text):
        '''
        ad a line of the program written in ASP
        '''
        self.program.append(text)

    def __init__(self, programPath=None):
        '''
        Constructor
        '''
        self.filename = "temp.lp"
        self.name = ""
        self.description = ""
        self.program = []
        self.predicates = {}
        if programPath != None:
            try:
                for line in fileinput.input(programPath):
                    self.program.append(line) 
            except IOError:
                print("Error: input file error, chec your path")
        
if __name__ == "__main__":
    CI = ClingoInterface()#("/home/redsnic/AI/alfieri_e_torri.lp")
    CI.addPredicateType("cell", 2)
    for i in range(10):
        for j in range(10):
            CI.addFact("cell", [i,j])
    
    CI.addProgramLine("sum(X,Y,Z):- cell(X,Y), Z=X+Y.")
    CI.addProgramLine("#show sum/3.")
    CI.run()
    CI.show("sum", 3)
    
    for t in CI.results("sum", 3):
        print(t[0]+"+"+t[1]+"="+t[2])
    
        
        
        