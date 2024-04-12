from openpyxl import load_workbook
import numpy as np
import logging as log

from typing import List
from dataObjects import *

def vojtaToHistoryMatrix(filename):
    """
    Convert Vojta's excel table into a history matrix and list of names.
    Logs warnings if something seems off about the data.

    Params:
    ---
    filename : string
        Filename of Vojta's excel table, downloaded to this folder.

    Returns:
    ---
    personNameList : list
        List of strings in format "Name Surname"
    historyMatrix : np.array
        Array size [# of people, # of years]. Elements of array are zero if person was 
        not in a recognised company that year (or if their company is unknown).
        If an element is nonzero, person was in company whose index matches the element.
    """
    excel = load_workbook(filename=f"./{filename}")
    sheet = excel["STATISTIKA"]

    cols = [[cell.value for cell in column] for column in sheet.columns]
    rows = [[cell.value for cell in row   ] for row    in sheet.rows   ]

    COMPANY_NAME_BLACKLIST = ["ved a kuch", "návštěva", "dětská", "dítě", "družinka"]   #strings that are not valid company names
    #per Vojta: Druzinka means person was in a company, but it is not known which one.  Therefore removing

    #this might need updating should the structure of Vojta's excel change
    COL_YEAR_FIRST = 7                  
    COL_YEAR_LAST = len(rows[0]) - 3
    COL_SURNAME = 0                     
    COL_NAME = 2                        
    ROW_PERSON_FIRST = 11
    ROW_PERSON_LAST = len(cols[0]) - 1
    YEARS_TOTAL = COL_YEAR_LAST - COL_YEAR_FIRST + 1
    PERSONS_TOTAL = ROW_PERSON_LAST - ROW_PERSON_FIRST + 1
    

    #prepare translation from companies to ints. Intended mapping: valid companies -> {1,2,3,4}, kitchen/org/visits/not present -> 0
    #reason: save some computation time when comparing each pair to see if they shared company (int comparision instead of string comp.)
    compDicts =  [{} for i in range(YEARS_TOTAL)]
    for i, col in enumerate(cols[COL_YEAR_FIRST:COL_YEAR_LAST+1]):
        d = compDicts[i]
        for cell in col[ROW_PERSON_FIRST:]:
            if isinstance(cell, str) and len(cell) > 0:
                if cell not in COMPANY_NAME_BLACKLIST and cell not in d.keys():
                    count = len(d.keys()) + 1
                    d[cell] = count

    historyMatrix = np.zeros((PERSONS_TOTAL, YEARS_TOTAL))

    for year in range(YEARS_TOTAL):
        d = compDicts[year]
        yearCol = cols[COL_YEAR_FIRST + year]
        for person in range(PERSONS_TOTAL):
            result = d.get(yearCol[ROW_PERSON_FIRST + person])
            if result: 
                historyMatrix[person, year] = result

    personNameList = []
    for i in range(PERSONS_TOTAL):
        joinedName = cols[COL_NAME][ROW_PERSON_FIRST+i] + " " + cols[COL_SURNAME][ROW_PERSON_FIRST+i]
        personNameList.append(joinedName)
        #ain't nobody got time for maiden names, sorry

    #check for anomalies and log them
    incompleteYears = []
    for i, d in enumerate(compDicts):
        l = len(d)       
        if l < 4:
            incompleteYears.append(i)
        elif l > 4:
            y = rows[0][COL_YEAR_FIRST+i]
            log.warning(f"Year {y} contains too many ({l}) companies! Dictionary follows: \n {d}")
    log.info(f'''Incomplete data (fewer than 4 companies found) for following years:
              {[rows[0][COL_YEAR_FIRST+i] for i in incompleteYears]}''')

    return personNameList, historyMatrix


def vojtaToCoCoPenaltyMatrix(filename, personList : List[Person], penaltyVector : np.array):
    """
    Converts Vojta's excel file into CoCompany Penalty Matrix (CCPM).

    arguments:
    filename : location of Vojta's excel
    personList : list of people for which to generate CCPM
    penaltyVector : vector of penalty values for sharing a company.  Number of elements corresponds to number of years into the past that
        are taken into account, starting with last year.

    returns:
    CCPM : x by x numpy matrix, where x is len(personList).  Intersection of ith row and jth column holds the penalty that will be applied if
        ith and jth person from personList are assigned to the same company.

    example:

    Consider a penalty vector of [10, 5, 2].  If two persons A, B are assigned to the same company in the present year (2024), following penalties
    may be applied:

    If A,B shared company in year 2023 only : penalty of 10
    If A,B shared company in year 2022 only : penalty of 5
    If A,B shared company in year 2021 only : penalty of 2
    If A,B shared company in year 2020 only : penalty of 0 (out of scope of penalty vector)
    If A,B shared company in years 2023 and 2021 : penalty of 12

    etc.

    """

    vojtaPersonNameList, historyMatrix = vojtaToHistoryMatrix(filename)

    #prepare translation from user supplied personList to vojta indices
    vojtaNameDict = {}
    for i, vName in enumerate(vojtaPersonNameList):
        for person in personList:
            if person.name == vName:
                vojtaNameDict[person.name] = i

    #check which people are not in Vojta's history file
    assumedNewbies = []
    for person in personList:
        value = vojtaNameDict.get(person.name, None)
        if value is None:
            assumedNewbies.append(person.name)

    print(f"Following persons did NOT match anyone in Vojta's database:  {assumedNewbies}")

    CCPM = np.zeros((len(personList), len(personList)))

    #fill out CCPM.
    #this could be twice as fast with diagonal flip but whatever
    for i, rowPerson in enumerate(personList):
        vojtaI = vojtaNameDict.get(rowPerson.name, None)
        if vojtaI is None:
            continue        #rowPerson not in history -> wont have any penalties
        for j, colPerson in enumerate(personList):
            if j == i:
                continue    #don't penalize being in same company as yourself
            vojtaJ = vojtaNameDict.get(colPerson.name, None)
            if vojtaJ is None:
                continue
            
            #if we reached thus far both rowPerson and colPerson exist in vojta records, calculate penalty
            hIndex = -1
            penalty = 0
            for p in penaltyVector:
                if historyMatrix[vojtaI, hIndex] == historyMatrix[vojtaJ, hIndex]:
                    penalty += p
                hIndex -= 1         #let's just assume nobody will look far enough into the past for this to fail

            CCPM[i,j] = penalty

    return CCPM








def calculateDailyMatrices(personList : List[Person], attributeList : List[str]):
    """
    arguments:
    personList : list of all people
    attributeList : list of strings. Specified attributes to be taken into account.
    ---------------
    returns:
    DSM : matrix, len(attributeList) by 14. Daily sum matrix. Rows contain sums of attributes present on that day, one row per attribute.
    DAM_list : List of len(attributeList) matrices. Each matrix within list has dimensions len(personList) by 14.  
        Cell contains value of that person's attribute, if person is present on that day.  If person is not present on that day, cell contains 0.
    """
    vl = []
    for p in personList:
        vl.append([p.presence])
    DPM = np.block(vl)

    DAM_list = []
    for attr in attributeList:
        DAM = DPM.copy()
        DAM_list.append(DAM)
        for i,p in enumerate(personList):
            aval = p.get(attr)
            DAM[i, :] *= aval

    DSM = np.zeros((len(attributeList), 14))
    for i, DAM in enumerate(DAM_list):
        DSM[i, :] = DAM.sum(axis = 0)

    return DSM, DAM_list
    






if __name__ == "__main__":
    log.basicConfig()
    log.getLogger().setLevel(log.DEBUG)

    pb = Person("Petr Brož")
    kb = Person("Kateřina Bímová")
    kbr = Person("Kateřina Brůžková")
    nz = Person("Nováček Zmatený")
    jm = Person("Jan Macháň")
     
    personList = [pb, kb, kbr, nz, jm]

    CCPM = vojtaToCoCoPenaltyMatrix("tabory_ucastnici.xlsx", personList, np.array([10, 5, 2, 1, 0.1]))

    print(CCPM)








