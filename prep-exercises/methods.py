#In Python, the distinction is simple:
#Function → defined on its own (not inside a class)
#Method → a function defined inside a class and called on an object
class Person:
    def __init__(self, name: str, age: int, preferred_operating_system: str):
        self.name = name
        self.age = age
        self.preferred_operating_system = preferred_operating_system

imran = Person("Imran", 22, "Ubuntu")
print(imran.name)

eliza = Person("Eliza", 34, "Arch Linux")
print(eliza.name)

