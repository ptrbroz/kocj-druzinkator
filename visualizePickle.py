import click
import numpy as np
import dill as pickle

from druzinkator.dataObjects import *
from druzinkator.matrixUtils import *
from druzinkator.optimize import optimize
from druzinkator.visualize import visualizeAssignment


@click.command()
@click.argument('input')
def visualizePickle(input):
    print(f"Visualizing pickle {input}")
    file = open(input, 'rb')
    data = pickle.load(file)
    file.close()

    problem = data[0]
    result = data[1]

    print(result)
    print(problem.attributeList)

    input()

    visualizeAssignment(result, problem)



if __name__ == '__main__':
    visualizePickle()