# Kaliwa - code-rendered animation (Python)

Ito ang source code ng animation. Lahat (drawing, galaw, tunog) ay ginagawa ng code.

## Kailangan
- Python 3.9 o mas bago
- FFmpeg (dapat nasa PATH, subukan: `ffmpeg -version`)
- Python packages: `pip install -r requirements.txt`

## Paano i-run
```
pip install -r requirements.txt
python build.py          # 1280x720  -> Kaliwa.mp4
python build.py --hd     # 1920x1080 -> Kaliwa_1080p.mp4 (mas mabagal)
```
Aabot ng mga 5-15 minuto depende sa CPU (mas maraming core, mas mabilis).

## Mga file
- `engine.py`  - drawing engine: characters, background, ulan, particles, easing
- `story.py`   - 8 scenes, timing, captions, sound-effect cues (dito mo babaguhin ang kuwento)
- `audio.py`   - synthesized music at sound effects
- `render.py`  - nagre-render ng isang scene: `python render.py S3 S3.mp4`
- `still.py`   - preview ng isang frame: `python still.py S4 14.9` (gumagawa ng PNG)
- `build.py`   - ginagawa ang lahat at pinagdudugtong
- `fonts/`     - Poppins (Open Font License)

## Mga madalas na gagalawin
- Dialogue/captions: `cap('S1', start, end, 'L', 'text')` sa `story.py`
- Credits: `CREDITS` list malapit sa dulo ng `story.py`
- Haba ng scenes: `DUR` sa taas ng `story.py`
