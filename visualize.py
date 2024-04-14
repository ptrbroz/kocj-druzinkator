
import matplotlib.pyplot as plt
import numpy as np
from dataObjects import Person, Assignment
from typing import List
from matrixUtils import *

def visualizeAssignment(assignment : Assignment, attributeList : List[str], CCPM : np.matrix):
    """
    Reports and plots results of supplied assignment for attributes given in attributeList
    """

    print(f"Taking into account attributes {attributeList}")
    print("Visualizing following assignment:")
    print(assignment)

    #prep DIM
    DSM, _ = calculateDailyMatrices(assignment.personList, attributeList)
    DIM = DSM / 4

    tdays = np.linspace(1, 14, 14)
    print(tdays)

    hratios = [(int(x == "human")*0.5 + 1) for x in attributeList]  #make manpower subplot a little bigger
    attrFig, attrAxs = plt.subplots(len(attributeList), gridspec_kw={'height_ratios':hratios})
    attrFig.suptitle("Daily attribute balance comparision")

    companyDSMs = []
    for company in assignment.companies:
        DSM_thiscomp, _ = calculateDailyMatrices(company, attributeList)
        companyDSMs.append(DSM_thiscomp)

    for i, attribute in enumerate(attributeList):
        ax = attrAxs[i]
        for j in range(4):
            attrData = (companyDSMs[j])[i, :]
            ax.plot(tdays, attrData, '--', linewidth = 2, alpha = 0.8)
            ax.set_xticks(tdays)
        ideal = DIM[i, :]
        ax.plot(tdays, ideal, linewidth = 3, alpha = 0.7)

        if i == 0:
            ax.legend(["C0", "C1", "C2", "C3", "Ideal"], loc = 'upper right')

        ax.set_ylabel(attribute)
        ax.grid()


    #cocompany penalty matrix plot

    CCPMfig, ax = plt.subplots()

    personList = assignment.personList
    pcount = len(personList)

    griddingRange = list(range(pcount+1))
    labelingRange = [x + 0.5 for x in range(pcount)]

    ax.set_aspect('equal')
    ax.set_xticks(griddingRange, [""]*len(griddingRange))
    ax.set_xticks(labelingRange, minor = True)
    ax.set_xticklabels([p.name for p in personList], minor = True, rotation = 90)

    ax.set_yticks(griddingRange, [""]*len(griddingRange))
    ax.set_yticks(labelingRange, minor = True)
    ax.set_yticklabels([p.name for p in personList], minor = True, rotation = 0)

    ax.invert_yaxis()

    ax.grid()

    print(CCPM)

    for j in range(pcount):
        for i in range(pcount):
            if i==j:
                ax.text(j+0.5, i+0.5, "-", va='center', ha='center', color='black', clip_on = True)
                ax.fill_between([j, j+1], i, i+1, color='lightgray')
                continue

            ccp = CCPM[i,j]
            p1 = personList[i]
            p2 = personList[j]
            textVal = f"{ccp:.1f}"
            
            #print(f"{p1.name} x {p2.name} -> {assignment.getCompanyByName(p1.name)} vs {assignment.getCompanyByName(p2.name)}")

            #sharedCompany = (assignment.getCompanyByName(p1.name) == assignment.getCompanyByName(p2.name))
            sharedCompany = assignment.SCM[i,j]
            
            if sharedCompany:
                intersectionDays = np.sum(p1.presence * p2.presence)
                if intersectionDays == 0:
                    sharedCompany = False
                else:
                    textVal += f"×{int(intersectionDays)}"

            color = 'white'
            if sharedCompany:
                if ccp > 0:
                    #maybe todo: pass twice and change red hue dep. on severity?
                    color = (1, 0.5, 0.5)
                else:
                    color = (0.8, 1, 0.7)

            ax.text(j+0.5, i+0.5, textVal, va='center', ha='center', color='black', clip_on = True)
            ax.fill_between([j, j+1], i, i+1, color=color)


    attrFig.show()
    CCPMfig.show()
    input()















