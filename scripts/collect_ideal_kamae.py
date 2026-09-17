"""Script to download pristine Kamae reference data from user specified sources:
1. Kendo Jidai - Koda Kunihide (Hanshi 8-dan)
2. YouTube 4sMu6-TYhS4 - Seigan no Kamae
3. Canonical Chudan-no-Kamae diagram
"""

import json
import urllib.request
from pathlib import Path
import cv2

KAMAE_DIR = Path("data/raw/kamae")
KAMAE_DIR.mkdir(parents=True, exist_ok=True)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
}

# ------------------------------------------------------------------------------
# 1. Download Koda Kunihide Sensei (Hanshi 8-dan) Kamae Photos from Kendo Jidai
# ------------------------------------------------------------------------------
koda_images = [
    (
        "https://kendojidai.com/wp-content/uploads/2024/08/kouda-14.jpg",
        "kamae_koda_sensei_lateral_ideal.jpg",
        "Koda Kunihide (Hanshi 8-dan) - Ideal Kamae Lateral Profile",
    ),
    (
        "https://kendojidai.com/wp-content/uploads/2024/08/kouda-01.jpg",
        "kamae_koda_sensei_frontal_ideal.jpg",
        "Koda Kunihide (Hanshi 8-dan) - Ideal Kamae Frontal Alignment",
    ),
    (
        "https://kendojidai.com/wp-content/uploads/2019/12/koda-l2-12.jpg",
        "kamae_koda_sensei_grip_tenouchi.jpg",
        "Koda Kunihide - Hand Placement & Tenouchi Grip Detail",
    ),
]

print("--- Downloading Kendo Jidai Koda Sensei Photos ---")
for url, filename, desc in koda_images:
    dest = KAMAE_DIR / filename
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req) as resp:
            data = resp.read()
            with open(dest, "wb") as f:
                f.write(data)
            print(f"[OK] Downloaded: {filename} ({len(data)} bytes)")
    except Exception as e:
        # Fallback to scaled version if original not direct
        fallback_url = url.replace(".jpg", "-1080x720.jpg").replace("01-", "01-683x1024.")
        try:
            req = urllib.request.Request(fallback_url, headers=HEADERS)
            with urllib.request.urlopen(req) as resp:
                data = resp.read()
                with open(dest, "wb") as f:
                    f.write(data)
                print(f"[OK Fallback] Downloaded: {filename} ({len(data)} bytes)")
        except Exception as e2:
            print(f"[ERR] Failed {filename}: {e2}")

# ------------------------------------------------------------------------------
# 2. Extract Key Frames from YouTube: Seigan no Kamae (4sMu6-TYhS4)
# ------------------------------------------------------------------------------
print("\n--- Extracting Frames from 'Seigan no Kamae' (4sMu6-TYhS4) ---")
import subprocess
import shutil

video_seigan = Path("data/raw/seigan_kamae_masakatsuaiki.mp4")
if not video_seigan.exists():
    print("Downloading video 4sMu6-TYhS4...")
    cmd = [
        "python", "-m", "yt_dlp", "--js-runtimes", "node",
        "-f", "bestvideo[ext=mp4]/best[ext=mp4]/18",
        "https://www.youtube.com/watch?v=4sMu6-TYhS4",
        "-o", str(video_seigan)
    ]
    subprocess.run(cmd, check=True)

if video_seigan.exists():
    cap = cv2.VideoCapture(str(video_seigan))
    fps = cap.get(cv2.CAP_PROP_FPS) or 29.97
    
    # Selected moments demonstrating precise Kamae:
    # 25s: Upright standing Kamae front
    # 58s: Side/lateral stance showing spine and footwork
    # 115s: Centerline throat alignment
    # 185s: Detailed body posture
    seigan_timestamps = [
        (25.0, "kamae_seigan_front_posture.jpg"),
        (58.0, "kamae_seigan_lateral_stance.jpg"),
        (115.0, "kamae_seigan_centerline_aim.jpg"),
        (185.0, "kamae_seigan_full_body_kamae.jpg"),
    ]
    
    for sec, out_name in seigan_timestamps:
        frame_idx = int(sec * fps)
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
        ret, frame = cap.read()
        if ret and frame is not None:
            out_file = KAMAE_DIR / out_name
            cv2.imwrite(str(out_file), frame, [cv2.IMWRITE_JPEG_QUALITY, 95])
            print(f"[OK] Extracted: {out_name} at {sec}s")
    cap.release()

# ------------------------------------------------------------------------------
# 3. Canonical Technical Anatomical Diagrams of Chudan-no-Kamae
# ------------------------------------------------------------------------------
print("\n--- Downloading Canonical Technical Kamae Diagrams ---")
diagrams = [
    (
        "https://upload.wikimedia.org/wikipedia/commons/6/61/FENCING_AT_AN_AGRICULTURAL_SCHOOL.jpg",
        "kamae_diagram_reference_01.jpg",
    ),
    (
        "https://www.kendo-guide.com/images/chudan_no_kamae_side_view.jpg",
        "kamae_diagram_side_view.jpg",
    ),
    (
        "https://www.kendo-guide.com/images/chudan_no_kamae_front_view.jpg",
        "kamae_diagram_front_view.jpg",
    ),
]

for url, filename in diagrams:
    dest = KAMAE_DIR / filename
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req) as resp:
            data = resp.read()
            with open(dest, "wb") as f:
                f.write(data)
            print(f"[OK] Diagram downloaded: {filename}")
    except Exception as e:
        print(f"[NOTE] Diagram {filename} direct URL skip: {e}")

print("\nKamae data collection completed!")
