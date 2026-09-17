#!/usr/bin/env python3
"""Visualize Skeleton / Keypoints from kamae_baseline.json onto Raw Kamae Images.

Reads:
  - data/gold_standards/kamae_baseline.json (normalized coordinates x, y)
  - data/raw/kamae/ (source images)
Calculates:
  - Pixel coordinates (x * image_width, y * image_height)
Renders:
  - Anatomical skeleton connections (bones) with dynamic thickness tailored to image resolution.
  - Joint keypoints with high-contrast outlines.
  - Tanden (navel) landmark and left-hand Kamae alignment vector.
Saves to:
  - data/gold_standards/kamae/
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Tuple

import cv2
import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parent.parent

# MediaPipe Pose connections grouped by anatomical body part
BODY_CONNECTIONS = {
    "torso": [
        (11, 12),  # Left shoulder to right shoulder
        (11, 23),  # Left shoulder to left hip
        (12, 24),  # Right shoulder to right hip
        (23, 24),  # Left hip to right hip
    ],
    "left_arm": [
        (11, 13),  # Left shoulder to left elbow
        (13, 15),  # Left elbow to left wrist
        (15, 17), (15, 19), (15, 21), (17, 19),  # Left hand fingers
    ],
    "right_arm": [
        (12, 14),  # Right shoulder to right elbow
        (14, 16),  # Right elbow to right wrist
        (16, 18), (16, 20), (16, 22), (18, 20),  # Right hand fingers
    ],
    "left_leg": [
        (23, 25),  # Left hip to left knee
        (25, 27),  # Left knee to left ankle
        (27, 29), (29, 31), (27, 31),  # Left foot
    ],
    "right_leg": [
        (24, 26),  # Right hip to right knee
        (26, 28),  # Right knee to right ankle
        (28, 30), (30, 32), (28, 32),  # Right foot
    ],
    "head": [
        (0, 1), (1, 2), (2, 3), (3, 7),  # Left eye/ear
        (0, 4), (4, 5), (5, 6), (6, 8),  # Right eye/ear
        (9, 10),  # Mouth
        (7, 11), (8, 12),  # Ears to shoulders
    ],
}

# Color palette in BGR
COLORS = {
    "torso": (0, 230, 255),       # Vibrant Gold / Yellow
    "left_arm": (255, 200, 0),     # Cyan / Sky Blue
    "right_arm": (0, 140, 255),    # Vibrant Orange
    "left_leg": (230, 120, 0),     # Deep Sky Blue
    "right_leg": (0, 100, 230),    # Red-Orange
    "head": (200, 220, 240),       # Off-white / Ice Blue
    "joint_fill": (255, 255, 255), # White fill
    "joint_outline": (20, 20, 20), # Dark outline
    "navel": (0, 0, 255),          # Red for Tanden / Navel
    "navel_line": (0, 80, 255),    # Red-orange connecting line
}


def draw_skeleton(img_bgr: np.ndarray, landmarks_norm: List[Dict], metrics: Dict) -> np.ndarray:
    """Draw full skeleton and keypoints with resolution-adaptive scaling."""
    annotated = img_bgr.copy()
    h, w = annotated.shape[:2]

    # Adaptive scale based on image dimensions
    scale_factor = max(1.0, min(w, h) / 800.0)
    line_thickness = max(2, int(round(3.0 * scale_factor)))
    joint_radius = max(3, int(round(5.0 * scale_factor)))
    outline_thickness = max(1, int(round(1.5 * scale_factor)))

    # Compute pixel coordinates from landmarks_normalized (x * w, y * h)
    pts: Dict[int, Tuple[int, int]] = {}
    visibilities: Dict[int, float] = {}

    for lm in landmarks_norm:
        idx = lm["index"]
        px = int(round(lm["x"] * w))
        py = int(round(lm["y"] * h))
        pts[idx] = (px, py)
        visibilities[idx] = lm.get("visibility", 1.0)

    # 1. Draw Bones / Connections
    for category, connection_pairs in BODY_CONNECTIONS.items():
        color = COLORS.get(category, (0, 255, 0))
        for idx1, idx2 in connection_pairs:
            if idx1 in pts and idx2 in pts:
                # Skip if visibility is extremely low (< 0.2)
                if visibilities.get(idx1, 1.0) < 0.2 and visibilities.get(idx2, 1.0) < 0.2:
                    continue
                pt1 = pts[idx1]
                pt2 = pts[idx2]
                cv2.line(annotated, pt1, pt2, color, line_thickness, cv2.LINE_AA)

    # 2. Draw Joints / Keypoints
    for idx, pt in pts.items():
        if visibilities.get(idx, 1.0) < 0.25:
            continue

        # Color specific critical joints differently
        if idx in (15, 16):  # Wrists (hands on Tsuka)
            r = int(joint_radius * 1.5)
            c = (255, 255, 0) if idx == 15 else (0, 165, 255)
        elif idx in (13, 14):  # Elbows
            r = int(joint_radius * 1.3)
            c = (0, 255, 128)
        elif idx in (11, 12, 23, 24):  # Shoulders and hips
            r = int(joint_radius * 1.3)
            c = (255, 0, 255)
        elif idx in (25, 26, 27, 28):  # Knees, ankles
            r = int(joint_radius * 1.2)
            c = (0, 220, 255)
        else:
            r = joint_radius
            c = COLORS["joint_fill"]

        cv2.circle(annotated, pt, r + outline_thickness, COLORS["joint_outline"], -1, cv2.LINE_AA)
        cv2.circle(annotated, pt, r, c, -1, cv2.LINE_AA)

    # 3. Draw Tanden (Navel) and Kamae Hand Alignment
    if 11 in pts and 12 in pts and 23 in pts and 24 in pts and 15 in pts:
        mid_sh_x = (pts[11][0] + pts[12][0]) / 2.0
        mid_sh_y = (pts[11][1] + pts[12][1]) / 2.0
        mid_hip_x = (pts[23][0] + pts[24][0]) / 2.0
        mid_hip_y = (pts[23][1] + pts[24][1]) / 2.0

        # Navel: ~15% from hip center towards shoulder center
        navel_x = int(round(mid_hip_x + 0.15 * (mid_sh_x - mid_hip_x)))
        navel_y = int(round(mid_hip_y + 0.15 * (mid_sh_y - mid_hip_y)))
        navel_pt = (navel_x, navel_y)

        # Draw alignment line between left wrist and navel
        cv2.line(annotated, pts[15], navel_pt, COLORS["navel_line"], max(2, int(2 * scale_factor)), cv2.LINE_AA)

        # Draw Navel marker
        cv2.circle(annotated, navel_pt, int(joint_radius * 1.4) + outline_thickness, (0, 0, 0), -1, cv2.LINE_AA)
        cv2.circle(annotated, navel_pt, int(joint_radius * 1.4), COLORS["navel"], -1, cv2.LINE_AA)

    # 4. Draw Informative HUD Banner (Adaptive Placement)
    # Determine pose bounding box horizontally
    pose_xs = [pt[0] for pt in pts.values()]
    pose_min_x = min(pose_xs) if pose_xs else w // 2
    pose_max_x = max(pose_xs) if pose_xs else w // 2

    # If there is enough space on the top-left, place it there; otherwise place at bottom-left or top-right
    base_hud_w = int(min(450 * scale_factor, w * 0.48))
    hud_h = int(125 * scale_factor)

    if pose_min_x > base_hud_w + 20:
        hud_x, hud_y = 10, 10
        hud_w = min(base_hud_w, pose_min_x - 15)
    elif w - pose_max_x > base_hud_w + 20:
        hud_x = w - base_hud_w - 10
        hud_y = 10
        hud_w = base_hud_w
    else:
        # Place at bottom corner
        hud_x = 10
        hud_y = max(10, h - hud_h - 15)
        hud_w = min(base_hud_w, int(w * 0.45))

    overlay = annotated.copy()
    cv2.rectangle(overlay, (hud_x, hud_y), (hud_x + hud_w, hud_y + hud_h), (15, 15, 15), -1)
    cv2.addWeighted(overlay, 0.78, annotated, 0.22, 0, annotated)
    cv2.rectangle(annotated, (hud_x, hud_y), (hud_x + hud_w, hud_y + hud_h), (0, 215, 255), max(1, int(scale_factor)))

    spine = metrics.get("spine_posture", {})
    elbows = metrics.get("elbow_angles", {})
    l_hand = metrics.get("left_hand_position_relative_to_navel", {})

    lines = [
        f"Kamae Standard [{w}x{h}]",
        f"Spine: {spine.get('trunk_tilt_angle_deg', 0.0)} deg | Align: {spine.get('ear_shoulder_hip_alignment_deg', 0.0)} deg",
        f"Elbows: L {elbows.get('left_elbow_deg_2d', 0.0)} deg | R {elbows.get('right_elbow_deg_2d', 0.0)} deg",
        f"Hand->Navel: {l_hand.get('distance_pixel', 0.0)}px ({l_hand.get('world_3d_distance_meters', 0.0)}m)",
    ]

    font_scale = max(0.32, 0.38 * scale_factor)
    line_spacing = int(26 * scale_factor)
    for i, line in enumerate(lines):
        color = (0, 230, 255) if i == 0 else (255, 255, 255)
        text_y = int(hud_y + 24 * scale_factor + i * line_spacing)
        cv2.putText(
            annotated,
            line,
            (int(hud_x + 12 * scale_factor), text_y),
            cv2.FONT_HERSHEY_SIMPLEX,
            font_scale,
            color,
            max(1, int(round(scale_factor))),
            cv2.LINE_AA,
        )

    return annotated


def main():
    json_path = PROJECT_ROOT / "data" / "gold_standards" / "kamae_baseline.json"
    raw_dir = PROJECT_ROOT / "data" / "raw" / "kamae"
    out_dir = PROJECT_ROOT / "data" / "gold_standards" / "kamae"

    out_dir.mkdir(parents=True, exist_ok=True)

    if not json_path.exists():
        print(f"Error: {json_path} not found. Please run scripts/extract_kamae_gold_standard.py first.")
        sys.exit(1)

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    images_data = data.get("images", [])
    print(f"Loaded {len(images_data)} baseline image entries from {json_path.name}")
    print(f"Rendering annotated skeletons into: {out_dir.relative_to(PROJECT_ROOT)}/\n")

    for entry in images_data:
        file_name = entry["file_name"]
        raw_img_path = raw_dir / file_name

        if not raw_img_path.exists():
            print(f"  [WARNING] Raw image not found: {raw_img_path}")
            continue

        img_bgr = cv2.imread(str(raw_img_path))
        if img_bgr is None:
            print(f"  [ERROR] Failed to read {raw_img_path}")
            continue

        landmarks_norm = entry["landmarks_normalized"]
        metrics = entry["metrics"]

        # Render skeleton on image
        annotated_img = draw_skeleton(img_bgr, landmarks_norm, metrics)

        # Save to data/gold_standards/kamae/
        out_file_path = out_dir / file_name
        cv2.imwrite(str(out_file_path), annotated_img)
        print(f"  -> Saved: {out_file_path.relative_to(PROJECT_ROOT)} ({img_bgr.shape[1]}x{img_bgr.shape[0]})")

    print("\n" + "=" * 60)
    print(f"Visualization complete! Files saved in: {out_dir.relative_to(PROJECT_ROOT)}")
    print("=" * 60)


if __name__ == "__main__":
    main()
