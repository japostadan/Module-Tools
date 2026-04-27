from dataclasses import dataclass
from enum import Enum
from typing import List, Dict, Tuple

class OperatingSystem(Enum):
    MACOS = "macOS"
    ARCH = "Arch Linux"
    UBUNTU = "Ubuntu"

@dataclass(frozen=True)
class Person:
    name: str
    age: int
    # Sorted in order of preference, most preferred is first.
    preferred_operating_system: Tuple[OperatingSystem, ...]


@dataclass(frozen=True)
class Laptop:
    id: int
    manufacturer: str
    model: str
    screen_size_in_inches: float
    operating_system: OperatingSystem


def sadness(person: Person, laptop: Laptop) -> int:
    try:
        return person.preferred_operating_system.index(laptop.operating_system)
    except ValueError:
        return 100


def allocate_laptops(people: List[Person], laptops: List[Laptop]) -> Dict[Person, Laptop]:
    best_allocation = None
    best_total_sadness = float("inf")

    def backtrack(i: int, used: set, current: Dict[Person, Laptop], total_sadness: int):
        nonlocal best_allocation, best_total_sadness

        # all people assigned
        if i == len(people):
            if total_sadness < best_total_sadness:
                best_total_sadness = total_sadness
                best_allocation = current.copy()
            return

        person = people[i]

        for j, laptop in enumerate(laptops):
            if j in used:
                continue

            s = sadness(person, laptop)

            used.add(j)
            current[person] = laptop

            backtrack(i + 1, used, current, total_sadness + s)

            used.remove(j)
            del current[person]

    backtrack(0, set(), {}, 0)

    return best_allocation


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
