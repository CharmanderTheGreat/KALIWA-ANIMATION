# Kaliwa Animation (`KALIWA-ANIMATION`)

A programmatic 2D animation and audiovisual storytelling project built entirely in Python, rendered in Full HD (1080p), and deployed as an interactive web showcase via GitHub Pages.

**Live Showcase:** [Watch Kaliwa Animation](https://charmanderthegreat.github.io/KALIWA-ANIMATION/)

---

## Overview

**Kaliwa** is a code-driven animated short where every visual scene, character expression, camera movement, lighting effect, and synchronized audio cue is generated procedurally through Python scripts rather than traditional keyframe animation software.

The project combines frame-by-frame 2D graphics rendering with programmatic audio synthesis and mixing, compiling everything into a high-definition video (`Kaliwa_1080p.mp4`) playable directly in the browser.

---

## Key Features

* **Procedural Scene & Character Animation:** Frame-accurate character rigging, facial expressions, mouth states, physics-based motion curves, and dynamic camera tracking scripted in `story.py`.
* **Custom 2D Rendering Engine:** Built-in graphics pipeline (`engine.py`) supporting anti-aliased vector shapes, gradients, lighting cones, atmospheric weather/particle effects, and smooth scene transitions.
* **Synchronized Audio & SFX Pipeline:** Programmatic sound effects, background score integration, and timed audio cues managed via `audio.py`.
* **Automated HD Build System:** Modular build pipeline (`build.py` & `media.py`) that renders visual frames, compiles audio tracks, and muxes them into a final 1080p MP4 output.
* **Web Showcase Ready:** Includes a responsive, dark-themed HTML5 video player (`index.html`) configured for seamless playback on GitHub Pages.

---

## Project Structure

```text
KALIWA-ANIMATION/
├── index.html           # Web player interface hosted on GitHub Pages
├── Kaliwa_1080p.mp4     # Final rendered 1080p Full HD animation with audio
├── build.py             # Main build script orchestrating the full render pipeline
├── cli.py               # Command-line interface for running renders and previews
├── story.py             # Scene choreography, character logic, dialogue, and timeline cues
├── engine.py            # Core 2D graphics rendering engine and drawing primitives
├── audio.py             # Audio generation, sound effects (SFX), and track synchronization
├── media.py             # Video encoding, frame compilation, and FFmpeg media muxing
├── requirements.txt     # Python dependencies required to build the project
└── README.md            # Project documentation
```

---

## Tech Stack

* **Core Language:** Python 3.x
* **Graphics & Rendering:** Skia-Python / Pillow / NumPy (`engine.py`)
* **Audio & Media Processing:** FFmpeg / Wave / SciPy (`audio.py`, `media.py`)
* **Web Hosting:** HTML5, CSS3, GitHub Pages

---

## Getting Started (Local Build)

To inspect the code or render the animation locally on your machine:

### 1. Prerequisites
* **Python 3.10+** installed on your system
* **FFmpeg** installed and added to your system PATH (required for video and audio muxing)

### 2. Clone the Repository
```bash
git clone https://github.com/CharmanderTheGreat/KALIWA-ANIMATION.git
cd KALIWA-ANIMATION
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the Build Pipeline
Trigger a local render using either the CLI or the main build script:
```bash
python cli.py
# or
python build.py
```

---

## GitHub Pages Deployment

This repository is configured to serve `index.html` directly from the `main` branch root:

1. Navigate to **Settings > Pages** in the GitHub repository.
2. Under **Build and deployment**, set the source to **Deploy from a branch**.
3. Select the **`main`** branch and **`/ (root)`** folder, then click **Save**.
4. Access the live site at `[https://charmanderthegreat.github.io/KALIWA-ANIMATION/](https://charmanderthegreat.github.io/KALIWA-ANIMATION/)`.

---

## Author

**Albert Lawrence B. Robiñol**
* GitHub: [@CharmanderTheGreat](https://github.com/CharmanderTheGreat)