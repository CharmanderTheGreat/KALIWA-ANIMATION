import sys, skia, importlib
from engine import *
import story
def make_sim(name): return Sim(story.SIMEV[name])
def still(name, ts, out):
    fn = getattr(story, name.lower())
    st = make_sim(name)
    s = skia.Surface(W, H); c = s.getCanvas()
    for t in ts:
        fn(c, t, st)
        s.makeImageSnapshot().save(f'{out}_{name}_{t}.png', skia.kPNG)
if __name__ == '__main__':
    name = sys.argv[1]; ts = [float(x) for x in sys.argv[2:]]
    still(name, ts, 'st')
