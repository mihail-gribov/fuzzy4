"""
fuzzy4 - 4-valued fuzzy logic library based on Belnap logic.

Each proposition is represented as a 2-component truth vector (T, F):
- T: degree of confirmation (truth)
- F: degree of refutation (falsity)

No constraint T + F = 1, allowing for four canonical states:
- TRUE:     (1, 0) - fully confirmed, not refuted
- FALSE:    (0, 1) - not confirmed, fully refuted
- UNKNOWN:  (0, 0) - neither confirmed nor refuted
- CONFLICT: (1, 1) - both confirmed and refuted

Example:
    >>> from fuzzy4 import FuzzyBool, TRUE, FALSE, UNKNOWN
    >>> x = FuzzyBool(0.8, 0.2)
    >>> y = FuzzyBool(0.6, 0.3)
    >>> result = x & y  # conjunction
    >>> print(result)
    (0.48, 0.44) [true]
"""

from .core import FuzzyBool, TRUE, FALSE, UNKNOWN, CONFLICT

__version__ = "0.1.0"
__all__ = ["FuzzyBool", "TRUE", "FALSE", "UNKNOWN", "CONFLICT"]
