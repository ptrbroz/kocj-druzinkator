from dataObjects import Person, Assignment
from visualize import visualizeAssignment
from matrixUtils import calculateDailyMatrices

import numpy as np
import scipy.sparse as sp
import gurobipy as gp
from gurobipy import GRB

from typing import List

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

    personList = [pa, pb, pc, pd, pe, pf] 
    attributeList = ["human", "jokerit", "matfyz"]

    defaultVector = np.append([0], np.ones(13))
    weightsList = [defaultVector.copy(), defaultVector.copy(), defaultVector.copy()]

    personCount = len(personList)







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



    #add objective to minimize weighed sum of absolute attribute errors
    expression = 0
    for i, AAEM in enumerate(AAEM_list):
        expression += np.ones((1,4)) @ AAEM @ weightsList[i]

    model.setObjective(expression)

    model.optimize()


    result = Assignment(personList, MM.x)

    visualizeAssignment(result, ["human"])



        

if __name__ == "__main__":
    optimize()