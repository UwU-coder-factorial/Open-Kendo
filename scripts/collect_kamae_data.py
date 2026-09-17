"""Script to extract and collect Kamae image dataset for Phase 1 analysis."""

import json
import urllib.request
from pathlib import Path
import cv2

DATA_RAW = Path("data/raw")
KAMAE_DIR = DATA_RAW / "kamae"
KAMAE_DIR.mkdir(parents=True, exist_ok=True)

# Part 1: Extract 6 pristine frames from Mokkei Kihon #01 video
video_path = DATA_RAW / "mokkei_kihon01_kamae_suburi.mp4"
if video_path.exists():
    cap = cv2.VideoCapture(str(video_path))
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0

    # Key moments in video demonstrating Kamae:
    # 52s: Front-facing Chudan Kamae
    # 78s: Lateral / 45-deg Kamae showing foot spacing & heel
    # 105s: Hand & Tsuka grip positioning at navel
    # 135s: Spine & posture alignment check
    # 175s: Full body Kamae preparation
    # 210s: Kamae to Suburi transition stance
    timestamps_sec = [52.0, 78.0, 105.0, 135.0, 175.0, 210.0]

    for idx, sec in enumerate(timestamps_sec, start=1):
        frame_id = int(sec * fps)
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_id)
        ret, frame = cap.read()
        if ret and frame is not None:
            out_file = KAMAE_DIR / f"kamae_mokkei_sensei_{idx:02d}.jpg"
            cv2.imwrite(str(out_file), frame, [cv2.IMWRITE_JPEG_QUALITY, 95])
            print(f"Extracted: {out_file.name} (at {sec:.1f}s)")
    cap.release()

# Part 2: Fetch 4 public reference images of Kendo Chudan Kamae from Wikimedia Commons
wikimedia_files = [
    ("Kendo_10.jpg", "kamae_wikimedia_chudan_01.jpg"),
    ("Kendo_12.jpg", "kamae_wikimedia_chudan_02.jpg"),
    ("FENCING_AT_AN_AGRICULTURAL_SCHOOL.jpg", "kamae_wikimedia_historical_03.jpg"),
]

headers = {"User-Agent": "OpenKendoBot/1.0 (academic research; contact@openkendo.org)"}

for wm_name, local_name in wikimedia_files:
    try:
        api_url = (
            f"https://commons.wikimedia.org/w/api.php?action=query&titles=File:{wm_name}"
            f"&prop=imageinfo&iiprop=url&format=json"
        )
        req = urllib.request.Request(api_url, headers=headers)
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            pages = data.get("query", {}).get("pages", {})
            for page in pages.values():
                if "imageinfo" in page and len(page["imageinfo"]) > 0:
                    img_url = page["imageinfo"][0]["url"]
                    img_req = urllib.request.Request(img_url, headers=headers)
                    with urllib.request.urlopen(img_req) as img_resp:
                        img_data = img_resp.read()
                        out_path = KAMAE_DIR / local_name
                        with open(out_path, "wb") as f:
                            f.write(img_data)
                        print(f"Downloaded: {local_name} from {img_url}")
    except Exception as e:
        print(f"Could not download {wm_name}: {e}")

print(f"\nAll Kamae images collected in: {KAMAE_DIR.resolve()}")
