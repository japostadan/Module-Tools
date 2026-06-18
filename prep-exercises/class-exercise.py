# Describe the purpose of a class.
#A class is used to define a new kind of object in your program. Its purpose is to:
    # Groups related data together (attributes like name, age)
    # Defines behavior for that data (methods like is_adult())
    # Provides structure and consistency so all objects of that type follow the same rules
#Relationship between a class and its instances
    #A class is the template or blueprint
    #An instance is a specific object created from that class
# Use classes in mypy.

#imran = {
#  "name": "Imran",
#  "age": 22,
#  "preferred_operating_system": "Ubuntu",
#}
#
#eliza = {
#  "name": "Eliza",
#  "age": 34,
#  "preferred_operating_system": "Arch Linux",
#}
#
#print(imran["name"])
#print(imran["address"])

class Person:
    def __init__(self, name: str, age: int, preferred_operating_system: str):
        self.name = name
        self.age = age
        self.preferred_operating_system = preferred_operating_system

imran = Person("Imran", 22, "Ubuntu")
print(imran.name)
#print(imran.address)

eliza = Person("Eliza", 34, "Arch Linux")
print(eliza.name)
#Print(eliza.address)

#This code is saying: “There’s a category of object called Person. Every instance of Person has a name, an age, and a preferred_operating_system”.
#It then makes two instances of Person, and uses them.
#The method called __init__ is called a constructor - it is what is called when we construct a new instance of the class.
#Exercise
#Save the above code to a file, and run it through mypy.
#Read the error, and make sure you understand what it’s telling you.
#You can use the names of classes in type annotations just like you can use types like str or int:

def is_adult(person: Person) -> bool:
    return person.age >= 18

print(is_adult(imran))

#.venv ❮ python -m mypy class-exercise.py
#Success: no issues found in 1 source file

#Exercise
#Add the is_adult code to the file you saved earlier.
#Run it through mypy - notice that no errors are reported - mypy understands that Person has a property named age so is happy with the function.
#Write a new function in the file that accepts a Person as a parameter and tries to access a property that doesn’t exist. 
def get_address(person: Person) -> str:
    return person.address

#Run it through mypy and check that it does report an error.

#.venv ❮ python -m mypy class-exercise.py
#class-exercise.py:61: error: "Person" has no attribute "address"  [attr-defined]
#Found 1 error in 1 file (checked 1 source file)

#.venv ❮ python -m mypy class-exercise.py
#class-exercise.py:34: error: "Person" has no attribute "address"  [attr-defined]
#class-exercise.py:38: error: "Person" has no attribute "address"  [attr-defined]
#Found 2 errors in 1 file (checked 1 source file)
