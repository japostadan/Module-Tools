from dataclasses import dataclass
from typing import List

@dataclass(frozen=True)
class Person:
    name: str
    children: List["Person"]

fatma = Person(name="Fatma", children=[])
aisha = Person(name="Aisha", children=[])

imran = Person(name="Imran", children=[fatma, aisha])

def print_family_tree(person: Person) -> None:
    print(person.name)
    for child in person.children:
        print(f"- {child.name} ({child.age})")

print_family_tree(imran)

#Run this code through mypy.
#
#Now that we’ve told mypy Person.children is a list of type Person (line 7), it can identify that the child variable on line 16 is of type Person.
#Because of this, it can tell us that child.age on line 17 doesn’t exist.
#📝Note
#
#Most generics don’t need the types to be quoted. Normally you’d just write List[Person].
#But inside a type definition itself (i.e. inside the Person class), the Person type doesn’t exist yet, so we need to quote it.
#
#It’s kind of annoying, but don’t worry about it too much.
##✍️exercise
#Fix the above code so that it works. You must not change the print on line 17 - we do want to print the children’s ages. 
#(Feel free to invent the ages of Imran’s children.)
