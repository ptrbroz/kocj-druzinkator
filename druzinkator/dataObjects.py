import numpy as np
from typing import List

class Person:
    """
    Ocejak vulgaris taboritae. 
    """

    def __init__(self, name, *atributes, presence = None, birthYear : int = None, addTo : List = None):
        """
        Params:
        ---------
        name : string
            required. Use same format as Vojta's excel (e.g. "Petr Brož")
        *atributes: either string or (string, value)
            optional. Initialises supplied attribute names to 1.
            Alternatively, if an attribute is supplied in the form of a tuple, it is initialized to the value of the second element.
        presence : numpy array of 1s and 0s, length = 14
            optional (defaults to ones). 1 -> person is present on that day, 0-> not present
        addTo : list of Person.  Optional.  If specified, constructor appends newly created object to this list.
        birthYear : year the person was born, defaults to unknown (None)
        Example:
            j = Person("Jan Tleskač", "jokerit", ("matfyz", 0.2))
            
        """
        self.name = name
        self.birthYear = birthYear
        if presence is None:
            presence = np.ones(14)
        elif len(presence) != 14:
            raise Exception(f"Wrong length of supplied presence vector. Wanted 14, got {len(presence)}")
        if isinstance(presence, List):
            presence = np.array(presence)
        self.presence = presence.flatten()
        self.presence = self.presence.astype(float)
        self.dict = {}

        self.dict["human"] = 1.0

        for a in atributes:
            if(a == "human"):
                raise Exception(f"Setting attribute 'human' is forbidden.  (It is automatically initialised to 1)")
            if isinstance(a, tuple):
                self.dict[a[0]] = a[1]
            else:
                self.dict[a] = 1.0

        if addTo is not None:
            addTo.append(self)


    def get(self, attribute):
        """
        Gets value of specified attribute (or 0 if that attribute is not present)
        """
        return self.dict.get(attribute, 0.0)

    def set(self, attribute, value=1.0):
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

    personList : List[Person] 
    companyFixList : List[int]
    personDict : dict
    attributeList : List[str] 
    attributeDict : dict

    AAEweighs : List[np.array] 

    CCPM : np.matrix 

    attributeLimitsList : List[tuple] 

    personalCouplingList : List[tuple] 
    

    def __init__(self, personList) -> None:
        self.personList = personList
        self.companyFixList = [None] * len(personList)
        self.personDict = {}
        self.attributeList = []
        self.attributeDict = {}
        self.AAEweighs = []
        self.CCPM = None
        self.attributeLimitsList = []
        self.personalCouplingList = []

        for i, person in enumerate(personList):
            self.personDict[person.name] = i

    def __registerAttribute(self, attr : str):
        gotten = self.attributeDict.get(attr, None)
        if gotten is None:
            self.attributeDict[attr] = len(self.attributeList)
            self.attributeList.append(attr)
            self.AAEweighs.append(None)
        #print(f"regAtt: {attr}, gotten = {gotten}.  {self.attributeList}")

    def getPersonByName(self, name : str):
        index = self.personDict.get(name, None)
        if index is None:
            return None
        return self.personList[index]

    def fixCompanyForPerson(self, person : Person, company : int):
        """
        Adds a hard constraint that @person be placed in company number @company, if @person is part of this problem.
        """
        if company not in [0,1,2,3]:
            raise Exception(f"Cannot fix {person.name}'s company to {company}.  Only company values {{0,1,2,3}} are allowed.")
        index = self.personDict.get(person.name, None)
        if index is not None:
            self.companyFixList[index] = company

    def fixPeopleFromOldAssignment(self, peopleList : List[Person], oldAss : Assignment):
        """
        Add a hard constraint that every person in @peopleList, if also present in this problem definition, be placed 
        in the same company as they were placed into in @oldAss.
        """
        for p in peopleList:
            index = self.personDict.get(p.name, None)
            if index is not None:
                self.companyFixList[index] = oldAss.getCompanyByName(p.name)

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
        product = 1
        if soft:
            self.personalCouplingList.append( (person1, person2, product, softPenalty) )
        else:
            self.personalCouplingList.append( (person1, person2, product) )

    def keepApart(self, person1 : Person, person2 : Person, soft = False, softPenalty = 100):
        """
        Sets a constraint requiring that specified persons be placed in different companies.
        """
        product = 0
        if soft:
            self.personalCouplingList.append( (person1, person2, product, softPenalty) )
        else:
            self.personalCouplingList.append( (person1, person2, product) )

    def report(self):
        s = "Problem definition report:\n"
        s += "------Attributes--------\n"
        for attr in self.attributeList:
            id = self.attributeDict[attr]
            aaew = self.AAEweighs[id]
            s += f"{attr}: aaew = {aaew}, limits = ["
            commaFlag = 0
            for tup in self.attributeLimitsList:
                if tup[0] == id:
                    if commaFlag:
                        s+= ", "
                    commaFlag = 1
                    s += f"{tup}"
            s += "]\n"
        s += "------Free People-------\n"
        freeList = []
        fixedListOfLists = []
        for i in range(4):
            fixedListOfLists.append([])
        for i, person in enumerate(self.personList):
            if self.companyFixList[i] is None:
                freeList.append(person.name)
            else:
                fixedListOfLists[self.companyFixList[i]].append(person.name)

        s += "["
        commaFlag = 0
        for p in freeList:
            if commaFlag:
                s+=", "
            commaFlag = 1
            s+=p
        s += "]\n"
        s += "------Fixed People-------\n"
        for i in range(4):
            s+= f"C{i}: {fixedListOfLists[i]}\n"

        kAList = []
        kTList = []
        for coupling in self.personalCouplingList:
            cs = f"{coupling[0].name} - {coupling[1].name}"
            if len(coupling) > 3:
                cs += f" (soft : {coupling[3]})"
            else:
                cs += " (hard)"
            if coupling[2] == 1:
                kTList.append(cs)
            else:
                kAList.append(cs)

        s += f"------Keep apart-----\n"
        for cs in kAList:
            s += f"{cs}\n"
        s += f"------Keep together-----\n"
        for cs in kTList:
            s += f"{cs}\n"
        s += "---------------------------"
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











