"""Tests for feature extraction skeletons."""

import pytest

from open_kendo.features.footwork import FootworkAnalyzer, FootworkType
from open_kendo.features.kinematics import KinematicSnapshot, KinematicsCalculator
from open_kendo.features.trajectories import TrajectoryBuffer
from open_kendo.perception.base import Point2D, PoseResult


def test_kinematics_calculator_interface():
    """Verify KinematicsCalculator raises NotImplementedError for template methods."""
    calculator = KinematicsCalculator()
    p1 = Point2D(0.0, 0.0)
    p2 = Point2D(0.0, 1.0)
    p3 = Point2D(1.0, 1.0)

    with pytest.raises(NotImplementedError):
        calculator.compute_angle_2d(p1, p2, p3)

    with pytest.raises(NotImplementedError):
        calculator.compute_spine_angle(PoseResult())


def test_trajectory_buffer_interface():
    """Verify TrajectoryBuffer raises NotImplementedError for template methods."""
    buffer = TrajectoryBuffer(buffer_size=30)

    with pytest.raises(NotImplementedError):
        buffer.append(Point2D(0.5, 0.5), timestamp_ms=100.0)

    with pytest.raises(NotImplementedError):
        buffer.get_peak_velocity()


def test_footwork_analyzer_interface():
    """Verify FootworkAnalyzer raises NotImplementedError for template methods."""
    analyzer = FootworkAnalyzer()

    with pytest.raises(NotImplementedError):
        analyzer.compute_stance_width(PoseResult())

    with pytest.raises(NotImplementedError):
        analyzer.detect_fumikomi_impact(PoseResult(), timestamp_ms=150.0)
