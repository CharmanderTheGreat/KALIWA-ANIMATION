"""Build the whole film: python build.py [--hd]   ->  Kaliwa.mp4 in this folder.
--hd renders 1920x1080 (slower), default is 1280x720."""
import os, sys, subprocess
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
HD = '--hd' in sys.argv
OUT = os.path.join(HERE, 'build_hd' if HD else 'build_720')
os.makedirs(OUT, exist_ok=True)
SCENES = ['S0', 'S1', 'S2', 'S3', 'S4', 'S5', 'S6', 'S7']
env = dict(os.environ, SCALE='1.5' if HD else '1')

def run_scene(s):
    # each scene is rendered by its own process so scenes can be rendered in parallel
    subprocess.run([sys.executable, os.path.join(HERE, 'render.py'), s, os.path.join(OUT, s + '.mp4')],
                   check=True, env=env, cwd=HERE)

workers = max(1, min(4, (os.cpu_count() or 2) // 1))
with ThreadPoolExecutor(workers) as ex:
    list(ex.map(run_scene, SCENES))

# synthesize the soundtrack
wav = os.path.join(OUT, 'audio.wav')
subprocess.run([sys.executable, os.path.join(HERE, 'audio.py'), wav], check=True, cwd=HERE)

# join scenes (no re-encode) and add the sound
lst = os.path.join(OUT, 'list.txt')
with open(lst, 'w') as f:
    for s in SCENES:
        f.write(f"file '{s}.mp4'\n")
joined = os.path.join(OUT, 'video_only.mp4')
subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', lst, '-c', 'copy', joined], check=True)
final = os.path.join(HERE, 'Kaliwa_1080p.mp4' if HD else 'Kaliwa.mp4')
subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', joined, '-i', wav, '-map', '0:v', '-map', '1:a',
                '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-shortest', '-movflags', '+faststart', final], check=True)
print('DONE ->', final)
