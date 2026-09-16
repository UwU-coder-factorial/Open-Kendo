"""Data models for evaluation results and scores."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional


class KendoStrikeType(str, Enum):
    """Primary valid datotsu targets in Kendo."""
    MEN = "men"
    KOTE = "kote"
    DO = "do"
    TSUKI = "tsuki"
    SUBURI = "suburi"


@dataclass
class TechniqueScore:
    """Sub-score component breakdown."""
    pillar_name: str
    score: float             # In range [0.0, 100.0]
    weight: float            # In range [0.0, 1.0]
    weighted_score: float
    feedback_notes: List[str] = field(default_factory=list)


@dataclass
class StrikeEvaluationResult:
    """Comprehensive evaluation report for a single detected strike."""
    strike_id: str
    target: KendoStrikeType
    start_timestamp_ms: float
    impact_timestamp_ms: float
    end_timestamp_ms: float
    total_score: float       # Final weighted score [0.0, 100.0]
    is_ippon_candidate: bool = False
    pillars: Dict[str, TechniqueScore] = field(default_factory=dict)
    diagnostics: Dict[str, float] = field(default_factory=dict)
