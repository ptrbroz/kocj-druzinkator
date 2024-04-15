import click
import numpy as np

from druzinkator.dataObjects import *
from druzinkator.matrixUtils import *
from druzinkator.optimize import optimize
from druzinkator.visualize import visualizeAssignment

@click.command()
@click.option('-o', '--output', default = None, help = "If specified, saves problem and assignment to pickle at defined location")
@click.option('-v', '--vojtafile', default = "tabory_ucastnici.xlsx", help = "Vojta's excel file")
@click.option('-t', '--maxtime', default = 60, help = "Maximum time to run the solver for (seconds).")
def defineAndSolveProblem(output, vojtafile, maxtime):

    personList = []

    #define people.  Names must exactly match vojta's excel!
    romeo = Person("Romeo", "jokerit", addTo=personList)
    juliet = Person("Juliet", addTo=personList)
    alan = Person("Alan Turing", "jokerit", "matfyz", presence=np.array([1]*7 + [0]*7), addTo=personList)
    ada = Person("Ada Lovelace", "matfyz", addTo=personList)
    donkey = Person("Donkey", "jokerit", addTo=personList)
    dragon = Person("Dragon", addTo=personList)


    #-------------------------------------------------------------------------------------

    problem = Problem(personList)

    # forbid placing following pairs in same company
    problem.keepApart(romeo, juliet)
    problem.keepApart(donkey, dragon)

    #parse vojta's excel
    historyNameList, historyMatrix = vojtaToHistoryMatrix(vojtafile)
    vojtaNameDict = vojtaNameListToDict(personList,historyNameList)

    #hand out novacek and potential rarasek attributes automatically based on vojta's excel
    autoRarasek(personList, historyMatrix, vojtaNameDict)   
    autoNovacek(personList, historyMatrix, vojtaNameDict)

    #default vector for weighing attribute imbalance -- disregarding the first day of camp
    defaultVector = np.array([0]*1 + [1]*13)

    #set penalties for imbalance in attributes, penalizing imbalance in "human" five times as much as the others
    problem.setAttributeErrorWeigh("human", 5*defaultVector)
    problem.setAttributeErrorWeigh("jokerit", defaultVector)
    problem.setAttributeErrorWeigh("matfyz", defaultVector)
    problem.setAttributeErrorWeigh("novacek", defaultVector)

    #penalize people for sharing companies if they've been together in a company previously.
    #Specifically:  If A and B share a company AND they shared a company last year, their penalty will be 0.5 * x, where 
    #x = number of days both A and B are present.  If A and B shared a company the year before last, then penalty is 0.2 * x.  If they shared 
    #a company both in the year before last and in last year, penalty is (0.5 + 0.2) * x.
    penaltyVector = np.array([0.5, 0.2])
    CCPM =  historyToCoCoPenaltyMatrix(historyMatrix, vojtaNameDict, personList, penaltyVector)
    problem.setCCPM(CCPM)

    #require that on each day, each company has at least one person with the "rarasek" attribute present.
    #Note that rarasek attribute is only given (in autoRarasek) to people whose presence is at least 13/14 days.
    problem.addAttributeLimits("rarasek", min=1, soft=True)   
    #normally, this would be a hard constraint.  I'm making it soft since nobody in example has rarasek attribute


    #-------------------------------------------------------------------------------------

    result = optimize(problem, maxtime)
    if result is None:
        return

    visualizeAssignment(result, problem)


    if output:
        print("Saving not yet implemented")










if __name__ == '__main__':#
    defineAndSolveProblem()