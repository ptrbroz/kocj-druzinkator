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

def calculateMatrices(personList : List[Person], attributeList : List[str]):
    """
    arguments:
    personList : list of all people
    attributeList : list of strings. Specified attribtes to be taken into account.
    ---------------
    returns:
    DPM : matrix, len(personList) by 14. Daily presence matrix. Contains 1 if person is present on that day, 0 if not.
    DSM : matrix, 1+len(attributeList) by 14. Daily sum matrix. First row contains sums of people present on that day, following
        rows contain sums of attributes present on that day.
    DAM_list : List of len(attributeList) matrices. Each matrix within list has same dimensions as DPM, but each row is multiplied
        by that person's value of corresponding attribute.
    """

    DSM = np.zeros((1+len(attributeList), 14))

    vl = []
    for p in personList:
        vl.append([p.presence])
        DSM[0,:] += p.presence
    DPM = np.block(vl)

    DAM_list = []
    for attr in attributeList:
        DAM = DPM.copy()
        DAM_list.append(DAM)
        for i,p in enumerate(personList):
            aval = p.get(attr)
            DAM[i, :] *= aval

    return DPM, DSM, DAM_list



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
    attributeList = ["jokerit", "matfyz"]
    defaultVector = np.append([0], np.ones(13))
    weighVectorList = [defaultVector.copy(), defaultVector.copy(), defaultVector.copy()]

    personCount = len(tabor)

    DSM = dailySumMatrix(tabor, attributeList)
    DIM = DSM/4 #daily ideal matrix. Holds ideal ammount of people and attributes per company per day
    DPM = dailyPresenceMatrix(tabor)

    model = gp.Model("druzinky")

    M = model.addMVar(shape=(4,personCount), vtype=GRB.BINARY, name="membership")    #membership of persons in companies. Main decision variable

    #   MEMBERSHIP
    msums = np.ones((1, 4)) @ M
    #add constaraint: each person is a member of exactly one company
    model.addConstr(msums == np.ones((1,personCount)))

    #   MANPOWER
    aem = model.addMVar(shape=(4,14), name="absolute_error_manpower")              #absolute error from optimal manpower 
    reps_temp = [0]*DIM.shape[0]
    reps_temp[0] = 4

    manpower = M @ DPM
    ideal_manpower = np.tile(DIM[1,:], (4,1))
    manpower_error = manpower - ideal_manpower

    #add constraint: aem = |manpower - ideal manpower|
    for compI in range(4):
        for day in range(14):
            model.addConstr(    manpower_error[compI, day] <= aem[compI, day])
            model.addConstr(-1* manpower_error[compI, day] <= aem[compI, day])


    for attribute in attributeList:
        #build DAM - daily attribute matrix. Same as DPM, but ones are only present if person is present AND has attribute.
        #if a person's attribute value is fractional, so are the elements in DAM
        DAM = DPM.copy()
        for compI in range(4):
            for day in range(14):







    model.setObjective(np.ones((1, 4)) @ aem @ np.ones((14, 1)))
    model.optimize()









        

if __name__ == "__main__":
    optimize()