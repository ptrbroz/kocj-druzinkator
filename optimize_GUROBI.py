from dataObjects import Person, Assignment
from visualize import visualizeAssignment
from matrixUtils import *

import numpy as np
import scipy.sparse as sp
import gurobipy as gp
from gurobipy import GRB

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

    model = gp.Model("companies")

    #   MEMBERSHIP
    MM = model.addMVar(shape=(4,personCount), vtype=GRB.BINARY, name="membership")    #membership matrix of persons in companies. Main decision variable
    #add constaraint: each person is a member of exactly one company
    msums = np.ones((1, 4)) @ MM
    model.addConstr(msums == np.ones((1,personCount)))

    #  ABSOLUTE ATTRIBUTE ERRORS
    AAEM_list = []
    for i, DAM in enumerate(DAM_list):
        # for each attribute, calculate AEM = attribute error matrix.  
        # AEM is a 4 by 14 matrix where each cell is that company's error from the ideal (=DIM) on that day for that attribute.
        # Since the first attribute is always the "human" attribute, the first AAEM effectively shows errors in manpower.

        AEM = MM @ DAM - np.tile(DIM[i, :], (4,1))

        print(np.tile(DIM[i, :], (4,1)))

        # introduce absolute attribute error matrix variable
        AAEM = model.addMVar(shape = (4,14), name = f"absolute_error_{attributeList[i]}")
        # enforce absolute value via constraints
        for compI in range(4):
            for day in range(14):
                model.addConstr(    AEM[compI, day] <= AAEM[compI, day])
                model.addConstr(-1* AEM[compI, day] <= AAEM[compI, day])

        AAEM_list.append(AAEM)

    #  SHARED COMPANY MATRIX
    #       used for tracking whether two persons are assigned to the same company this year.
    #       just a fancy name for prepared products of columns of MM
    SCM = np.empty((personCount,personCount), dtype=gp.MQuadExpr)

    for i in range(personCount):
        for j in range(i, personCount):
            SCM[i,j] = np.ones((1,4)) @ (MM[:, i] * MM[:, j])
            SCM[j,i] = SCM[i,j]







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


    cost = AAEsum + CCPsum

    model.setObjective(cost)
    #model.setParam('OutputFlag', False)
    model.update()
    model.printStats()
    model.optimize()


    print(SCM[0,0])
    print(SCM[0,0].item())



    SCM_val = np.zeros((personCount,personCount))
    for i in range(personCount):
        for j in range(personCount):
            SCM_val[i,j] = SCM[i,j].item().getValue()

    print(SCM_val)

    result = Assignment(personList, MM.x, SCM_val)


    visualizeAssignment(result, attributeList, CCPM)



        

if __name__ == "__main__":
    optimize()