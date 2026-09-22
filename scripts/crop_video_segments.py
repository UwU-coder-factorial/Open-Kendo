#!/usr/bin/env python3
"""Video Slicing Utility for Open-Kendo Benchmark Dataset.

Cuts long raw reference videos into short, focused clips based on annotated timestamps.
Supports both FFmpeg (high-speed frame-accurate H.264 encode) and OpenCV VideoWriter fallback.

Catalog of target segments:
1. data/raw/mokkei_kihon01_kamae_suburi.mp4:
   - 4:09 - 4:26 (shomen, frontview)
   - 7:28 - 7:31 (sideview)
2. data/raw/mokkei_part1_men_uchi_60fps.mp4:
   - 0:05 - 0:14 (men-uchi, sideview, right-to-left)
   - 0:16 - 0:25 (sideview, left-to-right)
   - 4:39 - 4:45 (frontview, occluded by defender)
   - 4:45 - 4:50 (backview)
3. data/raw/sample2_kendo_basics_shomen_uchi.mp4:
   - 0:42 - 0:49 (frontview ~45 deg)
   - 1:55 - 2:00 (sideview)

Outputs clips to data/segments/ and updates data/segments/segments_catalog.json.
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import cv2

PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Slicing Catalog Specifications
SEGMENT_CATALOG = [
    # --------------------------------------------------------------------------
    # 1. mokkei_kihon01_kamae_suburi.mp4
    # --------------------------------------------------------------------------
    {
        "source_video": "mokkei_kihon01_kamae_suburi.mp4",
        "output_filename": "mokkei_kihon01_04m09s_04m26s_shomen_frontview.mp4",
        "start_time": "04:09",
        "end_time": "04:26",
        "technique": "shomen_suburi",
        "view_angle": "frontview",
        "description": "Shomen-uchi Suburi repetitions viewed from direct front perspective.",
        "tags": ["suburi", "frontview", "shomen"],
    },
    {
        "source_video": "mokkei_kihon01_kamae_suburi.mp4",
        "output_filename": "mokkei_kihon01_07m28s_07m31s_suburi_sideview.mp4",
        "start_time": "07:28",
        "end_time": "07:31",
        "technique": "suburi",
        "view_angle": "sideview",
        "description": "Suburi arm extension and stance alignment viewed from the lateral/side angle.",
        "tags": ["suburi", "sideview", "lateral"],
    },
    # --------------------------------------------------------------------------
    # 2. mokkei_part1_men_uchi_60fps.mp4
    # --------------------------------------------------------------------------
    {
        "source_video": "mokkei_part1_men_uchi_60fps.mp4",
        "output_filename": "mokkei_part1_00m05s_00m14s_men_uchi_sideview_R2L.mp4",
        "start_time": "00:05",
        "end_time": "00:14",
        "technique": "men_uchi",
        "view_angle": "sideview",
        "description": "Men-uchi strike with Fumikomi-ashi, moving from right to left (60 FPS).",
        "tags": ["men_uchi", "sideview", "fumikomi", "right_to_left", "60fps"],
    },
    {
        "source_video": "mokkei_part1_men_uchi_60fps.mp4",
        "output_filename": "mokkei_part1_00m16s_00m25s_men_uchi_sideview_L2R.mp4",
        "start_time": "00:16",
        "end_time": "00:25",
        "technique": "men_uchi",
        "view_angle": "sideview",
        "description": "Men-uchi strike with Fumikomi-ashi, moving from left to right (60 FPS).",
        "tags": ["men_uchi", "sideview", "fumikomi", "left_to_right", "60fps"],
    },
    {
        "source_video": "mokkei_part1_men_uchi_60fps.mp4",
        "output_filename": "mokkei_part1_04m39s_04m45s_men_uchi_frontview_occluded.mp4",
        "start_time": "04:39",
        "end_time": "04:45",
        "technique": "men_uchi",
        "view_angle": "frontview",
        "description": "Men-uchi from front perspective partially occluded by motodachi (defender).",
        "tags": ["men_uchi", "frontview", "occlusion_stress_test"],
    },
    {
        "source_video": "mokkei_part1_men_uchi_60fps.mp4",
        "output_filename": "mokkei_part1_04m45s_04m50s_men_uchi_backview.mp4",
        "start_time": "04:45",
        "end_time": "04:50",
        "technique": "men_uchi",
        "view_angle": "backview",
        "description": "Men-uchi executed viewed directly from the rear / back perspective.",
        "tags": ["men_uchi", "backview", "zanshin"],
    },
    # --------------------------------------------------------------------------
    # 3. sample2_kendo_basics_shomen_uchi.mp4
    # --------------------------------------------------------------------------
    {
        "source_video": "sample2_kendo_basics_shomen_uchi.mp4",
        "output_filename": "sample2_basics_00m42s_00m49s_shomen_frontview_45deg.mp4",
        "start_time": "00:42",
        "end_time": "00:49",
        "technique": "shomen_uchi",
        "view_angle": "frontview_45deg",
        "description": "Stationary Shomen-uchi demonstration filmed from ~45 degree front-oblique angle.",
        "tags": ["shomen_uchi", "frontview_oblique", "tandoku_dosa"],
    },
    {
        "source_video": "sample2_kendo_basics_shomen_uchi.mp4",
        "output_filename": "sample2_basics_01m55s_02m00s_shomen_sideview.mp4",
        "start_time": "01:55",
        "end_time": "02:00",
        "technique": "shomen_uchi",
        "view_angle": "sideview",
        "description": "Stationary Shomen-uchi strike mechanics filmed from true lateral side view.",
        "tags": ["shomen_uchi", "sideview", "lateral"],
    },
]


def parse_timestamp_to_seconds(ts: str) -> float:
    """Convert timestamp string ('MM:SS', 'HH:MM:SS', or seconds) to float seconds."""
    ts = str(ts).strip()
    if ":" in ts:
        parts = [float(p) for p in ts.split(":")]
        if len(parts) == 2:
            return parts[0] * 60.0 + parts[1]
        elif len(parts) == 3:
            return parts[0] * 3600.0 + parts[1] * 60.0 + parts[2]
    return float(ts)


def get_ffmpeg_binary() -> Optional[str]:
    """Find available FFmpeg executable from imageio-ffmpeg or system PATH."""
    try:
        import imageio_ffmpeg
        exe = imageio_ffmpeg.get_ffmpeg_exe()
        if exe and os.path.exists(exe):
            return exe
    except ImportError:
        pass

    system_ffmpeg = shutil.which("ffmpeg")
    if system_ffmpeg:
        return system_ffmpeg

    return None


def slice_video_ffmpeg(
    ffmpeg_exe: str,
    input_path: Path,
    output_path: Path,
    start_sec: float,
    end_sec: float,
) -> bool:
    """Slice video segment using FFmpeg with frame-accurate H.264 encode."""
    duration = end_sec - start_sec
    cmd = [
        ffmpeg_exe,
        "-y",
        "-ss", str(start_sec),
        "-to", str(end_sec),
        "-i", str(input_path),
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "18",
        "-c:a", "aac",
        "-b:a", "128k",
        str(output_path),
    ]

    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    return result.returncode == 0


def slice_video_opencv(
    input_path: Path,
    output_path: Path,
    start_sec: float,
    end_sec: float,
) -> bool:
    """Slice video segment using OpenCV VideoCapture and VideoWriter fallback."""
    cap = cv2.VideoCapture(str(input_path))
    if not cap.isOpened():
        return False

    fps = cap.get(cv2.CAP_PROP_FPS)
    if fps <= 0:
        fps = 30.0

    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    start_frame = int(round(start_sec * fps))
    end_frame = min(int(round(end_sec * fps)), total_frames)

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(str(output_path), fourcc, fps, (width, height))

    cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
    current_frame = start_frame

    while current_frame < end_frame:
        ret, frame = cap.read()
        if not ret:
            break
        out.write(frame)
        current_frame += 1

    cap.release()
    out.release()
    return True


def get_video_metadata(video_path: Path) -> Dict[str, Any]:
    """Retrieve video width, height, fps, frame count, and duration."""
    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        return {}
    fps = float(cap.get(cv2.CAP_PROP_FPS))
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    cap.release()

    duration_sec = frame_count / fps if fps > 0 else 0.0
    size_mb = video_path.stat().st_size / (1024 * 1024) if video_path.exists() else 0.0

    return {
        "width": w,
        "height": h,
        "fps": round(fps, 2),
        "frame_count": frame_count,
        "duration_sec": round(duration_sec, 2),
        "file_size_mb": round(size_mb, 2),
    }


def main():
    parser = argparse.ArgumentParser(description="Slice reference Kendo videos into short evaluation clips.")
    parser.add_argument(
        "--output-dir",
        type=str,
        default="data/segments",
        help="Destination directory for cropped video clips (default: data/segments).",
    )
    parser.add_argument(
        "--raw-dir",
        type=str,
        default="data/raw",
        help="Source directory containing raw videos (default: data/raw).",
    )
    parser.add_argument(
        "--engine",
        type=str,
        choices=["auto", "ffmpeg", "opencv"],
        default="auto",
        help="Slicing engine: auto, ffmpeg, or opencv (default: auto).",
    )
    args = parser.parse_args()

    raw_dir = PROJECT_ROOT / args.raw_dir
    output_dir = PROJECT_ROOT / args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    # Detect slicing engine
    ffmpeg_exe = get_ffmpeg_binary()
    if args.engine == "ffmpeg":
        if not ffmpeg_exe:
            print("Error: FFmpeg engine requested but ffmpeg executable was not found.")
            sys.exit(1)
        engine = "ffmpeg"
    elif args.engine == "opencv":
        engine = "opencv"
    else:  # auto
        engine = "ffmpeg" if ffmpeg_exe else "opencv"

    print("=" * 75)
    print("Open-Kendo Video Slicing Pipeline")
    print("=" * 75)
    print(f"Source raw videos dir : {raw_dir.relative_to(PROJECT_ROOT)}")
    print(f"Output segments dir   : {output_dir.relative_to(PROJECT_ROOT)}")
    print(f"Active slicing engine : {engine.upper()}" + (f" ({ffmpeg_exe})" if engine == "ffmpeg" else ""))
    print(f"Total defined segments: {len(SEGMENT_CATALOG)}\n")

    catalog_results = []
    success_count = 0

    for i, seg in enumerate(SEGMENT_CATALOG, 1):
        src_file = raw_dir / seg["source_video"]
        out_file = output_dir / seg["output_filename"]

        start_sec = parse_timestamp_to_seconds(seg["start_time"])
        end_sec = parse_timestamp_to_seconds(seg["end_time"])
        target_dur = end_sec - start_sec

        print(f"[{i}/{len(SEGMENT_CATALOG)}] Slicing {seg['output_filename']}...")
        print(f"  Source : {seg['source_video']} | Window: {seg['start_time']} -> {seg['end_time']} ({target_dur:.1f}s)")
        print(f"  Target : {seg['technique']} ({seg['view_angle']})")

        if not src_file.exists():
            print(f"  [ERROR] Source video not found: {src_file}")
            continue

        # Execute crop
        ok = False
        if engine == "ffmpeg" and ffmpeg_exe:
            ok = slice_video_ffmpeg(ffmpeg_exe, src_file, out_file, start_sec, end_sec)
        else:
            ok = slice_video_opencv(src_file, out_file, start_sec, end_sec)

        if not ok or not out_file.exists():
            print(f"  [ERROR] Failed to slice {seg['output_filename']}!")
            continue

        meta = get_video_metadata(out_file)
        print(f"  [SUCCESS] {meta.get('width')}x{meta.get('height')} @ {meta.get('fps')} fps, {meta.get('frame_count')} frames, {meta.get('duration_sec')}s, {meta.get('file_size_mb')} MB")

        seg_entry = dict(seg)
        seg_entry.update({
            "start_sec": start_sec,
            "end_sec": end_sec,
            "actual_duration_sec": meta.get("duration_sec"),
            "width": meta.get("width"),
            "height": meta.get("height"),
            "fps": meta.get("fps"),
            "frame_count": meta.get("frame_count"),
            "file_size_mb": meta.get("file_size_mb"),
            "file_path": str(out_file.relative_to(PROJECT_ROOT)).replace("\\", "/"),
        })
        catalog_results.append(seg_entry)
        success_count += 1

    # Save summary catalog JSON
    catalog_json_path = output_dir / "segments_catalog.json"
    catalog_payload = {
        "metadata": {
            "title": "Open-Kendo Sliced Benchmark Video Segments",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "engine_used": engine,
            "total_segments": len(catalog_results),
            "output_directory": str(output_dir.relative_to(PROJECT_ROOT)).replace("\\", "/"),
        },
        "segments": catalog_results,
    }

    with open(catalog_json_path, "w", encoding="utf-8") as f:
        json.dump(catalog_payload, f, indent=2, ensure_ascii=False)

    print("\n" + "=" * 75)
    print(f"COMPLETED: Sliced {success_count}/{len(SEGMENT_CATALOG)} video segments successfully!")
    print(f"Segments catalog saved to: {catalog_json_path.relative_to(PROJECT_ROOT)}")
    print("=" * 75)


if __name__ == "__main__":
    main()
