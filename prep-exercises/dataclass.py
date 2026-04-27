from dataclasses import dataclass

@dataclass(frozen=True)
class Person:
    name: str
    age: int
    preferred_operating_system: str

imran = Person("Imran", 22, "Ubuntu")  # We can call this constructor - @dataclass generated it for us.
print(imran)  # Prints Person(name='Imran', age=22, preferred_operating_system='Ubuntu')

imran2 = Person("Imran", 22, "Ubuntu")
print(imran == imran2)  # Prints True
