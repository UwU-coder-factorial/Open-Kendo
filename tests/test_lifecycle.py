"""Unit tests for the 3-Phase State & Motion Lifecycle Tracker."""

import pytest

from open_kendo.evaluation.kamae import KamaeEvaluator, KamaeMetrics
from open_kendo.evaluation.lifecycle import (
    StateLifecycleTracker,
    StrikeLifecyclePhase,
)
from open_kendo.evaluation.models import (
    ExecutionEvaluationResult,
    IntegratedScoreResult,
    KamaeEvaluationResult,
    KendoStrikeType,
    ZanshinEvaluationResult,
)
from open_kendo.evaluation.scorer import KendoScorer
from open_kendo.evaluation.zanshin import ZanshinEvaluator, ZanshinMetrics
from open_kendo.perception.base import PoseResult


def test_lifecycle_phase_enum_values():
    """Verify all 3 lifecycle phases are correctly defined."""
    assert StrikeLifecyclePhase.IDLE.value == "idle"
    assert StrikeLifecyclePhase.PRE_ATTACK_KAMAE.value == "pre_attack_kamae"
    assert StrikeLifecyclePhase.MOTION_EXECUTION.value == "motion_execution"
    assert StrikeLifecyclePhase.POST_ATTACK_ZANSHIN.value == "post_attack_zanshin"
    assert StrikeLifecyclePhase.COMPLETED.value == "completed"


def test_state_lifecycle_tracker_interface():
    """Verify StateLifecycleTracker methods raise NotImplementedError in template."""
    tracker = StateLifecycleTracker()
    assert tracker.current_phase == StrikeLifecyclePhase.IDLE

    with pytest.raises(NotImplementedError):
        tracker.update(PoseResult(), timestamp_ms=100.0)

    with pytest.raises(NotImplementedError):
        tracker.reset()


def test_kamae_evaluator_interface():
    """Verify KamaeEvaluator template raises NotImplementedError."""
    evaluator = KamaeEvaluator()

    with pytest.raises(NotImplementedError):
        evaluator.extract_metrics(PoseResult())

    dummy_metrics = KamaeMetrics(
        spine_vertical_tilt_deg=2.0,
        stance_width_ratio=0.28,
        left_heel_elevation_ratio=0.03,
        left_hand_navel_distance=0.15,
        right_elbow_angle_deg=145.0,
        kensen_centerline_offset=0.02,
        kamae_hold_duration_ms=400.0,
    )
    with pytest.raises(NotImplementedError):
        evaluator.evaluate_posture(dummy_metrics)


def test_zanshin_evaluator_interface():
    """Verify ZanshinEvaluator template raises NotImplementedError."""
    evaluator = ZanshinEvaluator()

    with pytest.raises(NotImplementedError):
        evaluator.extract_metrics([PoseResult()])

    dummy_metrics = ZanshinMetrics(
        recovery_duration_ms=500.0,
        kensen_centerline_offset=0.03,
        spine_upright_score=95.0,
        body_balance_stability=90.0,
        is_ready_for_next_strike=True,
    )
    with pytest.raises(NotImplementedError):
        evaluator.evaluate_zanshin(dummy_metrics)


def test_integrated_scorer_interface():
    """Verify KendoScorer.score_integrated_strike raises NotImplementedError."""
    scorer = KendoScorer()
    kamae_res = KamaeEvaluationResult(
        score=90.0, is_spine_straight=True, is_stance_width_correct=True, is_hand_angle_correct=True
    )
    exec_res = ExecutionEvaluationResult(
        score=85.0, is_spine_stable=True, is_head_level=True
    )
    zanshin_res = ZanshinEvaluationResult(
        score=88.0, is_recovery_smooth=True, is_kensen_on_target=True, is_ready_next_strike=True
    )

    with pytest.raises(NotImplementedError):
        scorer.score_integrated_strike(
            target=KendoStrikeType.MEN,
            kamae_result=kamae_res,
            execution_result=exec_res,
            zanshin_result=zanshin_res,
        )
