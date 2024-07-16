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
        for row in filteredRows:
            #debug output
            #print(f"{unicodeToVariableName(row[0])} = Person(\"{row[0]}\", presence = {[1 if element == 'ano' else 0 for element in row[2:17]]}, addTo=personList)")
            file.write(f"{unicodeToVariableName(row[0])} = Person(\"{row[0]}\", presence = {[1 if element == 'ano' else 0 for element in row[2:16]]}, addTo=personList)\n")

    print("Moving south")

if __name__ == '__main__':
    crunchPergler()
