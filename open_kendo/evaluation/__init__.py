"""Evaluation, lifecycle tracking, and scoring engine for Open-Kendo."""

from open_kendo.evaluation.dtw_matcher import DTWMatchResult, DTWMatcher
from open_kendo.evaluation.kamae import KamaeEvaluator, KamaeMetrics
from open_kendo.evaluation.kikentaichi import (
    KiKenTaiIchiEvaluator,
    KiKenTaiIchiResult,
    SyncQuality,
)
from open_kendo.evaluation.lifecycle import (
    LifecycleTransitionEvent,
    StateLifecycleTracker,
    StrikeLifecyclePhase,
)
from open_kendo.evaluation.models import (
    ExecutionEvaluationResult,
    IntegratedScoreResult,
    KamaeEvaluationResult,
    KendoStrikeType,
    PhaseSubScore,
    StrikeEvaluationResult,
    TechniqueScore,
    ZanshinEvaluationResult,
)
from open_kendo.evaluation.scorer import KendoScorer
from open_kendo.evaluation.zanshin import ZanshinEvaluator, ZanshinMetrics

__all__ = [
    # Lifecycle
    "StrikeLifecyclePhase",
    "StateLifecycleTracker",
    "LifecycleTransitionEvent",
    # Evaluators
    "KamaeEvaluator",
    "KamaeMetrics",
    "KiKenTaiIchiEvaluator",
    "KiKenTaiIchiResult",
    "SyncQuality",
    "ZanshinEvaluator",
    "ZanshinMetrics",
    "DTWMatcher",
    "DTWMatchResult",
    "KendoScorer",
    # Models
    "KendoStrikeType",
    "PhaseSubScore",
    "TechniqueScore",
    "KamaeEvaluationResult",
    "ExecutionEvaluationResult",
    "ZanshinEvaluationResult",
    "IntegratedScoreResult",
    "StrikeEvaluationResult",
]
