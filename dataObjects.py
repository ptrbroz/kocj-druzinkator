import numpy as np
from typing import List

class Person:
    """
    Ocejak vulgaris taboritae. 
    """

    def __init__(self, name, *atributes, presence = None):
        """
        Params:
        ---------
        name : string
            required. Use same format as Vojta's excel (e.g. "Vojta Úlehla")
        *atributes: either string or (string, value)
            optional. Initialises supplied attribute names to 1.
            Alternatively, if an attribute is supplied in the form of a tuple, it is initialized to the value of the second element.
        presence : numpy array of 1s and 0s, length = 14
            optional (defaults to ones). 1 -> person is present on that day, 0-> not present
        Example:
            j = Person("Jan Tleskač", "jokerit", ("matfyz", 0.2))
            
        """
        self.name = name
        if presence is None:
            presence = np.ones(14)
        elif len(presence) != 14:
            raise Exception(f"Wrong length of supplied presence vector. Wanted 14, got {len(presence)}")
        self.presence = presence
        self.dict = {}

        self.dict["human"] = 1

        for a in atributes:
            if(a == "human"):
                raise Exception(f"Setting attribute 'human' is forbidden.  (Is automatically initialised to 1)")
            if isinstance(a, tuple):
                self.dict[a[0]] = a[1]
            else:
                self.dict[a] = 1


    def get(self, attribute):
        """
        Gets value of specified attribute (or 0 if that attribute is not present)
        """
        return self.dict.get(attribute, 0)

    def set(self, attribute, value=1):
        """
        Sets specified attribute to specified value (or to 1, if value is not supplied)
        """
        if(attribute == "human"):
            raise Exception(f"Setting attribute 'human' is forbidden.  (Is automatically initialised to 1)")
        self.dict[attribute] = value
    
    def __str__(self) -> str:
        s = ""
        s += self.name
        s += " "
        s += self.dict.__str__()
        return s
        


class Assignment:

    companies : List[List[Person]]
    personList : List[Person]

    def __init__(self, personList : List[Person], membershipMatrix : np.matrix) -> None:
        """
        Params:
        ---------
        personList : list of all persons
        membershipMatrix : 4 by len(personList) numpy matrix.  Each column must have exactly one element equal to 1 and rest zeroes.
                Describes assignment of persons into companies.
        """
        self.personList = personList
        self.membershipMatrix = membershipMatrix

        #prepare lists of companies and dictionary for membership lookup

        self.dict = {}

        self.companies = []
        for i in range(4):
            companyList = []
            self.companies.append(companyList)
            for j, person in enumerate(personList):
                if(membershipMatrix[i,j]):
                    companyList.append(person)
                self.dict[person.name] = i

    def getCompanyByName(self, personName : str) -> int:
        """
        Returns company id of specified person (0,1,2,3) or None if that person is not included in solution
        """
        return self.dict.get(personName, None)

    def __str__(self) -> str:
        s = ""
        s += f"===Assignment for total of {len(self.personList)} persons===\n\r"
        for i in range(4):
            s += f"Company {i} : {[person.name for person in self.companies[i]]}\n\r"

        return s




        
if __name__ == "__main__":
    a = Person("Ales Jahoda", "fuj", "jokerit", ("kreten",0.1))
    print(a)
    a.set("kamenik")
    a.set("arachnofob", 5)
    a.set("kreten", 0)
    print(f"Value of kamenik: {a.get('kamenik')}")
    print(f"Value of tankista: {a.get('tankista')}")
    print(a)











