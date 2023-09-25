from openpyxl import load_workbook
import numpy as np
import logging as log


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



if __name__ == "__main__":
    log.basicConfig()
    log.getLogger().setLevel(log.DEBUG)
    nameList, historyMatrix = vojtaToHistoryMatrix("tabory_ucastnici.xlsx")










