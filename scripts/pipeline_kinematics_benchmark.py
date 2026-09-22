#!/usr/bin/env python3
"""Open-Kendo 3-in-1 Kinematics Extraction, Signal Plotting & Ki-Ken-Tai Benchmark.

Executes all 3 planned phases in one unified, dependency-light script:
  Step 1: Extract Pose timeseries (wrists, elbows, ankles) using MediaPipe Pose.
  Step 2: Render kinematic signal curves + Ground Truth pins with OpenCV (no matplotlib dependency).
  Step 3: Run automated Ki-Ken-Tai-Ichi detection & benchmark MAE against manual ground truth.

Outputs:
  - data/gold_standards/strike_trajectories.json
  - data/outputs/kinematics_{clip_stem}.png
  - data/gold_standards/benchmark_results.json
"""

import json
import math
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import cv2
import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parent.parent

# MediaPipe Task API
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

MODEL_PATH = PROJECT_ROOT / "models" / "pose_landmarker_heavy.task"


def smooth_signal(arr: List[float], window_size: int = 3) -> np.ndarray:
    """Moving average filter for signal smoothing."""
    a = np.array(arr, dtype=float)
    if len(a) < window_size:
        return a
    window = np.ones(window_size) / window_size
    return np.convolve(a, window, mode="same")


def extract_video_trajectories(video_path: Path, detector: vision.PoseLandmarker) -> Tuple[List[Dict[str, Any]], float, int]:
    """Extract per-frame pose landmarks and kinematic coordinates."""
    cap = cv2.VideoCapture(str(video_path))
    fps = float(cap.get(cv2.CAP_PROP_FPS))
    if fps <= 0:
        fps = 30.0
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    frames_data = []
    frame_idx = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Convert to RGB MediaPipe Image
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_img = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame_rgb)
        res = detector.detect(mp_img)

        entry = {"frame_idx": frame_idx, "timestamp_ms": round((frame_idx / fps) * 1000.0, 2)}

        if res.pose_landmarks and len(res.pose_landmarks[0]) >= 33:
            lm = res.pose_landmarks[0]
            # Key indices: 15=L_wrist, 16=R_wrist, 13=L_elbow, 14=R_elbow, 11=L_sh, 12=R_sh, 27=L_ankle, 28=R_ankle
            entry["wrist_mid_y"] = float((lm[15].y + lm[16].y) / 2.0)
            entry["wrist_mid_x"] = float((lm[15].x + lm[16].x) / 2.0)
            entry["right_ankle_y"] = float(lm[28].y)
            entry["left_ankle_y"] = float(lm[27].y)
            entry["right_wrist_y"] = float(lm[16].y)
            entry["left_wrist_y"] = float(lm[15].y)
            entry["right_elbow_y"] = float(lm[14].y)
            entry["detected"] = True
        else:
            entry["detected"] = False

        frames_data.append(entry)
        frame_idx += 1

    cap.release()
    return frames_data, fps, total_frames


def draw_kinematics_plot(
    frames_data: List[Dict[str, Any]],
    repetitions: List[Dict[str, Any]],
    fps: float,
    output_path: Path,
    title: str,
):
    """Draw signal curves & ground truth event pins directly onto an OpenCV canvas."""
    width, height = 1200, 500
    canvas = np.full((height, width, 3), 25, dtype=np.uint8)

    n_frames = len(frames_data)
    if n_frames < 2:
        return

    # Extract signals
    wrist_y = [f.get("wrist_mid_y", 0.5) for f in frames_data]
    ankle_y = [f.get("right_ankle_y", 0.8) for f in frames_data]

    # Smooth
    wrist_smooth = smooth_signal(wrist_y, 3)
    # Wrist velocity: negative derivative of y (since y=0 is top, moving up is -dy, moving down is +dy)
    wrist_vel = np.gradient(wrist_smooth) * fps

    # Normalization helper to map values to pixel height [margin_top, margin_bottom]
    plot_top, plot_bottom = 70, height - 60
    plot_h = plot_bottom - plot_top
    plot_left, plot_right = 70, width - 40
    plot_w = plot_right - plot_left

    def x_to_px(f_idx: int) -> int:
        return int(plot_left + (f_idx / max(1, n_frames - 1)) * plot_w)

    def y_to_px(val: float, v_min: float, v_max: float) -> int:
        norm = (val - v_min) / max(1e-5, (v_max - v_min))
        # invert so higher value is higher on plot
        return int(plot_bottom - norm * plot_h)

    # Invert wrist height so raising sword goes UP on chart
    inv_wrist = 1.0 - wrist_smooth
    w_min, w_max = float(np.min(inv_wrist)), float(np.max(inv_wrist))

    # Draw grid lines
    for i in range(5):
        y_grid = int(plot_top + i * (plot_h / 4))
        cv2.line(canvas, (plot_left, y_grid), (plot_right, y_grid), (45, 45, 45), 1)

    # Draw Wrist Height Curve (Cyan)
    for i in range(n_frames - 1):
        pt1 = (x_to_px(i), y_to_px(inv_wrist[i], w_min, w_max))
        pt2 = (x_to_px(i + 1), y_to_px(inv_wrist[i + 1], w_min, w_max))
        cv2.line(canvas, pt1, pt2, (255, 200, 0), 2, cv2.LINE_AA)

    # Draw Wrist Velocity Curve (Purple/Magenta)
    v_min, v_max = float(np.min(wrist_vel)), float(np.max(wrist_vel))
    for i in range(n_frames - 1):
        pt1 = (x_to_px(i), y_to_px(wrist_vel[i], v_min, v_max))
        pt2 = (x_to_px(i + 1), y_to_px(wrist_vel[i + 1], v_min, v_max))
        cv2.line(canvas, pt1, pt2, (200, 50, 255), 1, cv2.LINE_AA)

    # Draw Ground Truth Event Vertical Lines
    colors = {
        "furikaburi_start": (0, 255, 128),  # Green
        "apex_top": (0, 230, 255),          # Yellow
        "fumikomi_landing": (255, 180, 0),  # Sky Blue
        "blade_impact": (0, 0, 255),        # Red
        "zanshin_complete": (255, 0, 255),  # Purple
    }

    for rep in repetitions:
        evs = rep.get("events", [])
        ev_dict = {e["event_id"]: e["frame_index"] for e in evs} if isinstance(evs, list) else evs
        rep_id = rep.get("rep_id", 1)

        # Rep boundary highlight
        apex_f = ev_dict.get("apex_top")
        impact_f = ev_dict.get("blade_impact")
        fumi_f = ev_dict.get("fumikomi_landing")

        if apex_f is not None:
            px = x_to_px(apex_f)
            cv2.line(canvas, (px, plot_top), (px, plot_bottom), colors["apex_top"], 2, cv2.LINE_AA)
            cv2.putText(canvas, f"R{rep_id}:Apex", (px - 15, plot_top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.38, colors["apex_top"], 1)

        if fumi_f is not None:
            px = x_to_px(fumi_f)
            cv2.line(canvas, (px, plot_top), (px, plot_bottom), colors["fumikomi_landing"], 2, cv2.LINE_AA)
            cv2.putText(canvas, "Fumi", (px - 10, plot_bottom + 18), cv2.FONT_HERSHEY_SIMPLEX, 0.38, colors["fumikomi_landing"], 1)

        if impact_f is not None:
            px = x_to_px(impact_f)
            cv2.line(canvas, (px, plot_top), (px, plot_bottom), colors["blade_impact"], 2, cv2.LINE_AA)
            cv2.putText(canvas, f"Impact", (px - 15, plot_top - 24), cv2.FONT_HERSHEY_SIMPLEX, 0.38, colors["blade_impact"], 1)

    # Title & Legend
    cv2.putText(canvas, f"Kinematic Curves & GT Events: {title}", (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 230, 255), 1, cv2.LINE_AA)
    # Legend
    cv2.circle(canvas, (plot_right - 340, 25), 5, (255, 200, 0), -1)
    cv2.putText(canvas, "Wrist Height", (plot_right - 330, 29), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (220, 220, 220), 1)
    cv2.circle(canvas, (plot_right - 230, 25), 5, (200, 50, 255), -1)
    cv2.putText(canvas, "Velocity", (plot_right - 220, 29), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (220, 220, 220), 1)
    cv2.circle(canvas, (plot_right - 140, 25), 5, (0, 0, 255), -1)
    cv2.putText(canvas, "GT Impact", (plot_right - 130, 29), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (220, 220, 220), 1)

    cv2.imwrite(str(output_path), canvas)


def detect_strike_events(
    frames_data: List[Dict[str, Any]],
    fps: float,
    search_window: Tuple[int, int],
) -> Dict[str, Optional[int]]:
    """Detect Apex, Impact, and Fumikomi within a candidate repetition window."""
    w_start, w_end = search_window
    window_frames = [f for f in frames_data if w_start <= f["frame_idx"] <= w_end]
    if len(window_frames) < 3:
        return {"apex": None, "impact": None, "fumikomi": None}

    # 1. Apex Detection: highest point of wrist (minimum y)
    wrist_y = [f.get("wrist_mid_y", 1.0) for f in window_frames]
    smooth_y = smooth_signal(wrist_y, 3)
    apex_local_idx = int(np.argmin(smooth_y))
    apex_frame = window_frames[apex_local_idx]["frame_idx"]

    # 2. Impact / Tenouchi Detection: sharp deceleration / bottom of swing after apex
    post_apex_frames = [f for f in window_frames if f["frame_idx"] >= apex_frame]
    if len(post_apex_frames) >= 2:
        post_y = [f.get("wrist_mid_y", 0.0) for f in post_apex_frames]
        smooth_post = smooth_signal(post_y, 3)
        # Lowest point on screen = maximum y value
        impact_local_idx = int(np.argmax(smooth_post))
        impact_frame = post_apex_frames[impact_local_idx]["frame_idx"]
    else:
        impact_frame = apex_frame

    # 3. Fumikomi Detection: right ankle vertical landing (max deceleration of ankle_y)
    ankle_y = [f.get("right_ankle_y", 0.0) for f in window_frames]
    smooth_ankle = smooth_signal(ankle_y, 3)
    ankle_vel = np.gradient(smooth_ankle)
    # Peak landing is zero crossing / deceleration after downward motion
    fumi_local_idx = int(np.argmax(ankle_vel)) if len(ankle_vel) > 0 else 0
    fumikomi_frame = window_frames[fumi_local_idx]["frame_idx"]

    return {
        "apex": apex_frame,
        "impact": impact_frame,
        "fumikomi": fumikomi_frame,
    }


def main():
    print("=" * 75)
    print("Open-Kendo: Kinematics Extraction, Plotting & Ki-Ken-Tai Benchmark")
    print("=" * 75)

    # 1. Setup MediaPipe Detector
    base_options = python.BaseOptions(model_asset_path=str(MODEL_PATH))
    options = vision.PoseLandmarkerOptions(
        base_options=base_options,
        output_segmentation_masks=False,
        min_pose_detection_confidence=0.35,
    )
    detector = vision.PoseLandmarker.create_from_options(options)

    ann_dir = PROJECT_ROOT / "data" / "annotations"
    seg_dir = PROJECT_ROOT / "data" / "segments"
    out_gold_dir = PROJECT_ROOT / "data" / "gold_standards"
    out_viz_dir = PROJECT_ROOT / "data" / "outputs"

    out_gold_dir.mkdir(parents=True, exist_ok=True)
    out_viz_dir.mkdir(parents=True, exist_ok=True)

    ann_files = sorted(ann_dir.glob("*_events.json"))
    if not ann_files:
        print(f"Error: No annotation files found in {ann_dir}")
        sys.exit(1)

    all_trajectories = {}
    benchmark_evals = []

    print(f"Processing {len(ann_files)} annotated video clips...\n")

    for ann_p in ann_files:
        clip_name = ann_p.stem.replace("_events", "") + ".mp4"
        video_p = seg_dir / clip_name

        if not video_p.exists():
            print(f"  [SKIP] Video not found: {video_p.name}")
            continue

        with open(ann_p, "r", encoding="utf-8") as f:
            ann_data = json.load(f)

        repetitions = ann_data.get("repetitions", [])
        if not repetitions and "annotated_events" in ann_data:
            repetitions = [{"rep_id": 1, "events": ann_data["annotated_events"]}]

        print(f"Extracting: {video_p.name} ({len(repetitions)} annotated reps)...")
        frames_data, fps, total_frames = extract_video_trajectories(video_p, detector)

        all_trajectories[video_p.name] = {
            "fps": fps,
            "total_frames": total_frames,
            "frames": frames_data,
        }

        # Step 2: Render Kinematic Signal Curves + GT Overlay
        plot_path = out_viz_dir / f"kinematics_{video_p.stem}.png"
        draw_kinematics_plot(frames_data, repetitions, fps, plot_path, video_p.name)
        print(f"  -> Saved kinematic plot: {plot_path.name}")

        # Step 3: Run Event Detection & Benchmark vs GT
        for rep in repetitions:
            evs = rep.get("events", [])
            ev_dict = {e["event_id"]: e["frame_index"] for e in evs} if isinstance(evs, list) else evs
            if not ev_dict:
                continue

            gt_furi = ev_dict.get("furikaburi_start", 0)
            gt_apex = ev_dict.get("apex_top")
            gt_fumi = ev_dict.get("fumikomi_landing")
            gt_impact = ev_dict.get("blade_impact")
            gt_zanshin = ev_dict.get("zanshin_complete", total_frames - 1)

            # Search window for this repetition
            search_start = max(0, gt_furi - 5)
            search_end = min(total_frames - 1, gt_zanshin + 10)

            pred = detect_strike_events(frames_data, fps, (search_start, search_end))

            eval_entry = {
                "video": video_p.name,
                "rep_id": rep.get("rep_id", 1),
                "fps": fps,
            }

            if gt_apex is not None and pred["apex"] is not None:
                err_frames = pred["apex"] - gt_apex
                err_ms = (err_frames / fps) * 1000.0
                eval_entry["apex"] = {"gt": gt_apex, "pred": pred["apex"], "err_ms": round(err_ms, 1)}

            if gt_impact is not None and pred["impact"] is not None:
                err_frames = pred["impact"] - gt_impact
                err_ms = (err_frames / fps) * 1000.0
                eval_entry["impact"] = {"gt": gt_impact, "pred": pred["impact"], "err_ms": round(err_ms, 1)}

            if gt_fumi is not None and pred["fumikomi"] is not None:
                err_frames = pred["fumikomi"] - gt_fumi
                err_ms = (err_frames / fps) * 1000.0
                eval_entry["fumikomi"] = {"gt": gt_fumi, "pred": pred["fumikomi"], "err_ms": round(err_ms, 1)}

            benchmark_evals.append(eval_entry)

    # Save Trajectories
    traj_path = out_gold_dir / "strike_trajectories.json"
    with open(traj_path, "w", encoding="utf-8") as f:
        json.dump(all_trajectories, f, indent=2)
    print(f"\n[STEP 1 SUCCESS] Saved full pose trajectories -> {traj_path.relative_to(PROJECT_ROOT)}")

    # Compute Benchmark Metrics (MAE)
    apex_errors = [abs(e["apex"]["err_ms"]) for e in benchmark_evals if "apex" in e]
    impact_errors = [abs(e["impact"]["err_ms"]) for e in benchmark_evals if "impact" in e]
    fumi_errors = [abs(e["fumikomi"]["err_ms"]) for e in benchmark_evals if "fumikomi" in e]

    benchmark_summary = {
        "metadata": {
            "title": "Open-Kendo Ki-Ken-Tai-Ichi Benchmark Evaluation",
            "evaluated_at": datetime.now(timezone.utc).isoformat(),
            "total_evaluated_reps": len(benchmark_evals),
        },
        "metrics_mae_ms": {
            "apex_mae_ms": round(float(np.mean(apex_errors)), 2) if apex_errors else 0.0,
            "impact_mae_ms": round(float(np.mean(impact_errors)), 2) if impact_errors else 0.0,
            "fumikomi_mae_ms": round(float(np.mean(fumi_errors)), 2) if fumi_errors else 0.0,
        },
        "detailed_repetition_results": benchmark_evals,
    }

    bench_path = out_gold_dir / "benchmark_results.json"
    with open(bench_path, "w", encoding="utf-8") as f:
        json.dump(benchmark_summary, f, indent=2)

    # Print Report
    print("=" * 75)
    print("BENCHMARK RESULTS (Automated AI Detection vs Ground Truth):")
    print(f"  Total Strike Repetitions Evaluated : {len(benchmark_evals)}")
    print(f"  Apex Timing MAE                    : {benchmark_summary['metrics_mae_ms']['apex_mae_ms']} ms")
    print(f"  Blade Impact / Tenouchi MAE        : {benchmark_summary['metrics_mae_ms']['impact_mae_ms']} ms")
    print(f"  Fumikomi Landing MAE               : {benchmark_summary['metrics_mae_ms']['fumikomi_mae_ms']} ms")
    print("=" * 75)
    print(f"Results saved to: {bench_path.relative_to(PROJECT_ROOT)}")


if __name__ == "__main__":
    main()
