'''
Created on 21 feb 2019

@author: redsnic
'''

import matplotlib.pyplot as plt
import pickle

def save_obj(obj, name):
    with open('obj/'+ name + '.pkl', 'wb') as f:
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)

def load_obj(name ):
    with open('obj/' + name + '.pkl', 'rb') as f:
        return pickle.load(f)

if __name__ == '__main__':
    merge = load_obj("mergeListTSP")
    plt.scatter( [ x for (x,_) in merge["solvetime"] ], [ y for (_,y) in merge["solvetime"] ] ) 
    plt.show()