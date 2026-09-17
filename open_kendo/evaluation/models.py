"""Data models for evaluation results, lifecycle phases, and integrated scores."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional

from open_kendo.evaluation.kikentaichi import KiKenTaiIchiResult
from open_kendo.evaluation.lifecycle import StrikeLifecyclePhase


class KendoStrikeType(str, Enum):
    """Primary valid datotsu targets in Kendo."""
    MEN = "men"
    KOTE = "kote"
    DO = "do"
    TSUKI = "tsuki"
    SUBURI = "suburi"


@dataclass
class PhaseSubScore:
    """Quantitative sub-score for a specific lifecycle phase."""
    phase_name: str
    raw_score: float             # In range [0.0, 100.0]
    weight: float                # Normalized weight in range [0.0, 1.0]
    weighted_score: float
    feedback_notes: List[str] = field(default_factory=list)
    diagnostics: Dict[str, float] = field(default_factory=dict)


@dataclass
class KamaeEvaluationResult:
    """Evaluation summary for Phase 1: Pre-Attack Kamae."""
    score: float                 # Range [0.0, 100.0]
    is_spine_straight: bool
    is_stance_width_correct: bool
    is_hand_angle_correct: bool
    sub_score: Optional[PhaseSubScore] = None


@dataclass
class ExecutionEvaluationResult:
    """Evaluation summary for Phase 2: Motion Execution."""
    score: float                 # Range [0.0, 100.0]
    is_spine_stable: bool        # Spine does not lean backward or hunch forward
    is_head_level: bool          # Head does not tilt sideways
    kikentaichi: Optional[KiKenTaiIchiResult] = None
    sub_score: Optional[PhaseSubScore] = None


@dataclass
class ZanshinEvaluationResult:
    """Evaluation summary for Phase 3: Post-Attack Zanshin."""
    score: float                 # Range [0.0, 100.0]
    is_recovery_smooth: bool     # Returns promptly to Kamae
    is_kensen_on_target: bool    # Sword points to throat
    is_ready_next_strike: bool   # Physical and mental alertness
    sub_score: Optional[PhaseSubScore] = None


@dataclass
class IntegratedScoreResult:
    """Final synthesized score across the complete 3-phase strike lifecycle.

    Score = (w_kamae * S_kamae) + (w_exec * S_exec) + (w_zanshin * S_zanshin)
    """
    strike_id: str
    target: KendoStrikeType
    start_timestamp_ms: float
    impact_timestamp_ms: float
    end_timestamp_ms: float
    total_score: float           # Final integrated score [0.0, 100.0]
    is_valid_technique: bool     # Meets overall pedagogical criteria
    kamae: Optional[KamaeEvaluationResult] = None
    execution: Optional[ExecutionEvaluationResult] = None
    zanshin: Optional[ZanshinEvaluationResult] = None
    coaching_summary: List[str] = field(default_factory=list)


# Backward compatibility alias
StrikeEvaluationResult = IntegratedScoreResult
TechniqueScore = PhaseSubScore
