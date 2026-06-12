# Implement Laptop Allocation with Preference Optimization

## Summary

This PR implements a solution to the laptop allocation problem where people are assigned laptops based on their operating system preferences. The algorithm finds the optimal assignment that minimizes total "sadness" across all allocations.

## What Changed

### Data Structures
- **`OperatingSystem` enum**: Represents the three supported OS options (macOS, Arch Linux, Ubuntu)
- **`Person` dataclass**: Stores a person's name, age, and ranked operating system preferences
- **`Laptop` dataclass**: Represents a laptop with its ID, manufacturer, model, screen size, and OS

### Core Algorithm
- **`sadness()` function**: Calculates dissatisfaction for a person-laptop pair by returning the preference index (0 = most preferred). If the laptop's OS is not in the person's preferences, returns 100 (maximum sadness)
- **`allocate_laptops()` function**: Finds the optimal laptop assignment by:
  - Generating all possible permutations of laptop assignments
  - Selecting the permutation with the minimum total sadness score
  - Returns a dictionary mapping each person to their optimal laptop

### Example Execution
The main block demonstrates the algorithm with:
- 2 people (Imran with Ubuntu/Arch preference, Eliza with Arch/macOS preference)
- 3 laptops (Dell XPS with Arch, Dell XPS with Ubuntu, Apple MacBook with macOS)
- Output showing the optimal person-to-laptop assignments

## How It Works

The allocation process uses brute-force optimization: it evaluates all possible ways to assign laptops to people and selects the assignment that minimizes total unhappiness. The "sadness" metric is the index in a person's preference list—lower indices (preferred OSes) result in lower sadness scores.

## Testing

The implementation can be run directly to see the optimal allocation:
```bash
python laptop-allocation.py
```

Expected output shows each person paired with the laptop that best matches their preferences while ensuring all people get exactly one laptop.

## Notes

- Uses immutable `frozen=True` dataclasses for data integrity
- The algorithm's time complexity is O(n! × n) where n is the number of people/laptops, suitable for small groups
- Easily extensible to include additional laptop properties or preference factors
