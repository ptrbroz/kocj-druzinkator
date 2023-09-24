from openpyxl import load_workbook


def vojtaToHistoryMatrix(filename):
    """
    Convert Vojta's excel table into a history matrix.

    Params:
    ---
    filename : string
        Filename of Vojta's excel table, downloaded to this folder.

    Returns:
    ---
        todo

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

    for d in compDicts:
        print(d)



if __name__ == "__main__":
    vojtaToHistoryMatrix("tabory_ucastnici.xlsx")









