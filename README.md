# kocj-druzinkator

## Installation

Get a conda environment (using miniforge conda.  Regular conda does not work.) set up, see requirements.txt file (not tested but I assume it will work, as I generated it with "conda list -e")

Download a copy of Vojta's Excellent Excel file (tabory_ucastnici.xlsx) to root of this repo.

## Setting up a problem

For now, see exampleSetup.py and comments for functions of Problem and Person objects.  

I'll write a manual eventually (for my own sake too).

## Solving a problem

Run exampleSetup.py or similar from commandline.  See "python exampleSetup.py --help" for options.

## Reading the visualization

### Daily attribute balance comparision

Dashed lines show sum of attributes represented in company on that day.  Full line shows the "ideal" ammount, i.e. total sum across people present on that day divided by 4.

The "human" attribute is automatically set to 1 for each person, therefore the "human" plot tracks daily manpower of companies.

### Co-Company Penalty Matrix

Cells show value of CCPM derived from Vojta's excel & weights supplied in setup.  

Coloured cells correspond to people who share a company.  A green cell signifies that the two people have zero co-company penalty, red means nonzero.

Format of data in cell is "co-company penalty" x "number of days spent in same company in this solution".  For couples who don't share a company in this solution, only the penalty is printed.
