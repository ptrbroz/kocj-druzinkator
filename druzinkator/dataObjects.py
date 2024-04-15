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
        self.presence = presence.flatten()
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

    """
    Assignment of people into companies.  The solution of the optimization problem.
    """

    companies : List[List[Person]]
    personList : List[Person]
    SCM : np.matrix

    def __init__(self, personList : List[Person], membershipMatrix : np.matrix, sharedCompanyMatrix: np.matrix) -> None:
        """
        Params:
        ---------
        personList : list of all persons
        membershipMatrix : 4 by len(personList) numpy matrix.  Each column must have exactly one element equal to 1 and rest zeroes.
                Describes assignment of persons into companies.
        sharedCompanyMatrix : len(personList) by len(personList) matrix.  Element at i,j is 1 if ith and jth person share company, 0 otherwise. Optional
        """
        self.personList = personList
        self.membershipMatrix = membershipMatrix
        self.SCM = sharedCompanyMatrix

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
                    #print(f"MM@[{i},{j}] = {membershipMatrix[i,j]}, {person.name} -> C{i}")

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


class Problem:
    """
    Object for high-level description of the optim. problem, weighs etc.
    """

    personList : List[Person] = []
    personDict = {}
    attributeList : List[str] = []
    attributeDict = {}

    AAEweighs : List[np.array] = []

    CCPM : np.matrix = None

    attributeLimitsList : List[tuple] = []
    keepTogetherList : List[tuple] = []
    keepApartList : List[tuple] = []
    

    def __init__(self, personList) -> None:
        self.personList = personList
        for i, person in enumerate(personList):
            self.personDict[person.name] = i

    def __registerAttribute(self, attr : str):
        gotten = self.attributeDict.get(attr, None)
        if gotten is None:
            self.attributeDict[attr] = len(self.attributeList)
            self.attributeList.append(attr)
            self.AAEweighs.append(None)
        print(f"regAtt: {attr}, gotten = {gotten}.  {self.attributeList}")
        
    def setCCPM(self, CCPM : np.matrix):
        """
        Sets the Co-company penalty matrix to be used.
        Obtained by calling vojtaToHistoryMatrix() and historyToCoCompanyPenalty()
        """
        self.CCPM = CCPM

    def setAttributeErrorWeigh(self, attribute : str, dailyWeighVector : np.array):
        """
        Set weighs for penalizing Absolute Attribute Error of specified attribute.
        You probably want to set this for attribute "human" at the very least.
        Example:
        setAttributeErrorWeigh("jokerit", dailyWeighVector = np.array([0]*7+[5]*3+[1]*4) )
            This will penalize AAE of jokerit attribute on 8th, 9th and 10th day with weigh 5 and with weigh 1 on days 11 to 14. 
            Jokerit errors on the first 7 days will not be penalized at all.
        """
        self.__registerAttribute(attribute)
        self.AAEweighs[self.attributeDict[attribute]] = dailyWeighVector.flatten()

    def addAttributeLimits(self, attribute : str, min = -np.inf, max = np.inf, soft = False, softPenalty = 100, enableVector = np.ones((1,14))):
        """
        Adds (inclusive) limits for sum of defined attribute to problem constraints.
        If soft is True, this translates into a soft constraint with penalty equal to softPenalty.
        The constraint only applies on days whose value is 1 in enableVector.
        
        Example use:
        problem.setAttributeLimits("rarasek", min=1)
            Require that the sum of present attribute "rarasek" is always at least 1 in each company on each day.
        """
        self.__registerAttribute(attribute)
        if soft:
            limitTuple = (self.attributeDict[attribute], min, max, enableVector.flatten(), softPenalty)
            self.attributeLimitsList.append(limitTuple)
        else:
            limitTuple = (self.attributeDict[attribute], min, max, enableVector.flatten())
            self.attributeLimitsList.append(limitTuple)


    def keepTogether(self, person1 : Person, person2 : Person, soft = False, softPenalty = 100):
        """
        Sets a constraint requiring that specified persons share a company.
        """
        if soft:
            self.keepTogetherSoftList.append( (person1, person2, softPenalty) )
        else:
            self.keepTogetherHardList.append( (person1, person2) )

    def keepApart(self, person1 : Person, person2 : Person, soft = False, softPenalty = 100):
        """
        Sets a constraint requiring that specified persons be placed in different companies.
        """
        if soft:
            self.keepApartSoftList.append( (person1, person2, softPenalty) )
        else:
            self.keepApartHardList.append( (person1, person2) )



        
if __name__ == "__main__":
    a = Person("Ales Jahoda", "fuj", "jokerit", ("kreten",0.1))
    print(a)
    a.set("kamenik")
    a.set("arachnofob", 5)
    a.set("kreten", 0)
    print(f"Value of kamenik: {a.get('kamenik')}")
    print(f"Value of tankista: {a.get('tankista')}")
    print(a)











