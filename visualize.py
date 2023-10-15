
import matplotlib.pyplot as plt
import numpy as np
from person import Person
from typing import List




def plotSolutions(personList : List[Person], mappingsList, attributeList = None):
    """
    personList : list of all Persons
    mappingList: list of lists. Each list within is as long as personList and in same order, containing integers 0-3 mapping people to companies.
    attributeList : list of strings. Optional. Decides which attributes to include in plot (if not specified, no attributes are compared)

    Example:
    plotSolutions([Person("Alice"), Person("Bob")], [[0, 0], [0, 1]])
    This compares two solutions -- one where both Alice and Bob are in company 0, another where Alice is in 0 and Bob is in 1.
    """

    print("Presence:")
    print(dailyPresenceSum)
    print("Attrs:")
    for i, a in enumerate(attributeList):
        print(f"{a} : {dailyAttributeLists[i]}")















