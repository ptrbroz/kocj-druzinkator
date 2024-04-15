import click
import numpy as np

from druzinkator.dataObjects import *
from druzinkator.matrixUtils import vojtaToHistoryMatrix, historyToCoCoPenaltyMatrix
from druzinkator.optimize import optimize
from druzinkator.visualize import visualizeAssignment

@click.command()
@click.option('-o', '--output', default = None, help = "If specified, saves problem and assignment to pickle at defined location")
@click.option('-v', '--vojtafile', default = "tabory_ucastnici.xlsx", help = "Vojta's excel file")
def defineAndSolveProblem(output, vojtafile):

    #define people
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
    h11 = Person("Rarach1", "rarasek")
    h12 = Person("Rarach2", "rarasek")
    h13 = Person("Rarach3", "rarasek")
    h14 = Person("Rarach4", "rarasek")
    personList = [h1, h2, h3, h4, h5, h6, h7, h8, h9, h10, h11, h12, h13, h14]

    #-------------------------------------------------------------------------------------

    problem = Problem(personList)

    defaultVector = np.array([0]*1 + [1]*13)
    
    problem.setAttributeErrorWeigh("human", 2*defaultVector)
    problem.setAttributeErrorWeigh("jokerit", defaultVector)
    problem.setAttributeErrorWeigh("matfyz", defaultVector)

    historyNameList, historyMatrix = vojtaToHistoryMatrix(vojtafile)
    penaltyVector = 0.1*np.array([15, 7, 3])
    CCPM =  historyToCoCoPenaltyMatrix(historyMatrix, historyNameList, personList, penaltyVector)
    problem.setCCPM(CCPM)


    problem.addAttributeLimits("rarasek", min=1)
    problem.addAttributeLimits("matfyz", max=1, soft = 1, softPenalty=0.000001)


    #-------------------------------------------------------------------------------------

    result = optimize(problem)
    if result is None:
        return

    visualizeAssignment(result, problem)













if __name__ == '__main__':
    defineAndSolveProblem()