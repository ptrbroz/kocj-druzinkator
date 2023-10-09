

class Person:
    """
    Ocejak vulgaris taboritae. Holds a name, assigned company (if any) and a list of attributes (eg.: jokerit, matfyz, ...)
    """

    def __init__(self, name, *atributes):
        """
        Params:
        ---------
        name : string
            required. Use same format as Vojta's excel (e.g. "Vojta Úlehla")
        *atributes: either string or (string, value)
            optional. Initialises supplied attribute names to 1.
            Alternatively, if an attribute is supplied in the form of a tuple, it is initialized to the value of the second element.

        Example:
            j = Person("Jan Tleskač", "jokerit", ("matfyz", 0.2), )
            
        """
        self.name = name
        self.company = None
        self.dict = {}

        for a in atributes:
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
        self.dict[attribute] = value
    
    def __str__(self) -> str:
        s = "[-] "
        if self.company is not None:
            s = f"[{self.company}] "
        s += self.name
        s += " "
        s += self.dict.__str__()
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












