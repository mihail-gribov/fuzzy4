"""Tests for 4-valued fuzzy logic."""

import pytest
from fuzzy4 import FuzzyBool, TRUE, FALSE, UNKNOWN, CONFLICT


class TestConstants:
    """Test canonical constants."""

    def test_true_components(self):
        assert TRUE.t == 1.0
        assert TRUE.f == 0.0
        assert TRUE.truth == 1.0
        assert TRUE.falsity == 0.0
        assert TRUE.unknown == 0.0
        assert TRUE.conflict == 0.0

    def test_false_components(self):
        assert FALSE.t == 0.0
        assert FALSE.f == 1.0
        assert FALSE.truth == 0.0
        assert FALSE.falsity == 1.0
        assert FALSE.unknown == 0.0
        assert FALSE.conflict == 0.0

    def test_unknown_components(self):
        assert UNKNOWN.t == 0.0
        assert UNKNOWN.f == 0.0
        assert UNKNOWN.truth == 0.0
        assert UNKNOWN.falsity == 0.0
        assert UNKNOWN.unknown == 1.0
        assert UNKNOWN.conflict == 0.0

    def test_conflict_components(self):
        assert CONFLICT.t == 1.0
        assert CONFLICT.f == 1.0
        assert CONFLICT.truth == 0.0
        assert CONFLICT.falsity == 0.0
        assert CONFLICT.unknown == 0.0
        assert CONFLICT.conflict == 1.0


class TestNegation:
    """Test NOT operation: ~(T, F) = (F, T)"""

    def test_not_true(self):
        assert ~TRUE == FALSE

    def test_not_false(self):
        assert ~FALSE == TRUE

    def test_not_unknown(self):
        assert ~UNKNOWN == UNKNOWN

    def test_not_conflict(self):
        assert ~CONFLICT == CONFLICT

    def test_double_negation(self):
        x = FuzzyBool(0.7, 0.3)
        assert ~~x == x


class TestConjunction:
    """
    Test AND operation.
    T = max(0, Tx + Ty - 1)
    F = min(1, Fx + Fy)
    """

    def test_and_truth_table(self):
        # T & T = T
        assert (TRUE & TRUE) == TRUE
        # T & F = F
        assert (TRUE & FALSE) == FALSE
        # T & U = U
        assert (TRUE & UNKNOWN) == UNKNOWN
        # T & C = C
        assert (TRUE & CONFLICT) == CONFLICT

        # F & T = F
        assert (FALSE & TRUE) == FALSE
        # F & F = F
        assert (FALSE & FALSE) == FALSE
        # F & U = F
        assert (FALSE & UNKNOWN) == FALSE
        # F & C = F
        assert (FALSE & CONFLICT) == FALSE

        # U & T = U
        assert (UNKNOWN & TRUE) == UNKNOWN
        # U & F = F
        assert (UNKNOWN & FALSE) == FALSE
        # U & U = U
        assert (UNKNOWN & UNKNOWN) == UNKNOWN
        # U & C = F (T=0, F=1)
        result = UNKNOWN & CONFLICT
        assert result.t == 0.0
        assert result.f == 1.0

        # C & T = C
        assert (CONFLICT & TRUE) == CONFLICT
        # C & F = F
        assert (CONFLICT & FALSE) == FALSE
        # C & U = F (T=0, F=1)
        result = CONFLICT & UNKNOWN
        assert result.t == 0.0
        assert result.f == 1.0
        # C & C = C
        assert (CONFLICT & CONFLICT) == CONFLICT

    def test_and_fuzzy_values(self):
        x = FuzzyBool(0.8, 0.2)
        y = FuzzyBool(0.6, 0.3)
        result = x & y
        # T = 0.8 * 0.6 = 0.48 (product t-norm)
        assert abs(result.t - 0.48) < 1e-9
        # F = 0.2 + 0.3 - 0.2*0.3 = 0.44 (probabilistic s-norm)
        assert abs(result.f - 0.44) < 1e-9


class TestDisjunction:
    """
    Test OR operation.
    T = min(1, Tx + Ty)
    F = max(0, Fx + Fy - 1)
    """

    def test_or_truth_table(self):
        # T | T = T
        assert (TRUE | TRUE) == TRUE
        # T | F = T
        assert (TRUE | FALSE) == TRUE
        # T | U = T
        assert (TRUE | UNKNOWN) == TRUE
        # T | C = T
        assert (TRUE | CONFLICT) == TRUE

        # F | T = T
        assert (FALSE | TRUE) == TRUE
        # F | F = F
        assert (FALSE | FALSE) == FALSE
        # F | U = U
        assert (FALSE | UNKNOWN) == UNKNOWN
        # F | C = C
        assert (FALSE | CONFLICT) == CONFLICT

        # U | T = T
        assert (UNKNOWN | TRUE) == TRUE
        # U | F = U
        assert (UNKNOWN | FALSE) == UNKNOWN
        # U | U = U
        assert (UNKNOWN | UNKNOWN) == UNKNOWN
        # U | C = T (T=1, F=0)
        result = UNKNOWN | CONFLICT
        assert result.t == 1.0
        assert result.f == 0.0

        # C | T = T
        assert (CONFLICT | TRUE) == TRUE
        # C | F = C
        assert (CONFLICT | FALSE) == CONFLICT
        # C | U = T (T=1, F=0)
        result = CONFLICT | UNKNOWN
        assert result.t == 1.0
        assert result.f == 0.0
        # C | C = C
        assert (CONFLICT | CONFLICT) == CONFLICT

    def test_or_fuzzy_values(self):
        x = FuzzyBool(0.3, 0.7)
        y = FuzzyBool(0.4, 0.8)
        result = x | y
        # T = 0.3 + 0.4 - 0.3*0.4 = 0.58 (probabilistic s-norm)
        assert abs(result.t - 0.58) < 1e-9
        # F = 0.7 * 0.8 = 0.56 (product t-norm)
        assert abs(result.f - 0.56) < 1e-9


class TestImplication:
    """Test implication: x -> y = ~x | y"""

    def test_implication_truth_table(self):
        # T -> T = T
        assert (TRUE >> TRUE) == TRUE
        # T -> F = F
        assert (TRUE >> FALSE) == FALSE
        # T -> U = U
        assert (TRUE >> UNKNOWN) == UNKNOWN
        # T -> C = C
        assert (TRUE >> CONFLICT) == CONFLICT

        # F -> anything = T
        assert (FALSE >> TRUE) == TRUE
        assert (FALSE >> FALSE) == TRUE
        assert (FALSE >> UNKNOWN) == TRUE
        assert (FALSE >> CONFLICT) == TRUE


class TestBiimplication:
    """Test bi-implication: x <-> y = (x -> y) & (y -> x)"""

    def test_iff_reflexive(self):
        assert TRUE.iff(TRUE) == TRUE
        assert FALSE.iff(FALSE) == TRUE

    def test_iff_opposite(self):
        assert TRUE.iff(FALSE) == FALSE
        assert FALSE.iff(TRUE) == FALSE


class TestComponentExtraction:
    """Test extraction of 4 components."""

    def test_partial_values(self):
        # Partially true, partially unknown
        x = FuzzyBool(0.6, 0.0)
        assert x.truth > 0
        assert x.unknown > 0
        assert x.falsity == 0.0
        assert x.conflict == 0.0

    def test_mixed_values(self):
        # Some conflict present
        x = FuzzyBool(0.7, 0.4)
        components = x.as_dict()
        # All components should sum to <= 1 for boundary cases
        assert all(0 <= v <= 1 for v in components.values())

    def test_dominant_state(self):
        assert TRUE.dominant_state() == "true"
        assert FALSE.dominant_state() == "false"
        assert UNKNOWN.dominant_state() == "unknown"
        assert CONFLICT.dominant_state() == "conflict"


class TestUtilityMethods:
    """Test utility methods."""

    def test_from_crisp(self):
        assert FuzzyBool.from_crisp(True) == TRUE
        assert FuzzyBool.from_crisp(False) == FALSE

    def test_from_probability(self):
        x = FuzzyBool.from_probability(0.8)
        assert abs(x.t - 0.8) < 1e-9
        assert abs(x.f - 0.2) < 1e-9

    def test_clamping(self):
        x = FuzzyBool(1.5, -0.3)
        assert x.t == 1.0
        assert x.f == 0.0

    def test_as_tuple(self):
        x = FuzzyBool(0.5, 0.3)
        assert x.as_tuple() == (0.5, 0.3)


class TestDeMorganLaws:
    """Test De Morgan's laws hold."""

    def test_de_morgan_and(self):
        # ~(x & y) = ~x | ~y
        x = FuzzyBool(0.7, 0.2)
        y = FuzzyBool(0.5, 0.4)
        left = ~(x & y)
        right = (~x) | (~y)
        assert abs(left.t - right.t) < 1e-9
        assert abs(left.f - right.f) < 1e-9

    def test_de_morgan_or(self):
        # ~(x | y) = ~x & ~y
        x = FuzzyBool(0.7, 0.2)
        y = FuzzyBool(0.5, 0.4)
        left = ~(x | y)
        right = (~x) & (~y)
        assert abs(left.t - right.t) < 1e-9
        assert abs(left.f - right.f) < 1e-9


class TestAddition:
    """Test + operator (accumulation with probabilistic sum)."""

    def test_add_basic(self):
        a = FuzzyBool(0.5, 0.3)
        b = FuzzyBool(0.4, 0.2)
        result = a + b
        # T = 1 - (1 - 0.5) * (1 - 0.4) = 1 - 0.5 * 0.6 = 0.7
        # F = 1 - (1 - 0.3) * (1 - 0.2) = 1 - 0.7 * 0.8 = 0.44
        assert abs(result.t - 0.7) < 1e-9
        assert abs(result.f - 0.44) < 1e-9

    def test_add_with_unknown(self):
        # UNKNOWN is neutral element
        assert TRUE + UNKNOWN == TRUE
        assert FALSE + UNKNOWN == FALSE
        assert UNKNOWN + UNKNOWN == UNKNOWN

    def test_add_true_true(self):
        # TRUE + TRUE = TRUE (saturates at 1)
        assert TRUE + TRUE == TRUE

    def test_add_false_false(self):
        # FALSE + FALSE = FALSE (saturates at 1 for F)
        assert FALSE + FALSE == FALSE

    def test_add_accumulates_evidence(self):
        # Multiple weak confirmations accumulate
        weak = FuzzyBool(0.3, 0.0)
        result = weak + weak + weak
        # T = 1 - (0.7)^3 = 1 - 0.343 = 0.657
        assert abs(result.t - 0.657) < 1e-9
        assert result.f == 0.0


class TestMultiplication:
    """Test * operator (component-wise multiplication)."""

    def test_mul_fuzzy_values(self):
        a = FuzzyBool(0.8, 0.6)
        b = FuzzyBool(0.5, 0.4)
        result = a * b
        assert abs(result.t - 0.4) < 1e-9
        assert abs(result.f - 0.24) < 1e-9

    def test_mul_with_true(self):
        a = FuzzyBool(0.5, 0.3)
        result = a * TRUE
        # TRUE = (1, 0), so result = (0.5*1, 0.3*0) = (0.5, 0)
        assert abs(result.t - 0.5) < 1e-9
        assert result.f == 0.0

    def test_mul_with_unknown(self):
        a = FuzzyBool(0.5, 0.3)
        assert a * UNKNOWN == UNKNOWN

    def test_mul_scalar(self):
        a = FuzzyBool(0.8, 0.6)
        result = a * 0.5
        assert abs(result.t - 0.4) < 1e-9
        assert abs(result.f - 0.3) < 1e-9

    def test_rmul_scalar(self):
        a = FuzzyBool(0.8, 0.6)
        result = 0.5 * a
        assert abs(result.t - 0.4) < 1e-9
        assert abs(result.f - 0.3) < 1e-9


class TestDivision:
    """Test / operator (component-wise division)."""

    def test_div_fuzzy_values(self):
        a = FuzzyBool(0.4, 0.3)
        b = FuzzyBool(0.8, 0.6)
        result = a / b
        # 0.4/0.8 = 0.5, 0.3/0.6 = 0.5
        assert abs(result.t - 0.5) < 1e-9
        assert abs(result.f - 0.5) < 1e-9

    def test_div_clamping(self):
        a = FuzzyBool(0.8, 0.6)
        b = FuzzyBool(0.4, 0.3)
        result = a / b
        # 0.8/0.4 = 2.0 -> clamped to 1.0
        # 0.6/0.3 = 2.0 -> clamped to 1.0
        assert result.t == 1.0
        assert result.f == 1.0

    def test_div_by_true(self):
        a = FuzzyBool(0.5, 0.3)
        result = a / TRUE
        # T = 0.5 / 1 = 0.5, F = 0.3 / 0 = 0
        assert abs(result.t - 0.5) < 1e-9
        assert result.f == 0.0

    def test_div_scalar(self):
        a = FuzzyBool(0.8, 0.6)
        result = a / 2.0
        assert abs(result.t - 0.4) < 1e-9
        assert abs(result.f - 0.3) < 1e-9

    def test_div_by_zero_component(self):
        a = FuzzyBool(0.5, 0.5)
        b = FuzzyBool(0.0, 0.5)
        result = a / b
        assert result.t == 0.0  # division by zero -> 0
        assert abs(result.f - 1.0) < 1e-9

    def test_div_by_zero_scalar(self):
        a = FuzzyBool(0.5, 0.5)
        result = a / 0
        assert result == UNKNOWN


class TestAccumulate:
    """Test accumulate operation (uses + operator)."""

    def test_accumulate_two_values(self):
        a = FuzzyBool(0.5, 0.3)
        b = FuzzyBool(0.4, 0.2)
        result = FuzzyBool.accumulate(a, b)
        # Same as a + b
        assert abs(result.t - 0.7) < 1e-9
        assert abs(result.f - 0.44) < 1e-9

    def test_accumulate_multiple_args(self):
        result = FuzzyBool.accumulate(TRUE, FALSE, UNKNOWN)
        # TRUE + FALSE + UNKNOWN = TRUE + FALSE = (1, 1) CONFLICT
        assert result.t == 1.0
        assert result.f == 1.0

    def test_accumulate_list(self):
        values = [FuzzyBool(0.3, 0.0), FuzzyBool(0.3, 0.0), FuzzyBool(0.3, 0.0)]
        result = FuzzyBool.accumulate(values)
        # T = 1 - (0.7)^3 = 0.657
        assert abs(result.t - 0.657) < 1e-9
        assert result.f == 0.0

    def test_accumulate_mixed_args_and_list(self):
        a = FuzzyBool(0.5, 0.0)
        b = FuzzyBool(0.3, 0.0)
        c = FuzzyBool(0.2, 0.0)
        result = FuzzyBool.accumulate(a, [b, c])
        expected = a + b + c
        assert result == expected

    def test_accumulate_single_value(self):
        result = FuzzyBool.accumulate(TRUE)
        assert result == TRUE

    def test_accumulate_same_values(self):
        result = FuzzyBool.accumulate(TRUE, TRUE, TRUE)
        assert result == TRUE

    def test_accumulate_empty_raises(self):
        with pytest.raises(ValueError):
            FuzzyBool.accumulate([])

    def test_accumulate_invalid_type_raises(self):
        with pytest.raises(TypeError):
            FuzzyBool.accumulate(TRUE, "not a fuzzy bool")

    def test_accumulate_generator(self):
        gen = (x for x in [TRUE, FALSE])
        result = FuzzyBool.accumulate(gen)
        # TRUE + FALSE = CONFLICT
        assert result.t == 1.0
        assert result.f == 1.0


class TestVersion:
    """Test package metadata."""

    def test_version_exists(self):
        import fuzzy4
        assert hasattr(fuzzy4, '__version__')
        assert fuzzy4.__version__ == "0.1.0"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
