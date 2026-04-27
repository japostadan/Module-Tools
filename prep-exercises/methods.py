#In Python, the distinction is simple:
#Function → defined on its own (not inside a class)
#Method → a function defined inside a class and called on an object
from datetime import date

class Person:
    def __init__(self, name: str, date_of_birth: date, preferred_operating_system: str):
        self.name = name
        self.date_of_birth = date_of_birth
        self.preferred_operating_system = preferred_operating_system

    def age(self) -> int:
        today = date.today()
        years = today.year - self.date_of_birth.year

        # Check if birthday has already happened this year
        if (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day):
            years -= 1

        return years

    def is_adult(self) -> bool:
        return self.age() >= 18

imran = Person("Imran", date(2001, 5, 10), "Ubuntu")
print(imran.is_adult())
print(imran.age())
