"""Tests for evaluation and scoring engines."""

import pytest

from open_kendo.evaluation.dtw_matcher import DTWMatcher
from open_kendo.evaluation.kikentaichi import KiKenTaiIchiEvaluator, SyncQuality
from open_kendo.evaluation.models import KendoStrikeType
from open_kendo.evaluation.scorer import KendoScorer


def test_kikentaichi_evaluator_interface():
    """Verify KiKenTaiIchiEvaluator methods raise NotImplementedError."""
    evaluator = KiKenTaiIchiEvaluator()

    with pytest.raises(NotImplementedError):
        evaluator.compute_sync_score(delta_ms=50.0)


def test_dtw_matcher_interface():
    """Verify DTWMatcher methods raise NotImplementedError."""
    matcher = DTWMatcher()

    with pytest.raises(NotImplementedError):
        matcher.load_reference("non_existent.npz")


def test_scorer_interface():
    """Verify KendoScorer methods raise NotImplementedError."""
    scorer = KendoScorer()

    with pytest.raises(NotImplementedError):
        scorer.evaluate_ippon_validity(None)
