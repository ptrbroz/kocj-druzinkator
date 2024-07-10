import re
import unicodedata

from .dataObjects import *

from typing import List, Tuple

def unicodeToVariableName(unicodeString):
    # Normalize the Unicode string to NFKD form
    normalizedString = unicodedata.normalize('NFKD', unicodeString)
    
    # Encode to ASCII bytes and decode back to a string, ignoring non-ASCII characters
    asciiString = normalizedString.encode('ASCII', 'ignore').decode('ASCII')
    
    # Replace any character that is not a letter, digit, or underscore with an underscore
    validVariableName = re.sub(r'\W|^(?=\d)', '_', asciiString)
    
    return validVariableName

def massAssign(persons : List[Person], attribute : str):
    for person in persons:
        person.set(attribute)

def spreadLoveAndHatred(pairs : List[Tuple[Person, Person]] , problem : Problem):
    """
    Keep apart all tuples of persons in pairs.
    """
    for pair in pairs:
        romeo, juliet = pair
        problem.keepApart(romeo, juliet)

def assignBirthYears(persons : List[Person], vojtaBirthYearDict):
    for person in persons:
        person.birthYear = vojtaBirthYearDict.get(person.name, None)

def assignDiscreteDemographicParameters(people : List[Person], currentYear : int, bins : List[Tuple[int, int]]= [(0,14), (15,23), (24,100)], 
                                       binNames : List[str] = None, assumeAge : int  = None):
    """
    Assigns parameters representing age groups to all @people.  Intended to be used in constraints, probably (?) not really suitable as a penalized
    attribute (like human, jokerit...).
    Each person is assigned parameters corresponding to bins they fit into.  Bins may overlap -- in that case, persons might be 
    assigned multiple parameters.
    @bins are specified as tuples (lowerbound, upperbound).  Bins are boundary-inclusive.
    If @binNames is none, parameter strings will be automatically generated out of bin boundaries.  If you want custom parameter strings, set @binNames
    to a list of strings of equal len to that of bins.
    To determine the age, the Person.birthYear property is accessed and age approximated using supplied @currentYear.  Persons might have unknown birthYear.
    If @assumeAge is None, people with unknown age will not be placed into any bins.  If you supply @assumeAge, persons with unknown age will be treated
    as if they were @assumeAge years old.
    ---------------
    Returns:
    usedBinNames :  list of strings of attributes corresponding to bins
    binCounts : list of integers representing the number of people placed into bins.
    """
 
    if binNames is None:
        binNames = []
        for bin in bins:
            binNames.append(f"Age_{bin[0]}_to_{bin[1]}")
    else:
        if len(binNames) != len(bins):
            raise Exception(f"Len mismatch: got {len(binNames)} bin names to {len(bin)} bins.")

    binCounts = [0]*len(bins)

    for person in people:
        bYear = person.birthYear
        if bYear is None:
            if assumeAge is None:
                continue
            else:
                bYear = assumeAge
        age = currentYear - bYear
        if(age < 0):
            raise Exception(f"Time traveller detected.  ({person.name} born in {person.birthYear}, treated as {bYear})")

        for i, bin in enumerate(bins):
            if age >= bin[0] and age <= bin[1]:
                binCounts[i] += 1
                person.set(binNames[i])

    return binNames, binCounts

if __name__ == "__main__":
    name = "Příšernus Nejmus 7"
    varName = unicodeToVariableName(name)
    print(varName)

    pb = Person("Petr Brož")
    kb = Person("Kateřina Bímová")
    kbr = Person("Kateřina Brůžková")
    nz = Person("Nováček Zmatený")
    jm = Person("Jan Macháň")
     
    personList = [pb, kb, kbr, nz, jm]
    massAssign(personList, "nadčlověk")

    problem = Problem(personList)
    spreadLoveAndHatred([(pb, jm), (kb, kbr)], problem)

    print("\nMass assignment")
    for person in problem.personList:
        print(person)

    print("\nCouplings")
    for coupling in problem.personalCouplingList:
        print(coupling[0], coupling[1])
