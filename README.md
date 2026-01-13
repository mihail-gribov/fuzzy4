# fuzzy4

[![PyPI version](https://badge.fury.io/py/fuzzy4.svg)](https://badge.fury.io/py/fuzzy4)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A Python library for **4-valued fuzzy logic** based on Belnap logic with product t-norm operations.

## Overview

Traditional boolean logic has two values: `True` and `False`. Real-world knowledge often involves **uncertainty** (we don't know) and **contradiction** (conflicting evidence). Belnap's 4-valued logic addresses this by representing propositions as vectors `(T, F)`:

| State | Vector | Meaning |
|-------|--------|---------|
| **TRUE** | (1, 0) | Confirmed, not refuted |
| **FALSE** | (0, 1) | Refuted, not confirmed |
| **UNKNOWN** | (0, 0) | Neither confirmed nor refuted |
| **CONFLICT** | (1, 1) | Both confirmed and refuted |

This library extends Belnap logic with **fuzzy values**, where `T` and `F` are continuous values in `[0, 1]`.

## Installation

```bash
pip install fuzzy4
```

## Quick Start

```python
from fuzzy4 import FuzzyBool, TRUE, FALSE, UNKNOWN, CONFLICT

# Create fuzzy values
x = FuzzyBool(0.8, 0.2)  # 80% confirmed, 20% refuted
y = FuzzyBool(0.6, 0.3)  # 60% confirmed, 30% refuted

# Logical operations
result = x & y           # conjunction (AND)
result = x | y           # disjunction (OR)
result = ~x              # negation (NOT)
result = x >> y          # implication (x -> y)
result = x.iff(y)        # bi-implication (x <-> y)

# Accumulate evidence
result = x + y           # combines evidence from multiple sources
result += FuzzyBool(0.5, 0.1)           # in-place accumulation
result = FuzzyBool.accumulate(x, y, z)  # accumulate many values

# Check dominant state
print(x.dominant_state())  # "true", "false", "unknown", or "conflict"
print(x.is_true())         # True if predominantly true
```

## Operations

### Negation: `~x`

Swaps confirmation and refutation:

| x | ~x |
|---|---|
| TRUE | FALSE |
| UNKNOWN | UNKNOWN |
| CONFLICT | CONFLICT |
| FALSE | TRUE |

```python
~FuzzyBool(0.8, 0.3)  # -> FuzzyBool(0.3, 0.8)
```

### Conjunction: `x & y`

Both must confirm, any refutation propagates:

| & | TRUE | UNKNOWN | CONFLICT | FALSE |
|---|------|---------|----------|-------|
| **TRUE** | TRUE | UNKNOWN | CONFLICT | FALSE |
| **UNKNOWN** | UNKNOWN | UNKNOWN | FALSE | FALSE |
| **CONFLICT** | CONFLICT | FALSE | CONFLICT | FALSE |
| **FALSE** | FALSE | FALSE | FALSE | FALSE |

Uses product t-norm for T and probabilistic s-norm for F:
- `T = Tx * Ty`
- `F = Fx + Fy - Fx * Fy`

### Disjunction: `x | y`

Any confirmation suffices, both must refute:

| \| | TRUE | UNKNOWN | CONFLICT | FALSE |
|---|------|---------|----------|-------|
| **TRUE** | TRUE | TRUE | TRUE | TRUE |
| **UNKNOWN** | TRUE | UNKNOWN | TRUE | UNKNOWN |
| **CONFLICT** | TRUE | TRUE | CONFLICT | CONFLICT |
| **FALSE** | TRUE | UNKNOWN | CONFLICT | FALSE |

Uses probabilistic s-norm for T and product t-norm for F:
- `T = Tx + Ty - Tx * Ty`
- `F = Fx * Fy`

### Implication: `x >> y`

Material implication: `x -> y = ~x | y`

| >> | TRUE | UNKNOWN | CONFLICT | FALSE |
|---|------|---------|----------|-------|
| **TRUE** | TRUE | UNKNOWN | CONFLICT | FALSE |
| **UNKNOWN** | TRUE | UNKNOWN | TRUE | UNKNOWN |
| **CONFLICT** | TRUE | TRUE | CONFLICT | CONFLICT |
| **FALSE** | TRUE | TRUE | TRUE | TRUE |

### Bi-implication: `x.iff(y)`

Equivalence: `x <-> y = (x -> y) & (y -> x)`

| iff | TRUE | UNKNOWN | CONFLICT | FALSE |
|---|------|---------|----------|-------|
| **TRUE** | TRUE | UNKNOWN | CONFLICT | FALSE |
| **UNKNOWN** | UNKNOWN | UNKNOWN | TRUE | UNKNOWN |
| **CONFLICT** | CONFLICT | TRUE | CONFLICT | CONFLICT |
| **FALSE** | FALSE | UNKNOWN | CONFLICT | TRUE |

### Evidence Accumulation: `x + y`

Combines evidence using probabilistic sum — useful for aggregating information from multiple sources:

| + | TRUE | UNKNOWN | CONFLICT | FALSE |
|---|------|---------|----------|-------|
| **TRUE** | TRUE | TRUE | CONFLICT | CONFLICT |
| **UNKNOWN** | TRUE | UNKNOWN | CONFLICT | FALSE |
| **CONFLICT** | CONFLICT | CONFLICT | CONFLICT | CONFLICT |
| **FALSE** | CONFLICT | FALSE | CONFLICT | FALSE |

```python
weak = FuzzyBool(0.3, 0.0)     # weak confirmation
result = weak + weak + weak    # -> FuzzyBool(0.657, 0.0)

# In-place accumulation
total = UNKNOWN
for source in sources:
    total += source            # accumulates evidence iteratively

# Accumulate a list of values
FuzzyBool.accumulate([source1, source2, source3])
```

Properties:
- More confirmations → T approaches 1
- More refutations → F approaches 1
- UNKNOWN is the neutral element

### Scalar Operations

```python
x = FuzzyBool(0.8, 0.6)
x * 0.5              # -> FuzzyBool(0.4, 0.3)
x / 2.0              # -> FuzzyBool(0.4, 0.3)
```

## Component Extraction

Each `FuzzyBool` has four derived properties representing the degree of each logical state:

```python
x = FuzzyBool(0.7, 0.4)

x.truth     # degree of pure truth (confirmed AND not refuted)
x.falsity   # degree of pure falsity (refuted AND not confirmed)
x.unknown   # degree of uncertainty (neither confirmed nor refuted)
x.conflict  # degree of contradiction (both confirmed and refuted)

x.as_dict()  # {"truth": ..., "falsity": ..., "unknown": ..., "conflict": ...}
```

## Use Cases

- **Knowledge bases**: Handle incomplete or contradictory information
- **Sensor fusion**: Combine readings from multiple sensors with varying reliability
- **Expert systems**: Model uncertainty in rule-based reasoning
- **Database queries**: Represent null/unknown values with more nuance than SQL's 3-valued logic

## Mathematical Background

This implementation uses:

- **Product t-norm** for conjunction: `a ⊗ b = a × b`
- **Probabilistic s-norm** for disjunction: `a ⊕ b = a + b - a × b`
- **Standard negation**: `¬a = 1 - a`

De Morgan's laws hold: `~(x & y) = ~x | ~y` and `~(x | y) = ~x & ~y`

## Development

```bash
# Clone the repository
git clone https://github.com/mihail-gribov/fuzzy4.git
cd fuzzy4

# Install with dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run tests with coverage
pytest --cov=fuzzy4
```

## License

MIT License — see [LICENSE](LICENSE) for details.

## References

- Belnap, N. D. (1977). "A useful four-valued logic"
- Fitting, M. (1994). "Kleene's Three Valued Logics and Their Children"
