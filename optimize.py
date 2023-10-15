from person import Person
from visualize import plotSolutions

import numpy as np
import scipy.sparse as sp
import gurobipy as gp
from gurobipy import GRB

from typing import List

def dailySumMatrix(personList : List[Person], attributeList):
    """
    arguments:
    personList : list of all people
    attributeList : list of strings. Specified attribtes will be taken into account.
    ---------------
    returns:
    A 1+x by 14 numpy matrix. 
    First row holds the sum of people present on each day
    Following rows hold sums of attributes present on each day, in same order as given in attributeList
    """

    dsm = np.zeros((1+len(attributeList), 14))
    for day in range(14):
        for p in personList:
            pres = p.presence[day]
            dsm[0,day] += pres
            if pres:
                for i, attribute in enumerate(attributeList):
                    dsm[1+i, day] += p.get(attribute)*pres
    return dsm

def dailyPresenceMatrix(personList : list[Person]):
    """
    returns a  len(personList) by 14 matrix whose rows are person presence vectors. 
    """
    vl = []
    for p in personList:
        vl.append([p.presence])
    DPM = np.block(vl)
    return DPM


def optimize():
    """
    TODO: add arguments and describe
    """

    pa = Person("Ales", "jokerit", "matfyz")
    pb = Person("Bara", "matfyz", presence = np.block([np.ones(7), np.zeros(7)]))
    pc = Person("Cyril", "jokerit", presence= np.block([np.zeros(3), np.ones(5), np.zeros(6)]))
    pd = Person("Debil", "jokerit", presence=np.block([np.zeros(7), np.ones(7)]))
    pe = Person("Emil", "jokerit", "matfyz", "pěstební dělník", presence=np.block([np.zeros(2), np.ones(12)]))
    pf = Person("Fiona", presence=np.block([np.ones(4), np.ones(6), np.zeros(4)]))

    tabor = [pa, pb, pc, pd, pe, pf]

    personCount = len(tabor)

    DSM = dailySumMatrix(tabor, ["jokerit", "matfyz"])
    DIM = DSM/4 #daily ideal matrix. Holds ideal ammount of people and attributes per company per day
    DPM = dailyPresenceMatrix(tabor)

    model = gp.Model("druzinky")

    m = model.addMVar(shape=(4,personCount), vtype=GRB.BINARY, name="membership")    #membership of persons in companies. Main decision variable

    #   MANPOWER
    aem = model.addMVar(shape=(4,14), name="absolute_error_membership")              #absolute error from optimal manpower 
    reps_temp = [0]*DIM.shape[0]
    reps_temp[0] = 4

    #add constraint: aem = |manpower - optimal_manpower|
    for compI in range(4):
        for day in range(14):
            thisDayManpower = m[compI,:] @ DPM[:, day]
            diff = thisDayManpower - DIM[0, day]
            model.addLConstr( diff, GRB.LESS_EQUAL, aem[compI, day])
            model.addLConstr(-diff, GRB.LESS_EQUAL, aem[compI, day])















        

if __name__ == "__main__":
    optimize()