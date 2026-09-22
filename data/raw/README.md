# Open-Kendo Raw Benchmark Dataset Catalog

This directory contains the curated raw benchmark dataset for the **Open-Kendo** framework, organized according to the pedagogical 3-phase motion lifecycle (**Kamae**, **Suburi Men**, and **Men-uchi**).

---

## 1. Men-uchi (Forward Step Strike with Fumikomi-ashi)

Strikes involving forward driving footwork (*Okuri-ashi* / *Fumikomi-ashi*), blade cutting trajectory (*Hasuji*), and *Ki-Ken-Tai-Ichi* synchronicity.

| Filename                                         | Source / Author                 | Resolution & FPS            | Duration | Role & Recommended Segments                                                                                                                                                               |
| :----------------------------------------------- | :------------------------------ | :-------------------------- | :------- | :---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **`mokkei_part1_men_uchi_60fps.mp4`**    | Mokkei Kendo Research Institute | **1280x720 @ 60 FPS** | 6m 51s   | **Primary Men-uchi Benchmark**:• `0:45 - 1:20`: Full Men-uchi strike executed with Fumikomi.• `2:40 - 3:30`: Detailed breakdown of foot-sword synchronization at true 60 FPS. |
| **`sample1_kendo_highspeed_slowmo.mp4`** | Kendo High Speed Slow Motion    | 1440x1080 @ 30 FPS          | 5m 18s   | **Impact Apex Reference**:• `0:20 - 0:50`: High-speed slow motion showing blade flex (*Datotsu-bu*) and foot landing impact.                                                   |

---

## 2. Suburi Men (Stationary Overhead Strike Practice)

Stationary overhead cutting mechanics (*Tandoku Dosa*) without forward lunging steps, focusing on arm extension, posture stability, and wrist snap (*Tenouchi*).

| Filename                                           | Source / Author                 | Resolution & FPS   | Duration | Role & Recommended Segments                                                                                                                      |
| :------------------------------------------------- | :------------------------------ | :----------------- | :------- | :----------------------------------------------------------------------------------------------------------------------------------------------- |
| **`sample2_kendo_basics_shomen_uchi.mp4`** | Kendo Basics (Tandoku Dosa)     | 1920x1080 @ 30 FPS | 2m 37s   | **Primary Suburi Benchmark**:• `0:15 - 1:05`: Continuous stationary Shomen-uchi repetitions, clean studio lighting with full body view. |
| **`mokkei_kihon01_kamae_suburi.mp4`**      | Mokkei Kendo Research Institute | 1280x720 @ 30 FPS  | 7m 58s   | **Swing Arc & Extension Analysis**:• `4:00 - 6:00`: Suburi arm extension, shoulder relaxation, and Tenouchi grip mechanics.             |

---

## 3. Kamae (Phase 1: Pre-Attack Chūdan-no-kamae Fighting Stance)

Stored in directory: `data/raw/kamae/`

Curated high-resolution pedagogical reference images representing proper *Chūdan-no-kamae* (upright spine, balanced stance width, left heel slightly raised, sword tip threatening the throat, and left fist one fist-width in front of the navel).

| Filename                                          | Source / Reference                                                                                                          | Resolution                     | Pedagogical Focus & Technical Keypoints                                                                                                                                                                                        |
| :------------------------------------------------ | :-------------------------------------------------------------------------------------------------------------------------- | :----------------------------- | :----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **`kamae_koda_sensei_lateral_ideal.jpg`** | [Kendo Jidai: Koda Kunihide](https://kendojidai.com/2024/08/12/how-to-create-an-ideal-kamae-koda-kunihide/) (Hanshi 8th Dan) | **2000 x 1333**          | **Gold Standard Lateral View**:• Perfectly vertical spine alignment perpendicular to the floor.• Left heel slightly raised; balanced foot distance (~1 foot-length).• Shinai pointed upward at the opponent's throat. |
| **`kamae-front.jpg`**                     | [Kendo Jidai: Unity of Offense and Defense](https://kendojidai.com/2020/05/11/unity-of-offense-and-defense/)                 | **679 x 452**            | **Frontal Centerline Alignment**:• Shinai held along the vertical body midline.• Left fist placed directly in front of the navel.• Relaxed shoulders and balanced eye line (*Seigan*).                              |
| **`Screenshot 2026-09-17 090750.png`**    | [The Kendo Show: Fighting Stance (Kamae)](https://www.youtube.com/watch?v=0Hat0im3zt0)                                       | **2880 x 1622** (4K UHD) | **Instructional Breakdown Comparison**:• High-clarity stance demonstration comparing full-body posture, elbow angles, and footwork foundation.                                                                          |
| **`kamae_eiga_sensei_ideal.jpg`**         | [Kendo Jidai: Eiga Naoki](https://kendojidai.com/2024/08/19/how-to-create-an-ideal-kamae-eiga-naoki/) (Kyoshi 8th Dan)       | **2000 x 1333**          | **World Champion Kamae Form**:• Full Bogu attire demonstration showing upright posture, hip squareness, and forward spirit (*Kizeme*).                                                                                |
| **`kamae_hojo_sensei_ideal.jpg`**         | [Kendo Jidai: Hojo Masaomi](https://kendojidai.com/2024/09/09/how-to-create-an-ideal-kamae-hojo-masaomi/) (Kyoshi 8th Dan)   | **2000 x 1331**          | **Offensive Pressure Stance (*Seme Omote*)**:• High-level Kamae with firm centerline control and grounded left foot foundation.                                                                                       |
| **`kamae_okido_sensei_ideal.jpg`**        | [Kendo Jidai: Okido Satoru](https://kendojidai.com/2024/08/26/how-to-create-an-ideal-kamae-okido-satoru/) (Kyoshi 8th Dan)   | **2000 x 1331**          | **Full-body Posture Stability**:• Lateral and semi-frontal view illustrating core stability and correct grip pressure.                                                                                                  |

---

## 4. Machine-Readable Metadata Manifest

The complete metadata and frame extraction parameters are defined in:
[`data/raw/dataset_manifest.yaml`](dataset_manifest.yaml)
