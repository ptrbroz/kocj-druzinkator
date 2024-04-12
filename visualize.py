
import matplotlib.pyplot as plt
import numpy as np
from dataObjects import Person, Assignment
from typing import List
from matrixUtils import *

def visualizeAssignment(assignment : Assignment, attributeList : List[str], CCPM : np.matrix = None):
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
        ax.plot(tdays, ideal, linewidth = 2, alpha = 0.5)

        if i == 0:
            ax.legend(["C0", "C1", "C2", "C3", "Ideal"], loc = 'upper right')

        ax.set_ylabel(attribute)
        ax.grid()




    attrFig.show()
    input()















