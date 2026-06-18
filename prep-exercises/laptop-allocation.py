from dataclasses import dataclass
from enum import Enum
from itertools import permutations

class OperatingSystem(Enum):
    MACOS = "macOS"
    ARCH = "Arch Linux"
    UBUNTU = "Ubuntu"

@dataclass(frozen=True)
class Person:
    name: str
    age: int
    # Sorted in order of preference, most preferred is first.
    preferred_operating_system: tuple[OperatingSystem, ...]


@dataclass(frozen=True)
class Laptop:
    id: int
    manufacturer: str
    model: str
    screen_size_in_inches: float
    operating_system: OperatingSystem


def sadness(person: Person, laptop: Laptop) -> int:
    prefs = person.preferred_operating_system
    return prefs.index(laptop.operating_system) if laptop.operating_system in prefs else 100


def allocate_laptops(people: list[Person], laptops: list[Laptop]) -> dict[Person, Laptop]:
    best_assignment = min(
        permutations(laptops, len(people)),
        key=lambda assignment: sum(sadness(p, l) for p, l in zip(people, assignment)),
    )
    return dict(zip(people, best_assignment))


if __name__ == "__main__":
    people = [
        Person("Imran", 22, (OperatingSystem.UBUNTU, OperatingSystem.ARCH)),
        Person("Eliza", 34, (OperatingSystem.ARCH, OperatingSystem.MACOS)),
    ]

    laptops = [
        Laptop(1, "Dell", "XPS", 13, OperatingSystem.ARCH),
        Laptop(2, "Dell", "XPS", 15, OperatingSystem.UBUNTU),
        Laptop(3, "Apple", "MacBook", 13, OperatingSystem.MACOS),
    ]

    result = allocate_laptops(people, laptops)

    for person, laptop in result.items():
        print(f"{person.name} → {laptop.manufacturer} {laptop.model} ({laptop.operating_system.value})")
