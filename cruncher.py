import click

from openpyxl import load_workbook
from druzinkator.utils import unicodeToVariableName

def dropRowsAfterFirstNone(matrix):
    resultMatrix = []
    for row in matrix:
        if row[0] is None:
            break
        resultMatrix.append(row)
    return resultMatrix


@click.command()
@click.option('-i', '--inputFile', default = "ucast.xlsx", help = "If specified, loads presence file from the specified path.")
@click.option('-o', '--outputFile', default = "exampleGenerated.py", help = "If specified, saves generated file to given location.")
def crunchPergler(inputfile, outputfile):
    print("Growing long hair")
    excel = load_workbook(filename=f"./{inputfile}")
    sheet = excel["Data"]

    cols = [[cell.value for cell in column] for column in sheet.columns]
    rows = [[cell.value for cell in row   ] for row    in sheet.rows   ]
    filteredRows = dropRowsAfterFirstNone(rows[1:])

    print("Attending Moták")
    with open(outputfile, 'w', encoding="utf-8") as file:

        maxNameLen = max([len(row[0]) for row in filteredRows]) 
        maxNameLen += 2 #add some slack in case longest name needs to be edited to a longer, Vojta-compatible version

        for row in filteredRows:

            lineString = f"{unicodeToVariableName(row[0])} = Person(\"{row[0]}\","
            
            #add padding to align presenceVectors
            diff = maxNameLen - len(row[0])
            lineString += 2*diff*" "

            lineString += " presence = ["

            presenceVector = [1 if element == 'ano' else 0 for element in row[2:16]]
            kozlikPoints = [2, 7, 9]   # indices preceded by Kozlík-style weekend separators
            for i in range(len(presenceVector)):
                if i:
                    if i in kozlikPoints:
                        lineString += ",   "
                    else:
                        lineString += ", "

                lineString += f"{presenceVector[i]}"

            lineString += "],   addTo=personList)\n"

            file.write(lineString)

    print("Moving south")

if __name__ == '__main__':
    crunchPergler()
