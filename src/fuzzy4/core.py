"""
Core implementation of 4-valued fuzzy logic.

Operations use Product t-norm:
- T-norm (AND): a * b = a * b
- S-norm (OR):  a + b = a + b - a*b (probabilistic sum)
- NOT:          ~a = 1 - a
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Union


def _clamp(value: float) -> float:
    """Clamp value to [0, 1] range."""
    return max(0.0, min(1.0, value))


def _t_norm(a: float, b: float) -> float:
    """Product t-norm: a * b"""
    return a * b


def _s_norm(a: float, b: float) -> float:
    """Probabilistic s-norm: a + b - a*b"""
    return a + b - a * b


@dataclass(frozen=True, slots=True)
class FuzzyBool:
    """
    4-valued fuzzy logic variable.

    Represents a proposition as (T, F) vector where:
    - T: degree of confirmation [0, 1]
    - F: degree of refutation [0, 1]

    Canonical states:
    - TRUE:     (1, 0) - fully confirmed, not refuted
    - FALSE:    (0, 1) - not confirmed, fully refuted
    - UNKNOWN:  (0, 0) - neither confirmed nor refuted
    - CONFLICT: (1, 1) - both confirmed and refuted
    """

    t: float  # truth/confirmation degree
    f: float  # falsity/refutation degree

    def __post_init__(self):
        # Validate and clamp values
        object.__setattr__(self, 't', _clamp(self.t))
        object.__setattr__(self, 'f', _clamp(self.f))

    # ==================== Component Extraction ====================

    @property
    def truth(self) -> float:
        """
        Degree of pure truth: confirmed AND not refuted.
        High when T is high and F is low.
        """
        return _t_norm(self.t, 1.0 - self.f)

    @property
    def falsity(self) -> float:
        """
        Degree of pure falsity: refuted AND not confirmed.
        High when F is high and T is low.
        """
        return _t_norm(self.f, 1.0 - self.t)

    @property
    def unknown(self) -> float:
        """
        Degree of uncertainty: neither confirmed nor refuted.
        High when both T and F are low.
        """
        return _t_norm(1.0 - self.t, 1.0 - self.f)

    @property
    def conflict(self) -> float:
        """
        Degree of contradiction: both confirmed AND refuted.
        High when both T and F are high.
        """
        return _t_norm(self.t, self.f)

    # ==================== Raw Components ====================

    @property
    def confirmation(self) -> float:
        """Raw confirmation degree (T component)."""
        return self.t

    @property
    def refutation(self) -> float:
        """Raw refutation degree (F component)."""
        return self.f

    # ==================== Logical Operations ====================

    def __invert__(self) -> FuzzyBool:
        """
        Negation: ~x

        ~(T, F) = (F, T)
        Swaps confirmation and refutation.
        """
        return FuzzyBool(self.f, self.t)

    def __and__(self, other: FuzzyBool) -> FuzzyBool:
        """
        Conjunction: x & y

        T = max(0, Tx + Ty - 1)  -- both must confirm
        F = min(1, Fx + Fy)      -- any refutation suffices
        """
        if not isinstance(other, FuzzyBool):
            return NotImplemented
        return FuzzyBool(
            t=_t_norm(self.t, other.t),
            f=_s_norm(self.f, other.f)
        )

    def __or__(self, other: FuzzyBool) -> FuzzyBool:
        """
        Disjunction: x | y

        T = min(1, Tx + Ty)      -- any confirmation suffices
        F = max(0, Fx + Fy - 1)  -- both must refute
        """
        if not isinstance(other, FuzzyBool):
            return NotImplemented
        return FuzzyBool(
            t=_s_norm(self.t, other.t),
            f=_t_norm(self.f, other.f)
        )

    def __rshift__(self, other: FuzzyBool) -> FuzzyBool:
        """
        Implication: x >> y (x -> y)

        x -> y := ~x | y
        """
        if not isinstance(other, FuzzyBool):
            return NotImplemented
        return (~self) | other

    def __eq__(self, other: object) -> bool:
        """Equality check with tolerance."""
        if not isinstance(other, FuzzyBool):
            return NotImplemented
        return abs(self.t - other.t) < 1e-9 and abs(self.f - other.f) < 1e-9

    def __hash__(self) -> int:
        return hash((round(self.t, 9), round(self.f, 9)))

    # ==================== Bi-implication ====================

    def iff(self, other: FuzzyBool) -> FuzzyBool:
        """
        Bi-implication (equivalence): x <-> y

        x <-> y := (x -> y) & (y -> x)
        """
        return (self >> other) & (other >> self)

    def __add__(self, other: FuzzyBool) -> FuzzyBool:
        """
        Accumulation: x + y

        Combines evidence using probabilistic sum (s-norm):
        T = 1 - (1 - Tx) * (1 - Ty)
        F = 1 - (1 - Fx) * (1 - Fy)

        Properties:
        - More confirmations -> higher T (approaches 1)
        - More refutations -> higher F (approaches 1)
        - Neutral element: UNKNOWN (0, 0)
        """
        if not isinstance(other, FuzzyBool):
            return NotImplemented
        return FuzzyBool(
            t=_s_norm(self.t, other.t),
            f=_s_norm(self.f, other.f)
        )

    def __mul__(self, other: Union[FuzzyBool, float]) -> FuzzyBool:
        """
        Component-wise multiplication: x * y

        T = Tx * Ty
        F = Fx * Fy

        Also supports scalar multiplication: x * 0.5
        """
        if isinstance(other, FuzzyBool):
            return FuzzyBool(
                t=self.t * other.t,
                f=self.f * other.f
            )
        elif isinstance(other, (int, float)):
            return FuzzyBool(
                t=self.t * other,
                f=self.f * other
            )
        return NotImplemented

    def __rmul__(self, other: float) -> FuzzyBool:
        """Support scalar * FuzzyBool."""
        return self.__mul__(other)

    def __truediv__(self, other: Union[FuzzyBool, float]) -> FuzzyBool:
        """
        Component-wise division: x / y

        T = Tx / Ty
        F = Fx / Fy

        Also supports scalar division: x / 2.0
        Division by zero returns 0 for that component.
        """
        if isinstance(other, FuzzyBool):
            return FuzzyBool(
                t=self.t / other.t if other.t != 0 else 0.0,
                f=self.f / other.f if other.f != 0 else 0.0
            )
        elif isinstance(other, (int, float)):
            if other == 0:
                return FuzzyBool(0.0, 0.0)
            return FuzzyBool(
                t=self.t / other,
                f=self.f / other
            )
        return NotImplemented

    # ==================== Utility Methods ====================

    def is_true(self, threshold: float = 0.5) -> bool:
        """Check if predominantly true."""
        return self.truth >= threshold

    def is_false(self, threshold: float = 0.5) -> bool:
        """Check if predominantly false."""
        return self.falsity >= threshold

    def is_unknown(self, threshold: float = 0.5) -> bool:
        """Check if predominantly unknown."""
        return self.unknown >= threshold

    def is_conflict(self, threshold: float = 0.5) -> bool:
        """Check if predominantly contradictory."""
        return self.conflict >= threshold

    def dominant_state(self) -> str:
        """Return the dominant logical state."""
        components = {
            "true": self.truth,
            "false": self.falsity,
            "unknown": self.unknown,
            "conflict": self.conflict
        }
        return max(components, key=components.get)

    def as_tuple(self) -> tuple[float, float]:
        """Return as (T, F) tuple."""
        return (self.t, self.f)

    def as_dict(self) -> dict[str, float]:
        """Return all 4 components as dictionary."""
        return {
            "truth": self.truth,
            "falsity": self.falsity,
            "unknown": self.unknown,
            "conflict": self.conflict
        }

    def __repr__(self) -> str:
        return f"FuzzyBool(t={self.t:.3f}, f={self.f:.3f})"

    def __str__(self) -> str:
        state = self.dominant_state()
        return f"({self.t:.2f}, {self.f:.2f}) [{state}]"

    # ==================== Class Methods ====================

    @classmethod
    def from_crisp(cls, value: bool) -> FuzzyBool:
        """Create from crisp boolean."""
        return TRUE if value else FALSE

    @classmethod
    def accumulate(cls, *args: Union[FuzzyBool, list[FuzzyBool]]) -> FuzzyBool:
        """
        Accumulate multiple FuzzyBool values using probabilistic sum.

        Combines evidence: T = 1 - prod(1 - Ti), F = 1 - prod(1 - Fi)

        Usage:
            # Multiple arguments
            FuzzyBool.accumulate(a, b, c)

            # Single list/iterable
            FuzzyBool.accumulate([a, b, c])
            FuzzyBool.accumulate(values)

            # Mixed (flattens automatically)
            FuzzyBool.accumulate(a, [b, c], d)

        Returns:
            FuzzyBool with accumulated T and F components.

        Raises:
            ValueError: If no values provided.
        """
        # Flatten all arguments into a single list
        values: list[FuzzyBool] = []
        for arg in args:
            if isinstance(arg, FuzzyBool):
                values.append(arg)
            elif hasattr(arg, '__iter__'):
                for item in arg:
                    if isinstance(item, FuzzyBool):
                        values.append(item)
                    else:
                        raise TypeError(f"Expected FuzzyBool, got {type(item).__name__}")
            else:
                raise TypeError(f"Expected FuzzyBool or iterable, got {type(arg).__name__}")

        if not values:
            raise ValueError("Cannot accumulate empty sequence")

        # Use + operator (probabilistic sum) to accumulate
        result = values[0]
        for v in values[1:]:
            result = result + v

        return result

    @classmethod
    def from_probability(cls, p: float) -> FuzzyBool:
        """
        Create from single probability value.
        Assumes complementary truth/falsity: (p, 1-p).
        """
        p = _clamp(p)
        return cls(t=p, f=1.0 - p)


# ==================== Constants ====================

TRUE = FuzzyBool(1.0, 0.0)
FALSE = FuzzyBool(0.0, 1.0)
UNKNOWN = FuzzyBool(0.0, 0.0)
CONFLICT = FuzzyBool(1.0, 1.0)
