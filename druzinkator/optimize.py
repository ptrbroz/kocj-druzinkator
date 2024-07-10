
from pyscipopt import Model
import pyscipopt

from .dataObjects import *
from .visualize import visualizeAssignment
from .matrixUtils import *


import numpy as np
import scipy.sparse as sp


from typing import List

def optimize(problem : Problem, oldAssignment : Assignment = None, maxtime = None) -> Assignment:
    """
    Finds optimal assignment to companies according to people, constraints, weighs etc. described by problem.
    If the oldAssignment argument is set, then assignments present in oldAssignment will be fixed.
    """

    personList = problem.personList
    personDict = problem.personDict
    personCount = len(personList)

    attributeList = problem.attributeList
    attributeDict = problem.attributeDict

    attributeLimits = problem.attributeLimitsList

    personalCouplingList = problem.personalCouplingList

    weightsList = problem.AAEweighs
    CCPM = problem.CCPM

    DSM, DAM_list = calculateDailyMatrices(personList, attributeList)
    DIM = DSM/4 #daily ideal matrix. Holds ideal ammount of people and attributes per company per day

    model = Model("companies")

    #   MEMBERSHIP
    MM = np.empty((4, personCount), dtype= pyscipopt.Variable)
    for i in range(4):
        for j in range(personCount):
            MM[i,j] = model.addVar(name = f"Membership_{i}_{j}", vtype = 'B')

    #add constaraint: each person is a member of exactly one company
    msums = np.ones((1, 4)) @ MM
    msums = msums[0]    #discard first axis of resulting 1 by personcount matrix
    for i in range(personCount):
        model.addCons(msums[i] == 1)

    #add constraints: persons which are already assigned in oldAssignment remain in their respective companies.
    for j in range(personCount):
        companyFix = problem.companyFixList[j]
        if companyFix is not None:
            model.addCons(MM[companyFix, j] == 1)   
            print(f"NEWCONS MM @ {companyFix}, {j} == 1")

    #  precalculate attribute sum matrices
    ASM_list = []
    for i, DAM in enumerate(DAM_list):
        ASM = MM @ DAM 
        ASM_list.append(ASM)


    #  ABSOLUTE ATTRIBUTE ERRORS
    AAEsum = 0

    for i, DAM in enumerate(DAM_list):
        # for each attribute, calculate AEM = attribute error matrix.  
        # AEM is a 4 by 14 matrix where each cell is that company's error from the ideal (=DIM) on that day for that attribute.
        # Since the first attribute is always the "human" attribute, the first AAEM effectively shows errors in manpower.

        if weightsList[i] is None:
            continue

        AEM = ASM_list[i] - np.tile(DIM[i, :], (4,1))

        #AAEM = model.addMVar(shape = (4,14), name = f"absolute_error_{attributeList[i]}")
        
        # introduce absolute attribute error matrix variable
        AAEM = np.empty((4,14), dtype=pyscipopt.Variable)
        for compI in range(4):
            for day in range(14):
                AAEM[compI, day] = model.addVar(name = f"abs_err_{attributeList[i]}_{compI}_{day}")
                # enforce absolute value via constraints
                model.addCons(    AEM[compI, day] <= AAEM[compI, day])
                model.addCons(-1* AEM[compI, day] <= AAEM[compI, day])

        addendum = np.ones((1,4)) @ AAEM @ weightsList[i]
        AAEsum += addendum[0]

    softPenaltySum = 0

    #  ATTRIBUTE LIMITS
    for limitTuple in attributeLimits:
        print(limitTuple)
        attrId = limitTuple[0]
        min = limitTuple[1]
        max = limitTuple[2]
        enableVector = limitTuple[3]

        softWeight = None       
        if len(limitTuple) > 4:
            softWeight = limitTuple[4]

        ASM = ASM_list[attrId]

        for day in range(len(enableVector)):
            if not enableVector[day]:
                continue
            for compId in range(4):
                compSum = ASM[compId, day]
                if softWeight is None:
                    #add hard constraints
                    model.addCons(compSum >= min)
                    model.addCons(compSum <= max)
                else:
                    #add soft constraints
                    s1 = model.addVar(name = f"Slack", vtype = 'C')
                    s2 = model.addVar(name = f"Slack", vtype = 'C')

                    model.addCons(compSum + s1 >= min)
                    model.addCons(compSum - s2 <= max)

                    softPenaltySum += (s1 + s2) * softWeight



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
                addendum = SCM[i,j] * penalty
                CCPsum += addendum


    #keep together / keep apart constraints 
    for coupling in personalCouplingList:

        p1 : Person = coupling[0]
        p2 : Person = coupling[1]
        desiredProduct = coupling[2]

        softWeight = None
        if len(coupling) > 3:
            softWeight = coupling[3]

        #get variable representing those people sharing a company
        product = SCM[personDict[p1.name], personDict[p2.name]]

        if softWeight is None:
            model.addCons(product == desiredProduct)
        else:
            #add soft constraint
            s = model.addVar(name = f"Slack", vtype = 'B')
            if desiredProduct == 1:
                model.addCons(product + s == desiredProduct)
            elif desiredProduct == 0:
                model.addCons(product - s == desiredProduct)

            softPenaltySum += s * softWeight


    # -------------------------------------------

    cost = AAEsum + CCPsum + softPenaltySum

    objVar = model.addVar(name = "objectiveVariable")
    model.addCons(objVar >= cost)

    model.setObjective(objVar)

    model.setParam('limits/time', maxtime)

    model.optimize()

    status = model.getStatus()
    if status in ["userinterrupt", "timelimit"]:
        pass
    elif status != "optimal":
        print(f"Could not find assignment. {status}")
        return None

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


    return result


        

if __name__ == "__main__":
    optimize()