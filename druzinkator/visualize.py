
import matplotlib.pyplot as plt
import numpy as np
from typing import List

from .matrixUtils import *
from .dataObjects import Person, Assignment

def visualizeAssignment(assignment : Assignment, problem : Problem, attributeList = None):
    """
    Visualizes supplied assignment and problem.
    All attributes specified in problem.attributeList will be visualized, unless attributeList argument is given.
    """

    if attributeList is None:
        attributeList = problem.attributeList
    CCPM = problem.CCPM

    print(f"Taking into account attributes {attributeList}")
    print("Visualizing following assignment:")
    print(assignment)

    #prep DIM
    DSM, _ = calculateDailyMatrices(assignment.personList, attributeList)
    DIM = DSM / 4

    tdays = np.linspace(1, 14, 14)

    hratios = [(int(x == "human")*0.5 + 1) for x in attributeList]  #make manpower subplot a little bigger
    attrFig, attrAxs = plt.subplots(len(attributeList), gridspec_kw={'height_ratios':hratios})
    attrFig.suptitle("Daily attribute balance comparision")

    companyDSMs = []
    for company in assignment.companies:
        DSM_thiscomp, _ = calculateDailyMatrices(company, attributeList)
        companyDSMs.append(DSM_thiscomp)

    lastI = len(attributeList) - 1
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

        if i != lastI:
            empty_string_labels = ['']*len(tdays)
            ax.set_xticklabels(empty_string_labels)
        else:
            week = ['po','ut','st','ct','pa','so','ne']
            labels = ['so', 'ne']
            labels.extend(week)
            labels.extend(week)
            labels = labels[:-2]
            ax.set_xticklabels(labels)


        ax.set_ylabel(attribute)
        ax.grid()

    attrFig.show()
    #plotCCPM(assignment, problem) #dont plot the big ccpm,
    for i in range(4):
        title = f"Co-Company Penalty Matrix for Company #{i}"
        plotCCPM(assignment, problem, assignment.companies[i], title)

    for i in range(4):
        plotCompanyMembersDays(assignment.companies[i], title= f"Presence for company #{i}" )

    input()


def plotCompanyMembersDays(persons: List[Person], title = ""):

    fig, ax = plt.subplots()

    #plt.figure(figsize=(10, len(persons) * 0.5))  # Adjusting the figure size for better readability

    persons = sorted(persons, key = lambda p : sum(p.presence))

    for idx, person in enumerate(persons):
        presence = person.presence
        for day, present in enumerate(presence):
            color = 'green' if present else 'red'
            ax.scatter(day+1, idx, color=color, s=100)  # s controls the size of the markers

    ax.set_title(title)
    ax.set_yticks(range(len(persons)), [person.name for person in persons])

    week = ['po','ut','st','ct','pa','so','ne']
    labels = ['so', 'ne']
    labels.extend(week)
    labels.extend(week)
    labels = labels[:-2]
    tdays = np.linspace(1,14,14)

    ax.set_xticks(tdays)
    ax.set_xticklabels(labels)

    ax.grid(True)
    fig.show()


def plotCCPM(assignment : Assignment, problem : Problem, personList = None, title = None):
    #cocompany penalty matrix plot

    CCPMfig, ax = plt.subplots()

    if title is None:
        CCPMfig.suptitle("Co-Company Penalty Matrix (Everyone)")
    else:
        CCPMfig.suptitle(title)

    if personList is None:
        personList = assignment.personList
    CCPM = problem.CCPM

    maxVal = CCPM.max()

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

    for j in range(pcount):
        for i in range(pcount):
            if i==j:
                ax.text(j+0.5, i+0.5, "-", va='center', ha='center', color='black', clip_on = True)
                ax.fill_between([j, j+1], i, i+1, color='lightgray')
                continue

            p1 = personList[i]
            p2 = personList[j]
            
            globalI = problem.personDict[p1.name]
            globalJ = problem.personDict[p2.name]
            ccp = CCPM[globalI,globalJ]
            textVal = f"{ccp:.1f}"
            
            #print(f"{p1.name} x {p2.name} -> {assignment.getCompanyByName(p1.name)} vs {assignment.getCompanyByName(p2.name)}")

            #sharedCompany = (assignment.getCompanyByName(p1.name) == assignment.getCompanyByName(p2.name))
            sharedCompany = assignment.SCM[globalI,globalJ]

            dontMeet = 0
            
            if sharedCompany:
                intersectionDays = np.sum(p1.presence * p2.presence)
                if intersectionDays == 0:
                    dontMeet = 1
                else:
                    textVal += f"×{int(intersectionDays)}"

            color = 'white'
            if sharedCompany:
                if ccp > 0:
                    #maybe todo: pass twice and change red hue depending on severity?
                    norm = ccp/maxVal
                    gb = 0.5
                    bb = 0.5
                    g = gb*(1-norm)
                    b = bb*(1-norm)
                    color = (1, g, b)
                else:
                    color = (0.8, 1, 0.7)

            ax.text(j+0.5, i+0.5, textVal, va='center', ha='center', fontsize= 7, color='black', clip_on = True)
            ax.fill_between([j, j+1], i, i+1, color=color)

            if dontMeet:
                ax.fill_between([j+0.1, j+0.9], i+0.1, i+0.9, color='white')


    CCPMfig.show()















