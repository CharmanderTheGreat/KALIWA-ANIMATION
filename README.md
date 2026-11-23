# Kaliwa Animation (`KALIWA-ANIMATION`)

A programmatic 2D animated short film built entirely in Python, rendered in Full HD (1080p), and presented through an interactive web screening room on GitHub Pages.

**Live Screening Room:** [Watch Kaliwa Animation](https://charmanderthegreat.github.io/KALIWA-ANIMATION/)

---

## Academic Context

* **Assessment Task:** Individual Laboratory Activity — *Bringing Ideas to Life: Applying the 12 Principles of Animation*
* **Author:** Albert Lawrence B. Robiñol
* **Program & Section:** BSIT 3-2
* **Format & Resolution:** MP4 (H.264), 1920x1080 (16:9 Landscape), 2–3 Minutes Runtime

---

## Overview

**Kaliwa** is an original code-driven 2D animation where every scene transition, character rig, facial expression, camera movement, volumetric lighting effect, and synchronized audio cue is generated procedurally through Python scripts rather than traditional keyframe GUI tools.

The showcase site (`index.html`) provides a theatrical screening interface with an animated title card intro, full HD playback, and an interactive breakdown mapping the 12 Principles of Animation to the project's underlying codebase.

---

## Application of the 12 Principles of Animation

| # | Principle | Module | Implementation in *Kaliwa* |
| :--- | :--- | :--- | :--- |
| 01 | **Squash and Stretch** | `story.py` | Dynamic scale and vertical compression applied during impact landings, footsteps, and reactive character movements while preserving volume. |
| 02 | **Anticipation** | `story.py` | Preparatory crouch poses, posture shifts, and pre-action wind-ups signaling major character turns and leaps to the viewer. |
| 03 | **Staging** | `engine.py` | Camera framing, headlight cones, rain contrast, and focal lighting direct attention cleanly to the narrative subject. |
| 04 | **Straight Ahead & Pose to Pose** | `story.py`, `engine.py` | Key narrative poses are scripted along timeline intervals while atmospheric rain, light flicker, and particles evolve straight-ahead per frame. |
| 05 | **Follow Through & Overlapping Action** | `story.py` | Secondary elements and limb motions settle at staggered intervals after primary body momentum stops. |
| 06 | **Slow In and Slow Out** | `engine.py` | Smoothstep and cubic easing interpolation curves govern camera pans, character acceleration, and scene fades. |
| 07 | **Arcs** | `story.py` | Trigonometric trajectories guide natural limb swings, head tilts, and airborne motion paths rather than rigid linear shifts. |
| 08 | **Secondary Action** | `story.py` | Subtle blinking, breathing cycles, brow movements, and environmental reflections reinforce emotion without distracting from dialogue. |
| 09 | **Timing** | `build.py`, `audio.py` | Exact timestamp pacing controls dramatic pauses, dialogue delivery, and beat-matched sound cues across the film. |
| 10 | **Exaggeration** | `story.py` | Amplified facial expressions, widened eyes, and heightened silhouette reactions clarify emotional beats immediately. |
| 11 | **Solid Drawing** | `engine.py` | Consistent character proportions, layered depth parallax, perspective road geometry, and grounded contact shadows maintain spatial depth. |
| 12 | **Appeal** | `story.py`, `engine.py` | Cohesive nocturnal color palette, expressive character design, and clear visual storytelling create an engaging atmosphere. |

---

## Project Structure

```text
KALIWA-ANIMATION/
├── index.html           # Interactive screening room & 12 Principles showcase (GitHub Pages)
├── Kaliwa_1080p.mp4     # Final rendered 1920x1080 Full HD H.264 animated video
├── build.py             # Main build orchestrator compiling frames and audio into final video
├── cli.py               # Command-line interface for rendering scenes and previews
├── story.py             # Scene choreography, character state machines, dialogue, and timeline cues
├── engine.py            # Custom 2D graphics rendering engine, lighting, and drawing primitives
├── audio.py             # Procedural SFX synthesis, score mixing, and timestamp synchronization
├── media.py             # Frame encoding and FFmpeg audio-video muxing pipeline
├── requirements.txt     # Python package dependencies
└── README.md            # Project and assessment documentation
```

---

## Tech Stack

* **Programming Language:** Python 3.x
* **2D Graphics & Math:** Skia-Python, Pillow, NumPy (`engine.py`)
* **Audio & Video Muxing:** FFmpeg, Wave, SciPy (`audio.py`, `media.py`)
* **Frontend Showcase:** HTML5, CSS3, Vanilla JavaScript (`index.html`)
* **Hosting:** GitHub Pages

---

## Local Build Instructions

### 1. Prerequisites
* **Python 3.10+**
* **FFmpeg** installed and available in your system PATH

### 2. Clone and Install
```bash
git clone https://github.com/CharmanderTheGreat/KALIWA-ANIMATION.git
cd KALIWA-ANIMATION
pip install -r requirements.txt
```

### 3. Render the Animation
```bash
python cli.py
# or
python build.py
```

---

## Author

**Albert Lawrence B. Robiñol** (BSIT 3-2)
* GitHub: [@CharmanderTheGreat](https://github.com/CharmanderTheGreat)