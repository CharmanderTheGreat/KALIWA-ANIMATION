# Kaliwa Animation (`KALIWA-ANIMATION`)

A programmatic 2D animated short film built entirely in Python, rendered in Full HD (1080p), and presented through an interactive web screening room on GitHub Pages.

**Live Screening Room:** `[https://charmanderthegreat.github.io/KALIWA-ANIMATION/](https://charmanderthegreat.github.io/KALIWA-ANIMATION/)`

---

## Project Specifications

* **Assessment Task:** Individual Laboratory Activity — *Bringing Ideas to Life: Applying the 12 Principles of Animation*
* **Author:** Albert Lawrence B. Robiñol
* **Format & Resolution:** MP4 (H.264), 1920x1080 (16:9 Landscape), 2–3 Minutes Runtime

---

## Overview

**Kaliwa** is an original code-driven 2D animation where every scene transition, character rig, facial expression, camera movement, volumetric lighting effect, and synchronized audio cue is generated procedurally through Python scripts rather than traditional keyframe GUI tools.

The showcase site (`index.html`) delivers a theatrical screening interface featuring an animated title card intro, floating picture-in-picture playback on scroll, Full HD 1080p streaming, and a structured breakdown of how the 12 Principles of Animation are applied in the film.

---

## Application of the 12 Principles of Animation

| # | Principle | Implementation in *Kaliwa* |
| :--- | :--- | :--- |
| 01 | **Squash and Stretch** | Dynamic scale and vertical compression applied during impact landings, footsteps, and reactive character movements while preserving volume. |
| 02 | **Anticipation** | Preparatory crouch poses, posture shifts, and pre-action wind-ups signaling major character turns and leaps to the viewer. |
| 03 | **Staging** | Camera framing, headlight cones, rain contrast, and focal lighting direct attention cleanly to the narrative subject. |
| 04 | **Straight Ahead & Pose to Pose** | Key narrative poses are scripted along timeline intervals while atmospheric rain, light flicker, and particles evolve straight-ahead per frame. |
| 05 | **Follow Through & Overlapping Action** | Secondary elements and limb motions settle at staggered intervals after primary body momentum stops. |
| 06 | **Slow In and Slow Out** | Smoothstep and cubic easing interpolation curves govern camera pans, character acceleration, and scene fades. |
| 07 | **Arcs** | Trigonometric trajectories guide natural limb swings, head tilts, and airborne motion paths rather than rigid linear shifts. |
| 08 | **Secondary Action** | Subtle blinking, breathing cycles, brow movements, and environmental reflections reinforce emotion without distracting from dialogue. |
| 09 | **Timing** | Exact timestamp pacing controls dramatic pauses, dialogue delivery, and beat-matched sound cues across the film. |
| 10 | **Exaggeration** | Amplified facial expressions, widened eyes, and heightened silhouette reactions clarify emotional beats immediately. |
| 11 | **Solid Drawing** | Consistent character proportions, layered depth parallax, perspective road geometry, and grounded contact shadows maintain spatial depth. |
| 12 | **Appeal** | Cohesive nocturnal color palette, expressive character design, and clear visual storytelling create an engaging atmosphere. |

---

## Showcase Architecture

```text
KALIWA-ANIMATION/
├── index.html           # Interactive screening room & 12 Principles showcase (GitHub Pages)
├── .gitignore           # Excludes local production scripts and raw media files
└── README.md            # Project and assessment documentation
```

*(Note: Core Python rendering scripts and raw master video assets are excluded from the public repository to protect original source code and media integrity.)*

---

## Tech Stack

* **Animation Production:** Python 3.x (Procedural 2D Graphics, Audio Synthesis, FFmpeg Media Muxing)
* **Frontend Screening Room:** HTML5, CSS3, Vanilla JavaScript
* **Media Streaming & Hosting:** YouTube Embedded Player (1080p HD), GitHub Pages

---

## Author

**Albert Lawrence B. Robiñol**
* GitHub: `@CharmanderTheGreat` (`[https://github.com/CharmanderTheGreat](https://github.com/CharmanderTheGreat)`)