#!/usr/bin/env python3
"""Extract MediaPipe Pose Keypoints and Biomechanical Metrics for Kendo Kamae Gold Standards.

This script processes authentic reference images of Chudan-no-Kamae in data/raw/kamae/,
extracts 33 human pose landmarks using Google MediaPipe Pose Landmarker (Heavy model),
calculates core static biomechanical metrics:
  1. Spine tilt angle (Ear -> Shoulder -> Hip vs. vertical gravity vector).
  2. Elbow angles (Shoulder -> Elbow -> Wrist for both left and right arms).
  3. Left hand position (relative to navel / Tanden region).
Outputs the structured baseline data to data/gold_standards/kamae_baseline.json
and generates diagnostic annotated visualizations in data/outputs/annotated_kamae/.
"""

import json
import math
import os
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import cv2
import numpy as np

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

# Landmark indices defined in MediaPipe Pose
LANDMARK_NAMES = [
    "NOSE",
    "LEFT_EYE_INNER",
    "LEFT_EYE",
    "LEFT_EYE_OUTER",
    "RIGHT_EYE_INNER",
    "RIGHT_EYE",
    "RIGHT_EYE_OUTER",
    "LEFT_EAR",
    "RIGHT_EAR",
    "MOUTH_LEFT",
    "MOUTH_RIGHT",
    "LEFT_SHOULDER",
    "RIGHT_SHOULDER",
    "LEFT_ELBOW",
    "RIGHT_ELBOW",
    "LEFT_WRIST",
    "RIGHT_WRIST",
    "LEFT_PINKY",
    "RIGHT_PINKY",
    "LEFT_INDEX",
    "RIGHT_INDEX",
    "LEFT_THUMB",
    "RIGHT_THUMB",
    "LEFT_HIP",
    "RIGHT_HIP",
    "LEFT_KNEE",
    "RIGHT_KNEE",
    "LEFT_ANKLE",
    "RIGHT_ANKLE",
    "LEFT_HEEL",
    "RIGHT_HEEL",
    "LEFT_FOOT_INDEX",
    "RIGHT_FOOT_INDEX",
]

POSE_CONNECTIONS = [
    (11, 12),  # shoulders
    (11, 13), (13, 15),  # left arm
    (12, 14), (14, 16),  # right arm
    (11, 23), (12, 24),  # torso sides
    (23, 24),  # hips
    (23, 25), (25, 27), (27, 29), (29, 31),  # left leg
    (24, 26), (26, 28), (28, 30), (30, 32),  # right leg
    (7, 11), (8, 12),  # ear to shoulder
    (9, 10), (0, 1), (0, 4),  # head features
]

MODEL_URL = "https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_heavy/float16/latest/pose_landmarker_heavy.task"
MODEL_PATH = PROJECT_ROOT / "models" / "pose_landmarker_heavy.task"


def ensure_model_exists() -> Path:
    """Download the heavy pose landmarker model if not present."""
    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    if not MODEL_PATH.exists():
        print(f"Downloading MediaPipe model to {MODEL_PATH}...")
        urllib.request.urlretrieve(MODEL_URL, str(MODEL_PATH))
        print("Model downloaded successfully.")
    return MODEL_PATH


def calculate_angle_2d(a: np.ndarray, b: np.ndarray, c: np.ndarray) -> float:
    """Calculate the interior angle at vertex b between vectors ba and bc in degrees."""
    ba = a - b
    bc = c - b
    norm_ba = np.linalg.norm(ba)
    norm_bc = np.linalg.norm(bc)
    if norm_ba < 1e-6 or norm_bc < 1e-6:
        return 0.0
    cosine = np.dot(ba, bc) / (norm_ba * norm_bc)
    cosine = np.clip(cosine, -1.0, 1.0)
    return float(np.degrees(np.arccos(cosine)))


def calculate_angle_3d(a: np.ndarray, b: np.ndarray, c: np.ndarray) -> float:
    """Calculate 3D angle at vertex b between vectors ba and bc in degrees."""
    return calculate_angle_2d(a, b, c)


def calculate_tilt_angle_from_vertical(vector: np.ndarray, vertical_ref: Optional[np.ndarray] = None) -> float:
    """Calculate deviation angle of a vector from vertical axis (upwards).

    In normalized 2D image coordinates:
      - y increases downwards, so vertical upwards direction is [0, -1].
    In 3D world coordinates (MediaPipe World Landmarks):
      - y is negative upwards (or positive downwards depending on orientation), vertical is [0, -1, 0].
    """
    if vertical_ref is None:
        if len(vector) == 2:
            vertical_ref = np.array([0.0, -1.0])
        else:
            vertical_ref = np.array([0.0, -1.0, 0.0])

    norm_v = np.linalg.norm(vector)
    norm_ref = np.linalg.norm(vertical_ref)
    if norm_v < 1e-6:
        return 0.0
    cosine = np.dot(vector, vertical_ref) / (norm_v * norm_ref)
    cosine = np.clip(cosine, -1.0, 1.0)
    return float(np.degrees(np.arccos(cosine)))


def compute_kamae_metrics(
    landmarks_norm: List[Dict[str, float]],
    landmarks_world: List[Dict[str, float]],
    img_width: int,
    img_height: int,
) -> Dict[str, Any]:
    """Compute biomechanical metrics for Kendo Chudan-no-Kamae.

    Calculates:
      1. Spine tilt: Trunk (Hip -> Shoulder) and Full Spine (Hip -> Ear) vs vertical.
      2. Spine alignment: Interior angle Ear -> Shoulder -> Hip.
      3. Elbow angles: Left and right Shoulder -> Elbow -> Wrist (both 2D & 3D).
      4. Left hand position relative to navel (Tanden) in normalized, pixel, and metric units.
    """
    # Helper to extract point as array
    def p2d(idx: int) -> np.ndarray:
        return np.array([landmarks_norm[idx]["x"], landmarks_norm[idx]["y"]])

    def p3d(idx: int) -> np.ndarray:
        return np.array([landmarks_world[idx]["x"], landmarks_world[idx]["y"], landmarks_world[idx]["z"]])

    # Keypoint indices
    l_ear, r_ear = 7, 8
    l_sh, r_sh = 11, 12
    l_elb, r_elb = 13, 14
    l_wri, r_wri = 15, 16
    l_hip, r_hip = 23, 24
    l_ank, r_ank = 27, 28

    # 1. Compute Midpoints
    mid_ear_2d = (p2d(l_ear) + p2d(r_ear)) / 2.0
    mid_sh_2d = (p2d(l_sh) + p2d(r_sh)) / 2.0
    mid_hip_2d = (p2d(l_hip) + p2d(r_hip)) / 2.0

    mid_ear_3d = (p3d(l_ear) + p3d(r_ear)) / 2.0
    mid_sh_3d = (p3d(l_sh) + p3d(r_sh)) / 2.0
    mid_hip_3d = (p3d(l_hip) + p3d(r_hip)) / 2.0

    # Determine which side is more visible / facing the camera
    left_vis = (landmarks_norm[l_sh]["visibility"] + landmarks_norm[l_hip]["visibility"]) / 2.0
    right_vis = (landmarks_norm[r_sh]["visibility"] + landmarks_norm[r_hip]["visibility"]) / 2.0
    dominant_side = "left" if left_vis >= right_vis else "right"

    side_ear = l_ear if dominant_side == "left" else r_ear
    side_sh = l_sh if dominant_side == "left" else r_sh
    side_hip = l_hip if dominant_side == "left" else r_hip

    # Spine Vectors (from lower body upwards to head)
    # Trunk: Hip -> Shoulder
    trunk_vector_2d = mid_sh_2d - mid_hip_2d
    trunk_vector_3d = mid_sh_3d - mid_hip_3d

    # Full spine: Hip -> Ear
    spine_vector_2d = mid_ear_2d - mid_hip_2d
    spine_vector_3d = mid_ear_3d - mid_hip_3d

    # Neck: Shoulder -> Ear
    neck_vector_2d = mid_ear_2d - mid_sh_2d

    # Side-specific trunk vector
    side_trunk_vector_2d = p2d(side_sh) - p2d(side_hip)

    # Spine tilt angles vs vertical
    spine_tilt_trunk_deg = calculate_tilt_angle_from_vertical(trunk_vector_2d)
    spine_tilt_overall_deg = calculate_tilt_angle_from_vertical(spine_vector_2d)
    spine_tilt_side_deg = calculate_tilt_angle_from_vertical(side_trunk_vector_2d)
    spine_tilt_3d_deg = calculate_tilt_angle_from_vertical(trunk_vector_3d)

    # Spine alignment: Angle Ear -> Shoulder -> Hip (ideally ~180° for perfectly upright posture)
    spine_alignment_deg = calculate_angle_2d(mid_ear_2d, mid_sh_2d, mid_hip_2d)
    spine_alignment_side_deg = calculate_angle_2d(p2d(side_ear), p2d(side_sh), p2d(side_hip))

    # 2. Elbow Angles (Shoulder -> Elbow -> Wrist)
    left_elbow_2d = calculate_angle_2d(p2d(l_sh), p2d(l_elb), p2d(l_wri))
    right_elbow_2d = calculate_angle_2d(p2d(r_sh), p2d(r_elb), p2d(r_wri))

    left_elbow_3d = calculate_angle_3d(p3d(l_sh), p3d(l_elb), p3d(l_wri))
    right_elbow_3d = calculate_angle_3d(p3d(r_sh), p3d(r_elb), p3d(r_wri))

    # 3. Left Hand Position relative to Navel / Tanden
    # Anatomical reference: Navel is located approximately 15% above mid-hip towards mid-shoulder
    torso_height_norm = float(np.linalg.norm(mid_sh_2d - mid_hip_2d))
    navel_2d = mid_hip_2d + 0.15 * (mid_sh_2d - mid_hip_2d)
    navel_3d = mid_hip_3d + 0.15 * (mid_sh_3d - mid_hip_3d)

    left_wrist_2d = p2d(l_wri)
    left_wrist_3d = p3d(l_wri)

    offset_norm_2d = left_wrist_2d - navel_2d
    dist_norm_2d = float(np.linalg.norm(offset_norm_2d))
    ratio_to_torso = float(dist_norm_2d / max(torso_height_norm, 1e-4))

    offset_px_2d = np.array([offset_norm_2d[0] * img_width, offset_norm_2d[1] * img_height])
    dist_px_2d = float(np.linalg.norm(offset_px_2d))

    offset_world_3d = left_wrist_3d - navel_3d
    dist_world_3d_meters = float(np.linalg.norm(offset_world_3d))

    # 4. Stance Width (Ankle distance)
    ankle_dist_norm = float(np.linalg.norm(p2d(l_ank) - p2d(r_ank)))
    ankle_dist_ratio_to_torso = float(ankle_dist_norm / max(torso_height_norm, 1e-4))

    return {
        "dominant_camera_view_side": dominant_side,
        "spine_posture": {
            "trunk_tilt_angle_deg": round(spine_tilt_trunk_deg, 2),
            "overall_spine_tilt_deg": round(spine_tilt_overall_deg, 2),
            "dominant_side_trunk_tilt_deg": round(spine_tilt_side_deg, 2),
            "world_3d_trunk_tilt_deg": round(spine_tilt_3d_deg, 2),
            "ear_shoulder_hip_alignment_deg": round(spine_alignment_deg, 2),
            "dominant_side_alignment_deg": round(spine_alignment_side_deg, 2),
        },
        "elbow_angles": {
            "left_elbow_deg_2d": round(left_elbow_2d, 2),
            "right_elbow_deg_2d": round(right_elbow_2d, 2),
            "left_elbow_deg_3d": round(left_elbow_3d, 2),
            "right_elbow_deg_3d": round(right_elbow_3d, 2),
        },
        "left_hand_position_relative_to_navel": {
            "offset_normalized": {
                "dx": round(float(offset_norm_2d[0]), 4),
                "dy": round(float(offset_norm_2d[1]), 4),
            },
            "distance_normalized": round(dist_norm_2d, 4),
            "distance_to_torso_ratio": round(ratio_to_torso, 4),
            "offset_pixel": {
                "dx": round(float(offset_px_2d[0]), 1),
                "dy": round(float(offset_px_2d[1]), 1),
            },
            "distance_pixel": round(dist_px_2d, 1),
            "world_3d_offset_meters": {
                "dx": round(float(offset_world_3d[0]), 4),
                "dy": round(float(offset_world_3d[1]), 4),
                "dz": round(float(offset_world_3d[2]), 4),
            },
            "world_3d_distance_meters": round(dist_world_3d_meters, 4),
        },
        "stance": {
            "ankle_distance_normalized": round(ankle_dist_norm, 4),
            "ankle_distance_to_torso_ratio": round(ankle_dist_ratio_to_torso, 4),
        },
    }


def draw_annotated_frame(
    img_bgr: np.ndarray,
    landmarks_norm: List[Dict[str, float]],
    metrics: Dict[str, Any],
    file_name: str,
) -> np.ndarray:
    """Draw skeleton lines, landmarks, and biomechanical telemetry overlay on the image."""
    annotated = img_bgr.copy()
    h, w = annotated.shape[:2]

    # Convert normalized landmarks to pixel coordinates
    pts = []
    for lm in landmarks_norm:
        pts.append((int(lm["x"] * w), int(lm["y"] * h)))

    # Draw connections
    for idx1, idx2 in POSE_CONNECTIONS:
        pt1, pt2 = pts[idx1], pts[idx2]
        cv2.line(annotated, pt1, pt2, (0, 215, 255), 3, cv2.LINE_AA)

    # Draw key landmark points
    for i, pt in enumerate(pts):
        # Highlight wrists, elbows, shoulders, hips in distinctive colors
        if i in (15, 16):  # wrists (cyan)
            cv2.circle(annotated, pt, 8, (255, 255, 0), -1)
            cv2.circle(annotated, pt, 10, (0, 0, 0), 2)
        elif i in (13, 14):  # elbows (green)
            cv2.circle(annotated, pt, 7, (0, 255, 0), -1)
            cv2.circle(annotated, pt, 9, (0, 0, 0), 2)
        elif i in (11, 12, 23, 24):  # shoulders, hips (magenta)
            cv2.circle(annotated, pt, 7, (255, 0, 255), -1)
            cv2.circle(annotated, pt, 9, (0, 0, 0), 2)
        else:
            cv2.circle(annotated, pt, 4, (0, 255, 255), -1)

    # Mark Navel / Tanden (mid-hip + 15% towards mid-shoulder)
    mid_sh = ((pts[11][0] + pts[12][0]) // 2, (pts[11][1] + pts[12][1]) // 2)
    mid_hip = ((pts[23][0] + pts[24][0]) // 2, (pts[23][1] + pts[24][1]) // 2)
    navel_pt = (
        int(mid_hip[0] + 0.15 * (mid_sh[0] - mid_hip[0])),
        int(mid_hip[1] + 0.15 * (mid_sh[1] - mid_hip[1])),
    )
    cv2.circle(annotated, navel_pt, 7, (0, 0, 255), -1)  # Red dot for Tanden
    # Line from left wrist to navel
    cv2.line(annotated, pts[15], navel_pt, (0, 0, 255), 2, cv2.LINE_AA)

    # Draw Semi-transparent HUD overlay
    hud_h = 160
    hud_w = min(480, w - 20)
    overlay = annotated.copy()
    cv2.rectangle(overlay, (10, 10), (10 + hud_w, 10 + hud_h), (20, 20, 20), -1)
    cv2.addWeighted(overlay, 0.75, annotated, 0.25, 0, annotated)
    cv2.rectangle(annotated, (10, 10), (10 + hud_w, 10 + hud_h), (0, 200, 255), 1)

    spine = metrics["spine_posture"]
    elbows = metrics["elbow_angles"]
    l_hand = metrics["left_hand_position_relative_to_navel"]

    lines = [
        f"Kendo Kamae: {file_name[:28]}",
        f"Spine Tilt (Trunk): {spine['trunk_tilt_angle_deg']} deg (Align: {spine['ear_shoulder_hip_alignment_deg']} deg)",
        f"Left Elbow: {elbows['left_elbow_deg_2d']} deg | Right: {elbows['right_elbow_deg_2d']} deg",
        f"Left Hand -> Navel: {l_hand['distance_pixel']} px ({l_hand['world_3d_distance_meters']} m)",
        f"Torso Dist Ratio: {l_hand['distance_to_torso_ratio']}",
    ]

    for i, line in enumerate(lines):
        color = (0, 255, 255) if i == 0 else (255, 255, 255)
        scale = 0.5 if i > 0 else 0.55
        cv2.putText(
            annotated,
            line,
            (20, 35 + i * 26),
            cv2.FONT_HERSHEY_SIMPLEX,
            scale,
            color,
            1,
            cv2.LINE_AA,
        )

    return annotated


def compute_aggregate_statistics(images_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Compute aggregate baseline statistics (mean, std, min, max) across gold standard samples."""
    stats = {}

    def extract_vals(accessor):
        return [accessor(img["metrics"]) for img in images_data if accessor(img["metrics"]) is not None]

    metrics_map = {
        "spine_trunk_tilt_deg": lambda m: m["spine_posture"]["trunk_tilt_angle_deg"],
        "spine_alignment_deg": lambda m: m["spine_posture"]["ear_shoulder_hip_alignment_deg"],
        "left_elbow_angle_deg_2d": lambda m: m["elbow_angles"]["left_elbow_deg_2d"],
        "right_elbow_angle_deg_2d": lambda m: m["elbow_angles"]["right_elbow_deg_2d"],
        "left_elbow_angle_deg_3d": lambda m: m["elbow_angles"]["left_elbow_deg_3d"],
        "right_elbow_angle_deg_3d": lambda m: m["elbow_angles"]["right_elbow_deg_3d"],
        "left_hand_navel_dist_ratio": lambda m: m["left_hand_position_relative_to_navel"]["distance_to_torso_ratio"],
        "left_hand_navel_dist_meters": lambda m: m["left_hand_position_relative_to_navel"]["world_3d_distance_meters"],
        "stance_ankle_dist_ratio": lambda m: m["stance"]["ankle_distance_to_torso_ratio"],
    }

    for key, fn in metrics_map.items():
        vals = extract_vals(fn)
        if vals:
            arr = np.array(vals)
            stats[key] = {
                "mean": round(float(np.mean(arr)), 2),
                "std": round(float(np.std(arr)), 2),
                "min": round(float(np.min(arr)), 2),
                "max": round(float(np.max(arr)), 2),
                "sample_count": len(vals),
            }

    return stats


def main() -> None:
    print("=" * 70)
    print("Open-Kendo: Extracting Kamae Gold Standard Keypoints & Biomechanics")
    print("=" * 70)

    # 1. Ensure Model
    model_path = ensure_model_exists()

    # 2. Setup MediaPipe Pose Landmarker
    base_options = python.BaseOptions(model_asset_path=str(model_path))
    options = vision.PoseLandmarkerOptions(
        base_options=base_options,
        output_segmentation_masks=False,
        min_pose_detection_confidence=0.4,
        min_pose_presence_confidence=0.4,
    )
    detector = vision.PoseLandmarker.create_from_options(options)

    # 3. Locate Input Images
    raw_kamae_dir = PROJECT_ROOT / "data" / "raw" / "kamae"
    output_json_path = PROJECT_ROOT / "data" / "gold_standards" / "kamae_baseline.json"
    output_viz_dir = PROJECT_ROOT / "data" / "gold_standards" / "kamae"

    output_json_path.parent.mkdir(parents=True, exist_ok=True)
    output_viz_dir.mkdir(parents=True, exist_ok=True)

    image_files = sorted(
        [
            p
            for p in raw_kamae_dir.glob("*.*")
            if p.suffix.lower() in [".jpg", ".jpeg", ".png"]
        ]
    )

    if not image_files:
        print(f"Error: No image files found in {raw_kamae_dir}")
        sys.exit(1)

    print(f"Found {len(image_files)} Kamae reference images in {raw_kamae_dir.relative_to(PROJECT_ROOT)}:")
    for img_p in image_files:
        print(f"  - {img_p.name}")

    results_data = []

    # 4. Process Each Image
    for img_path in image_files:
        print(f"\nProcessing {img_path.name}...")
        mp_image = mp.Image.create_from_file(str(img_path))
        detection_result = detector.detect(mp_image)

        if not detection_result.pose_landmarks:
            print(f"  [WARNING] No pose detected in {img_path.name}!")
            continue

        raw_landmarks = detection_result.pose_landmarks[0]
        world_landmarks = detection_result.pose_world_landmarks[0]

        # Extract 33 normalized landmarks
        landmarks_norm_list = []
        for i, lm in enumerate(raw_landmarks):
            landmarks_norm_list.append({
                "index": i,
                "name": LANDMARK_NAMES[i] if i < len(LANDMARK_NAMES) else f"LANDMARK_{i}",
                "x": float(lm.x),
                "y": float(lm.y),
                "z": float(lm.z),
                "visibility": float(lm.visibility) if lm.visibility is not None else 0.0,
                "presence": float(lm.presence) if lm.presence is not None else 0.0,
            })

        # Extract 33 real-world 3D landmarks (in meters)
        landmarks_world_list = []
        for i, wlm in enumerate(world_landmarks):
            landmarks_world_list.append({
                "index": i,
                "name": LANDMARK_NAMES[i] if i < len(LANDMARK_NAMES) else f"LANDMARK_{i}",
                "x": float(wlm.x),
                "y": float(wlm.y),
                "z": float(wlm.z),
                "visibility": float(wlm.visibility) if wlm.visibility is not None else 0.0,
            })

        # Calculate Biomechanical Metrics
        metrics = compute_kamae_metrics(
            landmarks_norm=landmarks_norm_list,
            landmarks_world=landmarks_world_list,
            img_width=mp_image.width,
            img_height=mp_image.height,
        )

        # Print summary
        spine = metrics["spine_posture"]
        elbows = metrics["elbow_angles"]
        l_hand = metrics["left_hand_position_relative_to_navel"]
        print(f"  Spine Trunk Tilt Angle : {spine['trunk_tilt_angle_deg']} deg (Ear-Shoulder-Hip align: {spine['ear_shoulder_hip_alignment_deg']} deg)")
        print(f"  Left Elbow Angle       : {elbows['left_elbow_deg_2d']} deg (3D: {elbows['left_elbow_deg_3d']} deg)")
        print(f"  Right Elbow Angle      : {elbows['right_elbow_deg_2d']} deg (3D: {elbows['right_elbow_deg_3d']} deg)")
        print(f"  Left Hand to Navel     : {l_hand['distance_pixel']} px, ratio to torso={l_hand['distance_to_torso_ratio']} (3D: {l_hand['world_3d_distance_meters']}m)")

        # Render and save visual diagnostic
        img_bgr = cv2.imread(str(img_path))
        annotated_bgr = draw_annotated_frame(img_bgr, landmarks_norm_list, metrics, img_path.name)
        viz_path = output_viz_dir / f"annotated_{img_path.stem}.jpg"
        cv2.imwrite(str(viz_path), annotated_bgr)
        print(f"  Saved visual annotation -> {viz_path.relative_to(PROJECT_ROOT)}")

        results_data.append({
            "file_name": img_path.name,
            "dimensions": {"width": mp_image.width, "height": mp_image.height},
            "metrics": metrics,
            "landmarks_normalized": landmarks_norm_list,
            "landmarks_world_meters": landmarks_world_list,
        })

    # 5. Compute Aggregate Gold Standard Benchmarks
    aggregate_stats = compute_aggregate_statistics(results_data)

    output_payload = {
        "metadata": {
            "title": "Open-Kendo Chudan-no-Kamae Gold Standard Baseline",
            "extracted_at": datetime.now(timezone.utc).isoformat(),
            "model": "MediaPipe Pose Landmarker (Heavy float16)",
            "total_images_processed": len(results_data),
            "reference_sources": [
                "Kendo World / All Japan Kendo Federation (AJKF) Standards",
                "Kendo Jidai (Koda Sensei, Eiga Sensei, Hojo Sensei, Okido Sensei)",
                "The Kendo Show (Andy Fisher Sensei Chudan Tutorial)",
            ],
            "definitions": {
                "trunk_tilt_angle_deg": "Angle of Hip-to-Shoulder vector relative to vertical upwards line (0 deg is perfectly upright).",
                "ear_shoulder_hip_alignment_deg": "Interior angle formed by Ear -> Shoulder -> Hip (180 deg is a completely straight upper posture).",
                "elbow_angle_deg": "Interior joint angle Shoulder -> Elbow -> Wrist.",
                "left_hand_navel_dist_ratio": "Euclidean distance between left wrist and navel normalized by torso length (mid-hip to mid-shoulder).",
            },
        },
        "aggregate_gold_standard": aggregate_stats,
        "images": results_data,
    }

    # 6. Save JSON
    with open(output_json_path, "w", encoding="utf-8") as f:
        json.dump(output_payload, f, indent=2)

    print("\n" + "=" * 70)
    print(f"SUCCESS: Saved baseline dataset to: {output_json_path.relative_to(PROJECT_ROOT)}")
    print(f"Total processed samples: {len(results_data)}")
    print("Aggregate Statistics Summary:")
    for k, v in aggregate_stats.items():
        print(f"  {k:30s}: mean={v['mean']} | std={v['std']} | range=[{v['min']}, {v['max']}]")
    print("=" * 70)


if __name__ == "__main__":
    main()
