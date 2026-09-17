# Open-Kendo 🥋⚡

> **Real-time Computer Vision & Kinematic Analysis Framework for Kendo Martial Arts**  
> Focused on Pedagogical Training Form (Kihon-waza) & 3-Phase Motion Lifecycle Analysis.

[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Linter: ruff](https://img.shields.io/badge/linter-ruff-red.svg)](https://github.com/astral-sh/ruff)
[![Architecture: Specified](https://img.shields.io/badge/architecture-docs%2Farchitecture.md-brightgreen.svg)](docs/architecture.md)

---

## 📌 Overview & Problem Statement

In **Kendo (剣道 - The Way of the Sword)**, training is fundamentally pedagogical: execution is not judged merely on striking speed or contact registration, but on adherence to correct form throughout the entire strike lifecycle:

1. **Pre-Attack Kamae (Thế thủ chuẩn bị)**: Straight vertical spine, balanced stance, grounded left heel, and centered sword tip threatening the opponent's centerline.
2. **Motion Execution (Phát lực & Chém)**: Maintaining an upright spine without leaning backward or lunging forward, steady eye-line without head tilting, and strict **Ki-Ken-Tai-Ichi (気剣体一致 - Spirit, Sword, and Body as One)** synchronization.
3. **Post-Attack Zanshin (Kiểm soát hậu đòn đánh)**: Prompt recovery back into Kamae, sword tip immediately dominating the centerline, and mental readiness for the next encounter.

**Open-Kendo** is an open-source, modular Computer Vision template framework designed to analyze live 60 FPS camera feeds and provide continuous, structured feedback on all 3 phases of Kendo strikes.

> 📖 **Full Architectural Specification**: See [docs/architecture.md](docs/architecture.md) for mathematical formulas, state machine contracts, and scoring thresholds.

---

## 🏗️ 3-Phase State & Motion Lifecycle Architecture

```text
┌────────────────────────────────────────────────────────┐
│                 CAMERA INPUT STREAM (60FPS)            │
└───────────────────────────┬────────────────────────────┘
                            │
                            ▼
┌────────────────────────────────────────────────────────┐
│         POSE & SHINAI EXTRACTION (MediaPipe/YOLO)      │
└───────────────────────────┬────────────────────────────┘
                            │
                            ▼
┌────────────────────────────────────────────────────────┐
│           STATE & MOTION LIFECYCLE TRACKER             │
└───────────────────────────┬────────────────────────────┘
                            │
┌───────────────────────────┼────────────────────────────┐
│                           │                            │
▼                           ▼                            ▼
[PHA 1: PRE-ATTACK KAMAE]   [PHA 2: MOTION EXECUTION]   [PHA 3: POST-ATTACK ZANSHIN]
  • Trục lưng thẳng           • Trục lưng không ngả       • Rút về Kamae chuẩn
  • Khoảng cách 2 chân        • Đầu không lắc nghiêng     • Mũi kiếm hướng mục tiêu
  • Góc 2 tay chuẩn           • Đo đạc Ki-Ken-Tai-Ichi    • Sẵn sàng đòn tiếp theo
│                           │                            │
└───────────────────────────┼────────────────────────────┘
                            │
                            ▼
┌────────────────────────────────────────────────────────┐
│           INTEGRATED SCORE & CONTINUOUS FEEDBACK       │
│   Score = (Kamae Score) + (Kinematics & Timing Score)  │
│           + (Zanshin Score)                            │
└────────────────────────────────────────────────────────┘
```

---

## 🌟 Core Features

- **🦾 Multi-backend Pose Estimation**: Standardized wrapper supporting Google **MediaPipe** (low-latency CPU/edge) and **Ultralytics YOLO-Pose** (high-accuracy GPU inference).
- **🗡️ Shinai & Kensen Tracking**: Continuous tracking of the bamboo sword tip (*Kensen*), hand grip (*Tsuka*), and blade trajectory ribbon (*Hasuji* alignment).
- **🔄 State & Motion Lifecycle Tracker**: Finite State Machine (FSM) detecting transitions between *Kamae* $\rightarrow$ *Execution* $\rightarrow$ *Zanshin*.
- **⚡ Ki-Ken-Tai-Ichi Event Timing**: Millisecond-level synchronization detection measuring $\Delta t = |t_{\text{Ken}} - t_{\text{Tai}}|$ between sword apex impact and Fumikomi stomp landing.
- **📊 Dynamic Time Warping (DTW) Kinematic Matching**: Compares student joint angular velocities against high-dan Sensei reference strikes.
- **🎯 3-Phase Integrated Scoring**:
  $$\text{Total Score} = w_{\text{kamae}} \cdot S_{\text{kamae}} + w_{\text{exec}} \cdot S_{\text{exec}} + w_{\text{zanshin}} \cdot S_{\text{zanshin}}$$
- **🖥️ Real-time OpenCV HUD Dashboard**: Visual overlays displaying live skeleton feedback, trajectory ribbons, sync status gauges, and lifecycle state badges.

---

## 📂 Directory Structure Map

```text
Open-Kendo/
├── docs/
│   └── architecture.md         # Full system architecture & motion lifecycle specification
├── configs/
│   ├── default.yaml            # Pipeline settings (camera, pose backend, thresholds, lifecycle)
│   └── weights.yaml            # 3-Phase integrated scoring weights (Kamae, Execution, Zanshin)
├── data/
│   ├── raw/                    # Raw suburi/kihon training videos (.gitkeep)
│   ├── gold_standards/         # Master reference strikes (.npz) (.gitkeep)
│   └── outputs/                # Processed output videos and evaluation logs (.gitkeep)
├── open_kendo/                 # Core Python source package (Class shells & interfaces)
│   ├── __init__.py             # Package version definition
│   ├── perception/             # Pose estimation & Shinai tracking
│   │   ├── __init__.py
│   │   ├── base.py             # BasePoseEstimator, BaseObjectTracker, Dataclasses
│   │   ├── mediapipe_pose.py   # MediaPipe Pose Landmarker wrapper
│   │   ├── yolo_pose.py        # Ultralytics YOLO-Pose wrapper
│   │   └── shinai_tracker.py   # Shinai blade & tip tracking
│   ├── features/               # Kinematic feature calculations
│   │   ├── __init__.py
│   │   ├── kinematics.py       # Joint angles, spine tilt, center-of-mass (COM)
│   │   ├── trajectories.py     # Temporal buffering, smoothing & velocity peak
│   │   └── footwork.py         # Fumikomi stomp impact & Okuri-ashi analysis
│   ├── evaluation/             # Synchronization, Lifecycle & Scoring
│   │   ├── __init__.py
│   │   ├── lifecycle.py        # StateLifecycleTracker & StrikeLifecyclePhase FSM
│   │   ├── kamae.py            # Phase 1: Pre-Attack Kamae Evaluator
│   │   ├── kikentaichi.py      # Phase 2: Ki-Ken-Tai-Ichi synchronization evaluator
│   │   ├── zanshin.py          # Phase 3: Post-Attack Zanshin Evaluator
│   │   ├── dtw_matcher.py      # FastDTW kinematic profile matcher
│   │   ├── scorer.py           # KendoScorer: 3-Phase integrated score synthesis
│   │   └── models.py           # Evaluation dataclasses & score containers
│   ├── ui/                     # Visual rendering & HUD
│   │   ├── __init__.py
│   │   ├── drawer.py           # Skeleton and trajectory ribbon drawing
│   │   └── dashboard.py        # Real-time heads-up display (HUD)
│   └── utils/                  # System utilities
│       ├── __init__.py
│       ├── config.py           # YAML configuration loader
│       ├── logger.py           # Structured logging setup
│       └── video_io.py         # VideoReader & VideoWriter abstractions
├── scripts/
│   ├── run_live.py             # Main execution script for 3-phase real-time analysis
│   └── record_master.py        # Utility to record Sensei gold-standard forms
├── tests/                      # Unit test suite
│   ├── __init__.py
│   ├── test_lifecycle.py       # Tests for 3-phase lifecycle and evaluators
│   ├── test_perception.py
│   ├── test_features.py
│   ├── test_evaluation.py
│   └── test_utils.py
├── .gitignore                  # Git ignore rules
├── environment.yml             # Conda environment definition
├── pyproject.toml              # Build configuration & dev tools (ruff, black, pytest)
├── requirements.txt            # Python package dependencies
└── README.md                   # Project documentation
```

---

## 🚀 Quick Start Guide

### 1. Prerequisites

- Python 3.10 or 3.11
- Webcam or external high-speed USB camera (60+ FPS recommended for Fumikomi capture)
- CUDA-compatible GPU (Optional, recommended for YOLO-Pose backend)

### 2. Environment Setup

#### Option A: Using Python `venv` (Standard)

```bash
# Clone the repository
git clone https://github.com/UwU-coder-factorial/Open-Kendo.git
cd Open-Kendo

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On Windows:
.venv\Scripts\activate
# On Linux / macOS:
source .venv/bin/activate

# Upgrade pip & install dependencies (when ready to implement)
python -m pip install --upgrade pip
pip install -r requirements.txt
pip install -e .
```

#### Option B: Using Conda

```bash
# Create and activate conda environment
conda env create -f environment.yml
conda activate open-kendo

# Install package in editable mode
pip install -e .
```

### 3. Running Scripts

```bash
# Launch live analysis template from camera
python scripts/run_live.py

# Or analyze a pre-recorded instructional video
python scripts/run_live.py --config configs/default.yaml --source data/raw/sample2_kendo_basics_shomen_uchi.mp4
```

### 4. Running Tests

```bash
pytest -v tests/
```

---

## 🗺️ Project Roadmap

- [x] **Phase 1: Architecture Specification & Template Scaffold (Completed)**
  - [x] Establish 3-Phase State & Motion Lifecycle pipeline.
  - [x] Author comprehensive [docs/architecture.md](docs/architecture.md).
  - [x] Define abstract interfaces, dataclasses, and unit test suites.
- [ ] **Phase 2: Data Acquisition & Master Reference (Next)**
  - [ ] Acquire high-quality pedagogical Kihon / Suburi footage (Sensei instructional).
  - [ ] Annotate ground truth events ($t_{\text{kamae}}$, $t_{\text{apex}}$, $t_{\text{fumikomi}}$, $t_{\text{zanshin}}$).
- [ ] **Phase 3: Perception & Tracking Implementation**
  - [ ] Implement MediaPipe and YOLO-Pose keypoint normalization.
  - [ ] Implement Shinai blade & Kensen tip tracker.
- [ ] **Phase 4: Biomechanical Signal Processing & FSM Calibration**
  - [ ] Calibrate StateLifecycleTracker transition thresholds.
  - [ ] Calibrate Fumikomi vertical deceleration and Ki-Ken-Tai-Ichi $\Delta t$.
- [ ] **Phase 5: Integrated Evaluation & Dojo Deployment**
  - [ ] FastDTW alignment calibration.
  - [ ] Real-time OpenCV HUD with continuous visual feedback.

---

## 📜 License

This project is licensed under the [MIT License](LICENSE).