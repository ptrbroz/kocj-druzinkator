import re
import unicodedata

from dataObjects import *

def unicodeToVariableName(unicodeString):
    # Normalize the Unicode string to NFKD form
    normalizedString = unicodedata.normalize('NFKD', unicodeString)
    
    # Encode to ASCII bytes and decode back to a string, ignoring non-ASCII characters
    asciiString = normalizedString.encode('ASCII', 'ignore').decode('ASCII')
    
    # Replace any character that is not a letter, digit, or underscore with an underscore
    validVariableName = re.sub(r'\W|^(?=\d)', '_', asciiString)
    
    return validVariableName

def massAssign(persons, attribute):
    for person in persons:
        person.set(attribute)

def spreadLoveAndHatred(pairs, persons, problem):
    for pair in pairs:
        romeo, juliet = pair
        problem.keepApart(romeo, juliet)
 

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
    spreadLoveAndHatred([(pb, jm), (kb, kbr)], personList, problem)

    print("\nMass assignment")
    for person in problem.personList:
        print(person)

    print("\nCouplings")
    for coupling in problem.personalCouplingList:
        print(coupling[0], coupling[1])
