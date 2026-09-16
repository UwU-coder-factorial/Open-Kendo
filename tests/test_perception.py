"""Tests for perception base data structures and wrappers."""

import pytest
import numpy as np

from open_kendo.perception.base import (
    Keypoint,
    Point2D,
    Point3D,
    PoseResult,
    TrackedObject,
)
from open_kendo.perception.mediapipe_pose import MediaPipePoseEstimator
from open_kendo.perception.shinai_tracker import ShinaiTracker
from open_kendo.perception.yolo_pose import YOLOPoseEstimator


def test_point2d_instantiation():
    """Verify Point2D coordinate initialization."""
    pt = Point2D(x=0.5, y=0.75)
    assert pt.x == 0.5
    assert pt.y == 0.75


def test_pose_result_keypoints():
    """Verify PoseResult keypoint retrieval."""
    pose = PoseResult()
    kp = Keypoint(name="right_wrist", point_2d=Point2D(0.4, 0.6), confidence=0.95)
    pose.keypoints["right_wrist"] = kp

    retrieved = pose.get_keypoint("right_wrist")
    assert retrieved is not None
    assert retrieved.name == "right_wrist"
    assert retrieved.confidence == 0.95
    assert pose.get_keypoint("non_existent") is None


def test_mediapipe_pose_raises_not_implemented():
    """Verify MediaPipePoseEstimator skeleton raises NotImplementedError."""
    estimator = MediaPipePoseEstimator()
    dummy_frame = np.zeros((480, 640, 3), dtype=np.uint8)

    with pytest.raises(NotImplementedError):
        estimator.initialize()

    with pytest.raises(NotImplementedError):
        estimator.estimate(dummy_frame)


def test_shinai_tracker_raises_not_implemented():
    """Verify ShinaiTracker skeleton raises NotImplementedError."""
    tracker = ShinaiTracker()
    dummy_frame = np.zeros((480, 640, 3), dtype=np.uint8)

    with pytest.raises(NotImplementedError):
        tracker.track(dummy_frame)
