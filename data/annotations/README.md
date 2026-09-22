# Kendo Video Event Annotation Guide

Manual event annotation system for Kendo striking techniques (Men-uchi, Suburi, Fumikomi, and Ki-Ken-Tai-Ichi).

Interactive GUI tool: [`scripts/annotate_events_gui.py`](../../scripts/annotate_events_gui.py).

---

## 1. Launching the Tool

Run in terminal:
```powershell
# Open default playlist of all clips in data/segments/
.\.venv\Scripts\python.exe scripts/annotate_events_gui.py

# Or open a specific video clip directly:
.\.venv\Scripts\python.exe scripts/annotate_events_gui.py --video data/segments/mokkei_part1_00m05s_00m14s_men_uchi_sideview_R2L.mp4
```

---

## 2. Keyboard Controls (Hotkeys)

### A. Multi-Repetition Management
| Key | Action | Description |
| :---: | :--- | :--- |
| **`Tab`** or **`R`** | **Add New Repetition** | Finalize current rep and create a new one (`Rep #2`, `Rep #3`...) |
| **`J`** / **`K`** | **Prev / Next Repetition** | Switch active repetition for review or edit |
| **`X`** | **Delete Repetition** | Remove currently selected repetition |

### B. Event Marking (Numeric Keys for Active Repetition)
| Key | Event Name | Technical Description | Marker Color |
| :---: | :--- | :--- | :---: |
| **`1`** | **Furikaburi Start** | Beginning of upward swing trajectory | Green |
| **`2`** | **Swing Apex** | Highest point of the swing arc | Yellow |
| **`3`** | **Fumikomi Landing (Optional)** | Right foot floor contact (optional for stationary Suburi) | Cyan |
| **`4`** | **Impact / Tenouchi Finish** | Target contact on Men or wrist deceleration snap | Red |
| **`5`** | **Zanshin Complete** | Follow-through completion and return to alertness | Purple |
| **`C`** | **Clear Event** | Remove event marker at current frame in active rep | - |
| **`Enter`** | **Save** | Save all repetitions to JSON file | - |

### C. Playback & Frame Scrubbing
| Key / Input | Action |
| :--- | :--- |
| **`Space`** | Play / Pause toggle |
| **`D`** or **Right Arrow** | Step forward 1 frame (+1) |
| **`A`** or **Left Arrow** | Step backward 1 frame (-1) |
| **`W`** or **Up Arrow** | Jump forward 10 frames (+10) |
| **`S`** or **Down Arrow** | Jump backward 10 frames (-10) |
| **`[`** / **`]`** | Change playback speed: `0.1x`, `0.25x`, `0.5x`, `1.0x`, `2.0x` |
| **Left Click / Drag** | Click or drag on the bottom timeline bar to scrub instantly |
| **`N`** / **`P`** | Auto-save and load Next / Previous video in catalog |
| **`H`** | Toggle on-screen Help HUD overlay |
| **`Esc`** or **`Q`** | Quit application |

---

## 3. Automated Ki-Ken-Tai-Ichi Analysis

When both **`[3] Fumikomi Landing`** and **`[4] Blade Impact`** are marked, the tool calculates temporal difference:

$$\Delta t = t_{\text{impact}} - t_{\text{fumikomi}} \quad (\text{ms})$$

- $|\Delta t| \le 50\text{ ms}$ (within approx. 3 frames at 60 FPS): **EXCELLENT SYNCHRONIZATION** (Ideal Ki-Ken-Tai-Ichi).
- $\Delta t > 50\text{ ms}$: Late impact (foot stamped before blade reached target).
- $\Delta t < -50\text{ ms}$: Early impact (blade reached target before foot landed).

For stationary Suburi without foot stomp, the tool computes total swing duration from Furikaburi to Tenouchi Finish.

---

## 4. Annotation Storage Format (`data/annotations/*.json`)

When saving or switching clips, data is written to `data/annotations/{clip_stem}_events.json`:
```json
{
  "metadata": {
    "source_video": "mokkei_part1_00m05s_00m14s_men_uchi_sideview_R2L.mp4",
    "annotated_at": "2026-09-21T04:28:58Z",
    "fps": 59.94,
    "total_frames": 540,
    "duration_sec": 9.009,
    "total_repetitions": 2
  },
  "repetitions": [
    {
      "rep_id": 1,
      "events": [
        {
          "event_id": "furikaburi_start",
          "event_name": "Furikaburi Start",
          "frame_index": 120,
          "timestamp_sec": 2.002,
          "timestamp_formatted": "00:02.002"
        },
        {
          "event_id": "fumikomi_landing",
          "event_name": "Fumikomi Landing (Opt)",
          "frame_index": 215,
          "timestamp_sec": 3.587,
          "timestamp_formatted": "00:03.587"
        },
        {
          "event_id": "blade_impact",
          "event_name": "Impact / Tenouchi",
          "frame_index": 217,
          "timestamp_sec": 3.62,
          "timestamp_formatted": "00:03.620"
        }
      ],
      "metrics": {
        "swing_duration_sec": 1.618,
        "swing_duration_ms": 1618.3,
        "kikentai_analysis": {
          "fumikomi_frame": 215,
          "impact_frame": 217,
          "delta_frames": 2,
          "delta_time_ms": 33.37,
          "evaluation": "EXCELLENT_SYNCHRONIZATION (Ki-Ken-Tai-Ichi ideal)"
        }
      }
    }
  ]
}
```
