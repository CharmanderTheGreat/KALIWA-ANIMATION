"""Render one scene to an H.264 mp4 (piped raw frames). usage: render.py S3 out.mp4"""
import sys, subprocess, os
import numpy as np
import skia
from engine import *
import story

def render(name, out):
    fn = getattr(story, name.lower())
    dur = story.DUR[name]
    nfr = int(round(dur * FPS))
    st = Sim(story.SIMEV[name])
    K = float(os.environ.get('SCALE', '1'))
    OW, OH = int(W * K), int(H * K)
    surf = skia.Surface(OW, OH)
    c = surf.getCanvas()
    tmp = out + '.part.mp4'
    cmd = ['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'bgra', '-s', f'{OW}x{OH}', '-r', str(FPS),
           '-i', '-', '-c:v', 'libx264', '-crf', '18', '-preset', 'veryfast', '-pix_fmt', 'yuv420p', '-r', str(FPS),
           '-movflags', '+faststart', tmp]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for i in range(nfr):
        t = i / FPS
        c.resetMatrix()
        c.clear(skia.ColorBLACK)
        c.scale(K, K)
        fn(c, t, st)
        img = surf.makeImageSnapshot()
        arr = img.toarray(colorType=skia.kBGRA_8888_ColorType, alphaType=skia.kPremul_AlphaType)
        p.stdin.write(np.ascontiguousarray(arr).tobytes())
    p.stdin.close()
    rc = p.wait()
    if rc == 0:
        os.replace(tmp, out)
        print('done', name, nfr, 'frames')
    else:
        print('FAILED', name, rc)
        sys.exit(1)

if __name__ == '__main__':
    render(sys.argv[1], sys.argv[2])
