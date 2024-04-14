
from pyscipopt import Model
import pyscipopt

from dataObjects import Person, Assignment
from visualize import visualizeAssignment
from matrixUtils import *


import numpy as np
import scipy.sparse as sp


from typing import List

def optimize():
    """
    TODO: add arguments and describe
    """


    h1 = Person("Petr Brož", "jokerit", "matfyz", presence = np.array([1]*10 + [0]*4))
    h2 = Person("Jan Macháň", "jokerit", "matfyz")
    h3 = Person("Kateřina Bímová", presence = np.array([0]*2 + [1]*12))
    h4 = Person("Matěj Břeň", "jokerit")
    h5 = Person("Eliška Byrtusová")
    h6 = Person("Kateřina Čížková", "matfyz", presence = np.array([0]*7 + [1]*7))
    h7 = Person("David Pokorný", "jokerit")
    h8 = Person("Eliška Jača", "matfyz")
    h9 = Person("Nováček první", "jokerit", presence = np.array([0]*4 + [1]*4 + [0]*6))
    h10 = Person("Nováček druhý")

    personList = [h1, h2, h3, h4, h5, h6, h7, h8, h9, h10]

    attributeList = ["human", "jokerit", "matfyz"]

    defaultVector = np.append([0], np.ones(13))
    weightsList = [defaultVector.copy(), defaultVector.copy(), defaultVector.copy()]

    personCount = len(personList)


    penaltyVector = 0.1*np.array([15, 7, 3])

    CCPM = vojtaToCoCoPenaltyMatrix("tabory_ucastnici.xlsx", personList, penaltyVector)

    
    DSM, DAM_list = calculateDailyMatrices(personList, attributeList)
    DIM = DSM/4 #daily ideal matrix. Holds ideal ammount of people and attributes per company per day

    print(DSM)

    model = Model("companies")



    #   MEMBERSHIP
    MM = np.empty((4, personCount), dtype= pyscipopt.Variable)
    for i in range(4):
        for j in range(personCount):
            MM[i,j] = model.addVar(name = f"Membership_{i}_{j}", vtype = 'B')

    #add constaraint: each person is a member of exactly one company
    print(MM)
    msums = np.ones((1, 4)) @ MM
    msums = msums[0]    #discard first axis of resulting 1 by personcount matrix
    for i in range(personCount):
        model.addCons(msums[i] == 1)



    #  ABSOLUTE ATTRIBUTE ERRORS
    AAEM_list = []
    for i, DAM in enumerate(DAM_list):
        # for each attribute, calculate AEM = attribute error matrix.  
        # AEM is a 4 by 14 matrix where each cell is that company's error from the ideal (=DIM) on that day for that attribute.
        # Since the first attribute is always the "human" attribute, the first AAEM effectively shows errors in manpower.

        AEM = MM @ DAM - np.tile(DIM[i, :], (4,1))

        #AAEM = model.addMVar(shape = (4,14), name = f"absolute_error_{attributeList[i]}")
        
        # introduce absolute attribute error matrix variable
        AAEM = np.empty((4,14), dtype=pyscipopt.Variable)
        for compI in range(4):
            for day in range(14):
                AAEM[compI, day] = model.addVar(name = f"abs_err_{attributeList[i]}_{compI}_{day}")
                # enforce absolute value via constraints
                model.addCons(    AEM[compI, day] <= AAEM[compI, day])
                model.addCons(-1* AEM[compI, day] <= AAEM[compI, day])

        AAEM_list.append(AAEM)


    #  SHARED COMPANY MATRIX
    #       used for tracking whether two persons are assigned to the same company this year.
    #       just a fancy name for prepared products of columns of MM
    SCM = np.empty((personCount,personCount), dtype=pyscipopt.Expr)

    for i in range(personCount):
        for j in range(i, personCount):
            ex = np.ones((1,4)) @ (MM[:, i] * MM[:, j])
            ex = ex[0]
            SCM[i,j] = ex
            SCM[j,i] = ex




    #sum of penalties for sharing companies with people they have shared companies with previously
    CCPsum = 0
    for i in range(personCount):
        for j in range(i, personCount):     #take just lower triangle to avoid doubling
            if CCPM[i,j] != 0:
                penalty = CCPM[i,j] * np.sum(personList[i].presence * personList[j].presence)
                CCPsum += SCM[i,j] * penalty


    #weighed sum of absolute attribute errors
    AAEsum = 0
    for i, AAEM in enumerate(AAEM_list):
        AAEsum += np.ones((1,4)) @ AAEM @ weightsList[i]


    cost = AAEsum #+ CCPsum
    cost = cost[0]

    objVar = model.addVar(name = "objectiveVariable")
    model.addCons(objVar >= cost)

    model.setObjective(objVar)

    model.optimize()

    MM_val = np.empty((4, personCount), dtype=int)
    for i in range(4):
        for j in range(personCount):
            MM_val[i,j] = round(model.getVal(MM[i,j]))

    print("MM_val:")
    print(MM_val)

    SCM_val = np.zeros((personCount,personCount), dtype=int)
    for i in range(personCount):
        for j in range(personCount):
            SCM_val[i,j] = model.getVal(SCM[i,j])

    result = Assignment(personList, MM_val, SCM_val)


    visualizeAssignment(result, attributeList, CCPM)



        

if __name__ == "__main__":
    optimize()