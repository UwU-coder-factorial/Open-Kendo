#!/usr/bin/env python3
"""Interactive Multi-Repetition Event Annotation Tool for Kendo Video Segments.

An intuitive OpenCV-based GUI player designed for precision frame-by-frame
annotation of Kendo strike events (Furikaburi, Apex, Fumikomi, Impact, Zanshin)
supporting multiple repetitions (strikes) per video clip.

Features:
- Multi-repetition management (Rep 1, Rep 2, Rep 3...) per video.
- Sub-millisecond & frame-level scrubbing (1-frame step, 10-frame jump).
- Variable speed playback (0.1x slow-mo to 2.0x).
- Clickable timeline scrubber bar with multi-rep visual brackets.
- Dedicated numeric hotkeys for Kendo strike phases.
- Real-time Ki-Ken-Tai-Ichi synchronicity analysis (delta_t between Foot Stomp & Blade Contact)
  and Suburi swing duration calculation.
- Auto-saves annotations to data/annotations/{clip_stem}_events.json.
- Seamless playlist switching between clips in data/segments/.

Keyboard Controls:
  [Space]       : Play / Pause toggle
  [A] / [Left]  : Previous frame (-1)
  [D] / [Right] : Next frame (+1)
  [W] / [Up]    : Jump +10 frames
  [S] / [Down]  : Jump -10 frames
  [[] / []]     : Speed down / Speed up (0.1x, 0.25x, 0.5x, 1.0x, 2.0x)

  REPETITION CONTROLS:
  [Tab] / [R]   : Add New Repetition (Lượt chém mới)
  [J] / [K]     : Previous / Next Repetition (Chuyển đổi lượt chém)
  [X]           : Delete current Repetition (Xóa lượt chém hiện tại)

  EVENT MARKING:
  [1]           : Mark Furikaburi Start (Vung kiếm lên)
  [2]           : Mark Swing Apex (Đỉnh đường kiếm)
  [3]           : Mark Fumikomi Landing (Chân phải chạm sàn - tùy chọn)
  [4]           : Mark Impact / Tenouchi Finish (Chạm Men hoặc Hãm kiếm)
  [5]           : Mark Zanshin Complete (Hoàn thành thế thủ)
  [C]           : Clear event at current frame for active repetition

  NAVIGATION & FILE:
  [Enter]       : Save annotations to JSON
  [N] / [P]     : Next / Previous video clip in segments catalog
  [H]           : Toggle on-screen Help HUD
  [Q] / [Esc]   : Quit
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import cv2
import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Event definitions: Name, color (BGR), short description
EVENT_DEFINITIONS = {
    "1": {
        "id": "furikaburi_start",
        "name": "Furikaburi Start",
        "short_name": "Furi",
        "color": (0, 255, 128),  # Vibrant Green
    },
    "2": {
        "id": "apex_top",
        "name": "Swing Apex (Top)",
        "short_name": "Apex",
        "color": (0, 230, 255),  # Yellow / Amber
    },
    "3": {
        "id": "fumikomi_landing",
        "name": "Fumikomi Landing (Opt)",
        "short_name": "Fumi",
        "color": (255, 180, 0),  # Cyan / Sky Blue
    },
    "4": {
        "id": "blade_impact",
        "name": "Impact / Tenouchi",
        "short_name": "Impact",
        "color": (0, 0, 255),  # Bright Red
    },
    "5": {
        "id": "zanshin_complete",
        "name": "Zanshin Complete",
        "short_name": "Zanshin",
        "color": (255, 0, 255),  # Magenta / Purple
    },
}

PLAYBACK_SPEEDS = [0.1, 0.25, 0.5, 1.0, 2.0]

# Distinct colors for repetition markers on the timeline
REP_COLORS = [
    (0, 200, 255),   # Rep 1: Gold / Yellow
    (255, 120, 0),   # Rep 2: Deep Sky Blue
    (0, 255, 180),   # Rep 3: Mint Green
    (180, 50, 255),  # Rep 4: Violet
    (50, 255, 255),  # Rep 5: Bright Cyan
    (255, 180, 50),  # Rep 6: Lavender
]


class KendoAnnotatorApp:
    """OpenCV interactive video annotation GUI application with multi-repetition support."""

    def __init__(self, video_paths: List[Path], out_dir: Path):
        self.video_paths = video_paths
        self.current_video_idx = 0
        self.out_dir = out_dir
        self.out_dir.mkdir(parents=True, exist_ok=True)

        self.cap: Optional[cv2.VideoCapture] = None
        self.total_frames = 0
        self.fps = 30.0
        self.width = 1280
        self.height = 720
        self.duration_sec = 0.0

        self.current_frame_idx = 0
        self.is_playing = False
        self.speed_idx = 3  # Default 1.0x
        self.show_help = True

        # Multi-repetition state: list of dicts [{"rep_id": 1, "events": {event_id: frame_idx}}]
        self.repetitions: List[Dict[str, Any]] = [{"rep_id": 1, "events": {}}]
        self.active_rep_idx = 0

        # Mouse scrubber interaction state
        self.mouse_scrubbing = False
        self.timeline_y_start = 0
        self.timeline_height = 46

        self.window_name = "Open-Kendo - Multi-Repetition Event Annotator"
        cv2.namedWindow(self.window_name, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(self.window_name, 1280, 780)
        cv2.setMouseCallback(self.window_name, self._mouse_callback)

        self._load_video(self.current_video_idx)

    @property
    def current_video_path(self) -> Path:
        return self.video_paths[self.current_video_idx]

    @property
    def current_rep(self) -> Dict[str, Any]:
        if not self.repetitions:
            self.repetitions = [{"rep_id": 1, "events": {}}]
            self.active_rep_idx = 0
        return self.repetitions[self.active_rep_idx]

    def _get_annotation_file_path(self, video_path: Path) -> Path:
        return self.out_dir / f"{video_path.stem}_events.json"

    def _load_annotations(self):
        """Load annotations with backwards-compatible support for legacy single-rep files."""
        self.repetitions = [{"rep_id": 1, "events": {}}]
        self.active_rep_idx = 0

        ann_path = self._get_annotation_file_path(self.current_video_path)
        if ann_path.exists():
            try:
                with open(ann_path, "r", encoding="utf-8") as f:
                    data = json.load(f)

                if "repetitions" in data and len(data["repetitions"]) > 0:
                    self.repetitions = []
                    for i, r in enumerate(data["repetitions"], 1):
                        evs = {}
                        if isinstance(r.get("events"), list):
                            for ev in r["events"]:
                                evs[ev["event_id"]] = int(ev["frame_index"])
                        elif isinstance(r.get("events"), dict):
                            evs = {k: int(v) for k, v in r["events"].items()}
                        self.repetitions.append({
                            "rep_id": r.get("rep_id", i),
                            "events": evs,
                        })
                    self.active_rep_idx = 0
                    print(f"Loaded {len(self.repetitions)} repetitions from {ann_path.name}")
                elif "annotated_events" in data:
                    # Legacy single-rep format migration
                    evs = {}
                    for ev in data.get("annotated_events", []):
                        evs[ev["event_id"]] = int(ev["frame_index"])
                    self.repetitions = [{"rep_id": 1, "events": evs}]
                    self.active_rep_idx = 0
                    print(f"Migrated 1 repetition from legacy format in {ann_path.name}")
            except Exception as e:
                print(f"Failed to load existing annotations: {e}")

    def save_annotations(self):
        """Save multi-repetition event annotations to structured JSON."""
        ann_path = self._get_annotation_file_path(self.current_video_path)
        reps_data = []

        for rep in self.repetitions:
            events_list = []
            ev_dict = rep["events"]

            for key, defn in EVENT_DEFINITIONS.items():
                ev_id = defn["id"]
                if ev_id in ev_dict:
                    f_idx = ev_dict[ev_id]
                    t_sec = f_idx / self.fps if self.fps > 0 else 0.0
                    events_list.append({
                        "event_id": ev_id,
                        "event_name": defn["name"],
                        "frame_index": f_idx,
                        "timestamp_sec": round(t_sec, 4),
                        "timestamp_formatted": f"{int(t_sec//60):02d}:{t_sec%60:06.3f}",
                    })

            # Metrics for this repetition
            rep_metrics = {}
            if "furikaburi_start" in ev_dict and "blade_impact" in ev_dict:
                swing_frames = ev_dict["blade_impact"] - ev_dict["furikaburi_start"]
                rep_metrics["swing_duration_sec"] = round(swing_frames / self.fps, 4)
                rep_metrics["swing_duration_ms"] = round((swing_frames / self.fps) * 1000.0, 1)

            if "fumikomi_landing" in ev_dict and "blade_impact" in ev_dict:
                f_fumikomi = ev_dict["fumikomi_landing"]
                f_impact = ev_dict["blade_impact"]
                frame_diff = f_impact - f_fumikomi
                dt_ms = (frame_diff / self.fps) * 1000.0 if self.fps > 0 else 0.0

                if abs(dt_ms) <= 50.0:
                    eval_str = "EXCELLENT_SYNCHRONIZATION (Ki-Ken-Tai-Ichi ideal)"
                elif dt_ms > 50.0:
                    eval_str = "LATE_IMPACT (Foot stamped before blade reached target)"
                else:
                    eval_str = "EARLY_IMPACT (Blade reached target before foot landed)"

                rep_metrics["kikentai_analysis"] = {
                    "fumikomi_frame": f_fumikomi,
                    "impact_frame": f_impact,
                    "delta_frames": frame_diff,
                    "delta_time_ms": round(dt_ms, 2),
                    "evaluation": eval_str,
                }

            reps_data.append({
                "rep_id": rep["rep_id"],
                "events": events_list,
                "metrics": rep_metrics,
            })

        payload = {
            "metadata": {
                "source_video": self.current_video_path.name,
                "annotated_at": datetime.now(timezone.utc).isoformat(),
                "fps": round(self.fps, 2),
                "total_frames": self.total_frames,
                "duration_sec": round(self.duration_sec, 3),
                "total_repetitions": len(reps_data),
            },
            "repetitions": reps_data,
        }

        with open(ann_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2, ensure_ascii=False)

        print(f"\n[SAVED] Saved {len(reps_data)} repetitions -> {ann_path.name}")
        for r in reps_data:
            m = r.get("metrics", {})
            if "kikentai_analysis" in m:
                k = m["kikentai_analysis"]
                print(f"  Rep #{r['rep_id']}: Ki-Ken-Tai Delta = {k['delta_time_ms']} ms ({k['evaluation']})")
            elif "swing_duration_ms" in m:
                print(f"  Rep #{r['rep_id']}: Swing Time = {m['swing_duration_ms']} ms")

    def _load_video(self, idx: int):
        if self.cap is not None:
            self.cap.release()

        self.current_video_idx = max(0, min(idx, len(self.video_paths) - 1))
        vid_p = self.current_video_path

        self.cap = cv2.VideoCapture(str(vid_p))
        if not self.cap.isOpened():
            print(f"Error: Unable to open video {vid_p}")
            return

        self.fps = float(self.cap.get(cv2.CAP_PROP_FPS))
        if self.fps <= 0:
            self.fps = 30.0

        self.total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.duration_sec = self.total_frames / self.fps if self.fps > 0 else 0.0

        self.current_frame_idx = 0
        self.is_playing = False
        self._load_annotations()
        print(f"\nLoaded Clip [{self.current_video_idx + 1}/{len(self.video_paths)}]: {vid_p.name}")
        print(f"  {self.width}x{self.height} @ {self.fps:.2f} FPS | {self.total_frames} frames ({self.duration_sec:.2f}s)")

    def add_repetition(self):
        """Add a new repetition strike."""
        new_id = len(self.repetitions) + 1
        self.repetitions.append({"rep_id": new_id, "events": {}})
        self.active_rep_idx = len(self.repetitions) - 1
        print(f"\n[+] Created & switched to Repetition #{new_id}")

    def switch_repetition(self, step: int):
        """Switch to previous (-1) or next (+1) repetition."""
        if not self.repetitions:
            return
        self.active_rep_idx = (self.active_rep_idx + step) % len(self.repetitions)
        rep = self.current_rep
        print(f"[*] Switched to Repetition #{rep['rep_id']} ({self.active_rep_idx + 1}/{len(self.repetitions)})")
        # Jump to first event in this repetition if available
        if rep["events"]:
            first_frame = min(rep["events"].values())
            self.current_frame_idx = first_frame

    def delete_repetition(self):
        """Delete currently active repetition."""
        if len(self.repetitions) <= 1:
            self.repetitions[0]["events"] = {}
            print("[*] Cleared events for Repetition #1 (cannot delete sole repetition).")
            return

        removed_id = self.repetitions[self.active_rep_idx]["rep_id"]
        self.repetitions.pop(self.active_rep_idx)
        # Re-index remaining repetitions
        for i, r in enumerate(self.repetitions, 1):
            r["rep_id"] = i

        self.active_rep_idx = max(0, min(self.active_rep_idx, len(self.repetitions) - 1))
        print(f"[-] Deleted Repetition #{removed_id}. Active is now Rep #{self.current_rep['rep_id']}")

    def _mouse_callback(self, event, x, y, flags, param):
        """Allow scrubbing timeline by clicking or dragging on bottom timeline bar."""
        if y >= self.timeline_y_start:
            if event == cv2.EVENT_LBUTTONDOWN:
                self.mouse_scrubbing = True
                self._scrub_to_x(x)
            elif event == cv2.EVENT_MOUSEMOVE and self.mouse_scrubbing:
                self._scrub_to_x(x)
        if event == cv2.EVENT_LBUTTONUP:
            self.mouse_scrubbing = False

    def _scrub_to_x(self, x: int):
        if self.total_frames > 1:
            fraction = max(0.0, min(1.0, x / float(self.width)))
            target_frame = int(round(fraction * (self.total_frames - 1)))
            self.current_frame_idx = target_frame
            self.is_playing = False

    def _draw_overlay(self, frame: np.ndarray) -> np.ndarray:
        h, w = frame.shape[:2]
        canvas = frame.copy()

        current_time_sec = self.current_frame_idx / self.fps if self.fps > 0 else 0.0

        # 1. Top HUD Banner (Semi-transparent black)
        hud_h = 82
        top_overlay = canvas.copy()
        cv2.rectangle(top_overlay, (0, 0), (w, hud_h), (18, 18, 18), -1)
        cv2.addWeighted(top_overlay, 0.82, canvas, 0.18, 0, canvas)
        cv2.line(canvas, (0, hud_h), (w, hud_h), (0, 200, 255), 1)

        # Title and Clip info
        clip_name = self.current_video_path.name
        title_str = f"[{self.current_video_idx + 1}/{len(self.video_paths)}] {clip_name} ({self.fps:.1f} FPS)"
        cv2.putText(canvas, title_str, (16, 24), cv2.FONT_HERSHEY_SIMPLEX, 0.62, (0, 230, 255), 1, cv2.LINE_AA)

        # Active Repetition Status
        rep = self.current_rep
        rep_col = REP_COLORS[(rep['rep_id'] - 1) % len(REP_COLORS)]
        rep_badge = f"ACTIVE STRIKE: REP #{rep['rep_id']} of {len(self.repetitions)} ([Tab]/[R]: New Rep | [J]/[K]: Switch)"
        cv2.putText(canvas, rep_badge, (16, 48), cv2.FONT_HERSHEY_SIMPLEX, 0.52, rep_col, 2, cv2.LINE_AA)

        # Time & Frame counter
        time_str = f"F#{self.current_frame_idx:04d}/{self.total_frames:04d} | {current_time_sec:06.3f}s/{self.duration_sec:05.2f}s | Speed: {PLAYBACK_SPEEDS[self.speed_idx]}x {'[PLAY]' if self.is_playing else '[PAUSE]'}"
        cv2.putText(canvas, time_str, (16, 72), cv2.FONT_HERSHEY_SIMPLEX, 0.48, (230, 230, 230), 1, cv2.LINE_AA)

        # Real-time Synchronicity & Swing Metrics for Active Repetition
        ev_dict = rep["events"]
        metrics_text = ""
        metrics_col = (0, 255, 128)
        if "fumikomi_landing" in ev_dict and "blade_impact" in ev_dict:
            dt_ms = ((ev_dict["blade_impact"] - ev_dict["fumikomi_landing"]) / self.fps) * 1000.0
            metrics_col = (0, 255, 128) if abs(dt_ms) <= 50.0 else (0, 120, 255)
            metrics_text = f"Ki-Ken-Tai Delta: {dt_ms:+.1f} ms"
        elif "furikaburi_start" in ev_dict and "blade_impact" in ev_dict:
            dur_ms = ((ev_dict["blade_impact"] - ev_dict["furikaburi_start"]) / self.fps) * 1000.0
            metrics_text = f"Swing Time: {dur_ms:.0f} ms"
            metrics_col = (0, 230, 255)

        if metrics_text:
            cv2.putText(canvas, metrics_text, (w - 360, 24), cv2.FONT_HERSHEY_SIMPLEX, 0.58, metrics_col, 2, cv2.LINE_AA)

        # 2. Bottom Timeline Bar
        self.timeline_y_start = h - self.timeline_height
        cv2.rectangle(canvas, (0, self.timeline_y_start), (w, h), (22, 22, 22), -1)
        cv2.line(canvas, (0, self.timeline_y_start), (w, self.timeline_y_start), (60, 60, 60), 1)

        # Progress bar background fill
        progress_w = int((self.current_frame_idx / max(1, self.total_frames - 1)) * w)
        cv2.rectangle(canvas, (0, self.timeline_y_start), (progress_w, h), (50, 50, 50), -1)

        # Draw Multi-Repetition Brackets & Pins on Timeline
        for r_idx, r_entry in enumerate(self.repetitions):
            r_evs = r_entry["events"]
            is_active = (r_idx == self.active_rep_idx)
            r_color = REP_COLORS[(r_entry["rep_id"] - 1) % len(REP_COLORS)]

            # Draw Repetition Span Bar (if start and impact exist)
            start_f = r_evs.get("furikaburi_start")
            end_f = r_evs.get("zanshin_complete") or r_evs.get("blade_impact")
            if start_f is not None and end_f is not None and end_f >= start_f:
                span_x1 = int((start_f / max(1, self.total_frames - 1)) * w)
                span_x2 = int((end_f / max(1, self.total_frames - 1)) * w)
                bar_y = self.timeline_y_start + 2
                cv2.rectangle(canvas, (span_x1, bar_y), (span_x2, bar_y + 6), r_color, -1)
                # Label Repetition tag
                label_txt = f"R{r_entry['rep_id']}"
                cv2.putText(canvas, label_txt, (span_x1 + 2, self.timeline_y_start + 24), cv2.FONT_HERSHEY_SIMPLEX, 0.40, r_color, 1, cv2.LINE_AA)

            # Draw Event Pins for this Repetition
            for defn in EVENT_DEFINITIONS.values():
                ev_id = defn["id"]
                if ev_id in r_evs:
                    ev_f = r_evs[ev_id]
                    pin_x = int((ev_f / max(1, self.total_frames - 1)) * w)
                    pin_col = defn["color"]

                    if is_active:
                        # Active rep: full vertical line and large dot with dark ring
                        cv2.line(canvas, (pin_x, self.timeline_y_start), (pin_x, h), pin_col, 2, cv2.LINE_AA)
                        cv2.circle(canvas, (pin_x, self.timeline_y_start + 12), 6, pin_col, -1, cv2.LINE_AA)
                        cv2.circle(canvas, (pin_x, self.timeline_y_start + 12), 7, (0, 0, 0), 1, cv2.LINE_AA)
                    else:
                        # Inactive rep: smaller subtle dot
                        cv2.circle(canvas, (pin_x, self.timeline_y_start + 12), 4, pin_col, -1, cv2.LINE_AA)

        # Current Playhead Pin (White)
        cv2.line(canvas, (progress_w, self.timeline_y_start), (progress_w, h), (255, 255, 255), 2, cv2.LINE_AA)
        cv2.circle(canvas, (progress_w, self.timeline_y_start + 12), 5, (255, 255, 255), -1)

        # 3. Help HUD overlay (toggleable with H)
        if self.show_help:
            hud_box_w = 420
            hud_box_h = 280
            hud_x = w - hud_box_w - 12
            hud_y = hud_h + 10
            hud_ov = canvas.copy()
            cv2.rectangle(hud_ov, (hud_x, hud_y), (hud_x + hud_box_w, hud_y + hud_box_h), (15, 15, 15), -1)
            cv2.addWeighted(hud_ov, 0.88, canvas, 0.12, 0, canvas)
            cv2.rectangle(canvas, (hud_x, hud_y), (hud_x + hud_box_w, hud_y + hud_box_h), (0, 200, 255), 1)

            lines = [
                "HOTKEYS: MULTI-STRIKE ANNOTATION",
                "[Tab] / [R] : Add New Repetition (Luot chem moi)",
                "[J] / [K]   : Prev / Next Repetition",
                "[X]         : Delete Active Repetition",
                "[1] Furikaburi Start (Vung kiem)",
                "[2] Swing Apex (Dinh duong kiem)",
                "[3] Fumikomi Landing (Dam chan - Tuy chon)",
                "[4] Impact / Tenouchi Finish (Cham Men / Ham kiem)",
                "[5] Zanshin Complete (The thu)",
                "[C] Clear event at current frame",
                "[Enter]: Save to JSON",
                "[Space] Play/Pause | [A]/[D] -1/+1 | [W]/[S] -10/+10",
                "[[]/[]] Speed: 0.1x - 2.0x | [N]/[P] Next/Prev clip",
                "[H] Toggle help HUD",
            ]
            for i, line in enumerate(lines):
                if i == 0:
                    col = (0, 230, 255)
                    scale = 0.48
                elif i in (1, 2, 3):
                    col = (0, 255, 255)
                    scale = 0.44
                elif i in (4, 5, 6, 7, 8):
                    col = (255, 255, 255)
                    scale = 0.44
                else:
                    col = (190, 190, 190)
                    scale = 0.42
                cv2.putText(
                    canvas,
                    line,
                    (hud_x + 12, hud_y + 20 + i * 19),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    scale,
                    col,
                    1,
                    cv2.LINE_AA,
                )

        # 4. Status List for Active Repetition (Left side)
        status_y = hud_h + 24
        header_txt = f"Repetition #{rep['rep_id']} Events:"
        cv2.putText(canvas, header_txt, (18, status_y), cv2.FONT_HERSHEY_SIMPLEX, 0.52, rep_col, 2, cv2.LINE_AA)
        status_y += 24

        for defn in EVENT_DEFINITIONS.values():
            ev_id = defn["id"]
            if ev_id in ev_dict:
                ev_f = ev_dict[ev_id]
                t_str = f"{ev_f / self.fps:05.2f}s"
                txt = f"{defn['name']}: F#{ev_f:04d} ({t_str})"
                # Color bullet
                cv2.circle(canvas, (18, status_y - 4), 6, defn["color"], -1)
                cv2.putText(canvas, txt, (32, status_y), cv2.FONT_HERSHEY_SIMPLEX, 0.48, (255, 255, 255), 1, cv2.LINE_AA)
                status_y += 22

        return canvas

    def run(self):
        """Main application loop."""
        while True:
            if self.cap is None or not self.cap.isOpened():
                break

            self.cap.set(cv2.CAP_PROP_POS_FRAMES, self.current_frame_idx)
            ret, frame = self.cap.read()
            if not ret:
                # Loop back or stop
                if self.is_playing:
                    self.current_frame_idx = 0
                    continue
                else:
                    break

            display_frame = self._draw_overlay(frame)
            cv2.imshow(self.window_name, display_frame)

            # Frame rate delay calculation
            speed = PLAYBACK_SPEEDS[self.speed_idx]
            base_delay_ms = int(1000.0 / (self.fps * speed)) if self.fps > 0 else 33
            delay = max(1, base_delay_ms) if self.is_playing else 30

            key = cv2.waitKey(delay) & 0xFF

            if key in (ord("q"), ord("Q"), 27):  # Esc or Q
                break
            elif key == ord(" "):  # Space
                self.is_playing = not self.is_playing
            elif key in (ord("d"), ord("D"), 83):  # Right or D
                self.is_playing = False
                self.current_frame_idx = min(self.total_frames - 1, self.current_frame_idx + 1)
            elif key in (ord("a"), ord("A"), 81):  # Left or A
                self.is_playing = False
                self.current_frame_idx = max(0, self.current_frame_idx - 1)
            elif key in (ord("w"), ord("W"), 82):  # Up or W (+10 frames)
                self.is_playing = False
                self.current_frame_idx = min(self.total_frames - 1, self.current_frame_idx + 10)
            elif key in (ord("s"), ord("S"), 84):  # Down or S (-10 frames)
                self.is_playing = False
                self.current_frame_idx = max(0, self.current_frame_idx - 10)
            elif key in (13, 10):  # Enter key: Save
                self.save_annotations()
            elif key == 9 or key in (ord("r"), ord("R")):  # Tab or R: New Repetition
                self.add_repetition()
            elif key in (ord("j"), ord("J")):  # J: Previous Repetition
                self.switch_repetition(-1)
            elif key in (ord("k"), ord("K")):  # K: Next Repetition
                self.switch_repetition(1)
            elif key in (ord("x"), ord("X")):  # X: Delete current Repetition
                self.delete_repetition()
            elif key == ord("["):  # Speed down
                self.speed_idx = max(0, self.speed_idx - 1)
            elif key == ord("]"):  # Speed up
                self.speed_idx = min(len(PLAYBACK_SPEEDS) - 1, self.speed_idx + 1)
            elif key in (ord("h"), ord("H")):  # Help toggle
                self.show_help = not self.show_help
            elif key in (ord("n"), ord("N")):  # Next video
                self.save_annotations()
                self._load_video((self.current_video_idx + 1) % len(self.video_paths))
            elif key in (ord("p"), ord("P")):  # Previous video
                self.save_annotations()
                self._load_video((self.current_video_idx - 1) % len(self.video_paths))
            elif chr(key) in EVENT_DEFINITIONS:  # 1 to 5: Mark Event in current rep
                defn = EVENT_DEFINITIONS[chr(key)]
                rep = self.current_rep
                rep["events"][defn["id"]] = self.current_frame_idx
                print(f"[Rep #{rep['rep_id']}] Marked [{defn['name']}] at Frame {self.current_frame_idx:04d} ({self.current_frame_idx / self.fps:06.3f}s)")
            elif key in (ord("c"), ord("C")):  # Clear event in current rep
                rep = self.current_rep
                to_remove = [k for k, v in rep["events"].items() if v == self.current_frame_idx]
                for k in to_remove:
                    del rep["events"][k]
                    print(f"[Rep #{rep['rep_id']}] Removed event '{k}' at Frame {self.current_frame_idx}")

            # If playing, advance frame
            if self.is_playing:
                self.current_frame_idx += 1
                if self.current_frame_idx >= self.total_frames:
                    self.current_frame_idx = 0  # Loop playback

        if self.cap:
            self.cap.release()
        cv2.destroyAllWindows()


def main():
    parser = argparse.ArgumentParser(description="Kendo Video Event Annotation GUI")
    parser.add_argument(
        "--segments-dir",
        type=str,
        default="data/segments",
        help="Directory containing video segments to annotate (default: data/segments).",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="data/annotations",
        help="Directory to store annotation JSON files (default: data/annotations).",
    )
    parser.add_argument(
        "--video",
        type=str,
        default=None,
        help="Path to a specific video file to annotate instead of the full directory.",
    )
    args = parser.parse_args()

    out_dir = PROJECT_ROOT / args.output_dir

    if args.video:
        vid_p = Path(args.video)
        if not vid_p.is_absolute():
            vid_p = PROJECT_ROOT / vid_p
        if not vid_p.exists():
            print(f"Error: Specified video not found: {vid_p}")
            sys.exit(1)
        video_paths = [vid_p]
    else:
        seg_dir = PROJECT_ROOT / args.segments_dir
        video_paths = sorted([p for p in seg_dir.glob("*.mp4")])
        if not video_paths:
            print(f"Error: No .mp4 video segments found in {seg_dir}")
            sys.exit(1)

    print("=" * 70)
    print("Open-Kendo - Multi-Repetition Video Event Annotation Tool")
    print("=" * 70)
    print(f"Found {len(video_paths)} video segments.")
    print("Starting GUI...")

    app = KendoAnnotatorApp(video_paths=video_paths, out_dir=out_dir)
    app.run()


if __name__ == "__main__":
    main()
