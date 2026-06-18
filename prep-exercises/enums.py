from dataclasses import dataclass
from enum import Enum
from typing import List
import sys


class OperatingSystem(Enum):
    MACOS = "macOS"
    ARCH = "Arch Linux"
    UBUNTU = "Ubuntu"


@dataclass(frozen=True)
class Person:
    name: str
    age: int
    preferred_os: OperatingSystem


@dataclass(frozen=True)
class Laptop:
    id: int
    manufacturer: str
    model: str
    screen_size_in_inches: float
    operating_system: OperatingSystem


def parse_age(value: str) -> int:
    try:
        age = int(value)
        if age <= 0:
            raise ValueError
        return age
    except ValueError:
        print(f"Error: invalid age '{value}'", file=sys.stderr)
        sys.exit(1)


def parse_os(value: str) -> OperatingSystem:
    normalized = value.strip().lower()

    for os in OperatingSystem:
        if normalized == os.value.lower():
            return os

    print(f"Error: invalid operating system '{value}'", file=sys.stderr)
    sys.exit(1)


def count_laptops_by_os(laptops: List[Laptop]) -> dict:
    counts = {os: 0 for os in OperatingSystem}
    for laptop in laptops:
        counts[laptop.operating_system] += 1
    return counts


def find_laptops(laptops: List[Laptop], os: OperatingSystem) -> List[Laptop]:
    return [l for l in laptops if l.operating_system == os]

def main():
    laptops = [
        Laptop(1, "Dell", "XPS 13", 13, OperatingSystem.ARCH),
        Laptop(2, "Dell", "XPS 15", 15, OperatingSystem.UBUNTU),
        Laptop(3, "Lenovo", "ThinkPad", 14, OperatingSystem.UBUNTU),
        Laptop(4, "Apple", "MacBook Air", 13, OperatingSystem.MACOS),
        Laptop(5, "HP", "Pavilion", 15, OperatingSystem.UBUNTU),
    ]

    name = input("Enter your name: ").strip()
    if not name:
        print("Error: name cannot be empty", file=sys.stderr)
        sys.exit(1)

    age = parse_age(input("Enter your age: "))
    preferred_os = parse_os(input("Enter preferred OS (macOS, Arch Linux, Ubuntu): "))

    person = Person(name=name, age=age, preferred_os=preferred_os)

    counts = count_laptops_by_os(laptops)
    matching = find_laptops(laptops, person.preferred_os)

    print(f"\n{name}, we have {len(matching)} laptop(s) for {person.preferred_os.value}.")

    best_os = max(counts, key=counts.get)

    if best_os != person.preferred_os:
        print(
            f"If you're flexible, you're more likely to get a laptop with "
            f"{best_os.value} ({counts[best_os]} available)."
        )


if __name__ == "__main__":
    main()
