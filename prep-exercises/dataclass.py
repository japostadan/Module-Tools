from dataclasses import dataclass
from datetime import date

@dataclass(frozen=True)
class Person:
    name: str
    date_of_birth: date
    preferred_operating_system: str

    def age(self) -> int:
        today = date.today()
        years = today.year - self.date_of_birth.year

        if (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day):
            years -= 1

        return years

    def is_adult(self) -> bool:
        return self.age() >= 18

imran = Person("Imran", 22, "Ubuntu")  # We can call this constructor - @dataclass generated it for us.
print(imran)  # Prints Person(name='Imran', age=22, preferred_operating_system='Ubuntu')

imran2 = Person("Imran", 22, "Ubuntu")
print(imran == imran2)  # Prints True
