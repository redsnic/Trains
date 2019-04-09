'''
Created on 17 dic 2018

@author: redsnic
'''

import fileinput
from subprocess import call
 
class ClingoInterface(object):
    '''
    Interfaccia per l'uso semplificato di clingo 
    permette di generare direttamente in python input e programma
    e di sfruttarlo per maneggiare l'output
    '''
    def addPredicateType(self, name, arity):
        '''
        Aggiunge un predicato alla lista di quelli possibili
        --- si potrebbe anche automatizzare ---
        '''
        try:
            self.predicates[name+"/"+str(arity)]
            print("Error: name " + name + " defined multiple times!")
        except KeyError:
            self.predicates[name+"/"+str(arity)] = (arity, [])
    
    def addFact(self, name, params):
        '''
        Aggiunge un fatto relativo ad uno specifico predicato
        --- l'arita' e' estratta automaticamente ---
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
        prepara l'header con il nome del programma
        '''
        if self.name == "":
            return ""        
        header =  "".join(["%" for _ in range(8+len(self.name))]) + "\n"
        header += "%%% " + self.name + " %%%\n"
        header += "".join(["%" for _ in range(8+len(self.name))]) + "\n"
        return header
    
    def _prepareDescription(self):
        '''
        prepara l'header con la descrizione del programma
        '''
        if self.description == "":
            return ""
        header = "% Description:\n"
        for line in self.description.split("\n"):
            header += "% "+ line + "\n" 
        return header

    def _packText(self):
        '''
        prepara il testo completo del programma ASP per l'esecuzione con clingo
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
        preleva il nome da un predicato di ouput estratto dal testo di clingo
        '''
        return pred[:pred.find("(")]
    
    def _getvals(self, pred):
        '''
        preleva la lista degli argomenti di un predicato di output 
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
        

    def run(self):
        '''
        Execute clingo and store answers 
        '''
        program_text = self._packText()
        outfile = open(self.filename, "w")
        outfile.write(program_text)
        outfile.close()
        print("grounding + solving...")
        call(["clingo", "-t", "8", self.filename], stdout=open("temOut.ans", 'wb'))
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
    
        
        
        