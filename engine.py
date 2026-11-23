"""Drawing engine for 'Si Kaliwa' - skia based 2D renderer (English comments)."""
import math, random
import skia

W, H, FPS = 1280, 720, 30
GY = 598          # street level (where hops land)
STEP_Y = 566      # top of the doorstep
import os
_HERE = os.path.dirname(os.path.abspath(__file__))
FONT_B = os.path.join(_HERE, 'fonts', 'Poppins-Bold.ttf')    # bundled font (Open Font License)
FONT_M = os.path.join(_HERE, 'fonts', 'Poppins-Medium.ttf')

# ---------------------------------------------------------------- helpers
def col(c, a=255):
    return skia.Color(int(c[0]), int(c[1]), int(c[2]), int(max(0, min(255, a))))

def mix(a, b, t):
    return tuple(a[i] + (b[i] - a[i]) * t for i in range(len(a)))

def clamp(x, lo=0.0, hi=1.0):
    return lo if x < lo else hi if x > hi else x

def lerp(a, b, t):
    return a + (b - a) * t

def smooth(t):
    t = clamp(t)
    return t * t * (3 - 2 * t)

def ease_io(t):          # slow in / slow out (cubic)
    t = clamp(t)
    return 4 * t ** 3 if t < .5 else 1 - (-2 * t + 2) ** 3 / 2

def ease_in(t):
    return clamp(t) ** 3

def ease_out(t):
    return 1 - (1 - clamp(t)) ** 3

def out_back(t, s=1.9):
    t = clamp(t) - 1
    return t * t * ((s + 1) * t + s) + 1

def spring(tau, f=3.0, d=6.0):
    """0 -> 1 with overshoot (follow through)."""
    if tau <= 0:
        return 0.0
    return 1 - math.exp(-d * tau) * math.cos(2 * math.pi * f * tau)

def kf(t, pts, ease=ease_io):
    """Piecewise keyframe interpolation. pts = [(time, value), ...]; values: number or tuple."""
    if t <= pts[0][0]:
        return pts[0][1]
    for i in range(len(pts) - 1):
        t0, v0 = pts[i]
        t1, v1 = pts[i + 1]
        if t <= t1:
            u = ease((t - t0) / (t1 - t0)) if t1 > t0 else 1
            if isinstance(v0, tuple):
                return mix(v0, v1, u)
            return v0 + (v1 - v0) * u
    return pts[-1][1]

def fill(c, a=255, shader=None):
    p = skia.Paint()
    p.setAntiAlias(True)
    p.setColor(col(c, a))
    if shader is not None:
        p.setShader(shader)
    return p

def stroke(c, w, a=255):
    p = skia.Paint()
    p.setAntiAlias(True)
    p.setColor(col(c, a))
    p.setStyle(skia.Paint.kStroke_Style)
    p.setStrokeWidth(w)
    p.setStrokeCap(skia.Paint.kRound_Cap)
    p.setStrokeJoin(skia.Paint.kRound_Join)
    return p

def lin(x0, y0, x1, y1, c0, c1, a0=255, a1=255):
    return skia.GradientShader.MakeLinear([(x0, y0), (x1, y1)], [col(c0, a0), col(c1, a1)])

def rad(cx, cy, r, c0, c1, a0=255, a1=0):
    return skia.GradientShader.MakeRadial((cx, cy), r, [col(c0, a0), col(c1, a1)])

_fonts = {}
def font(size, bold=True):
    k = (int(size), bold)
    if k not in _fonts:
        tf = skia.Typeface.MakeFromFile(FONT_B if bold else FONT_M)
        _fonts[k] = skia.Font(tf, size)
    return _fonts[k]

def text(c, s, x, y, size, color=(255, 255, 255), a=255, align='center', bold=True, outline=None, ow=6):
    f = font(size, bold)
    w = f.measureText(s)
    if align == 'center':
        x -= w / 2
    elif align == 'right':
        x -= w
    if outline is not None:
        c.drawString(s, x, y, f, stroke(outline, ow, a))
    c.drawString(s, x, y, f, fill(color, a))
    return w

def R(x, y, w, h):
    return skia.Rect.MakeXYWH(x, y, w, h)

def rrect(c, x, y, w, h, r, paint):
    c.drawRoundRect(R(x, y, w, h), r, r, paint)

def oval(c, cx, cy, rx, ry, paint):
    c.drawOval(R(cx - rx, cy - ry, 2 * rx, 2 * ry), paint)

def poly(pts, close=True):
    p = skia.Path()
    p.moveTo(*pts[0])
    for q in pts[1:]:
        p.lineTo(*q)
    if close:
        p.close()
    return p

# ---------------------------------------------------------------- palettes
PALS = {
    'dusk':  dict(sky_top=(255, 132, 98), sky_bot=(255, 214, 140), far=(200, 112, 112), palm=(120, 62, 84),
                  road=(112, 102, 112), walk=(196, 176, 164), wall=(255, 228, 192), roof=(196, 84, 72),
                  door=(142, 82, 52), dark=0, stars=0),
    'storm': dict(sky_top=(62, 72, 98), sky_bot=(132, 144, 162), far=(84, 94, 112), palm=(48, 58, 74),
                  road=(76, 82, 94), walk=(126, 132, 142), wall=(206, 200, 192), roof=(120, 70, 68),
                  door=(100, 66, 48), dark=45, stars=0),
    'night': dict(sky_top=(10, 14, 40), sky_bot=(32, 42, 86), far=(26, 32, 64), palm=(14, 20, 42),
                  road=(34, 38, 58), walk=(62, 68, 92), wall=(110, 114, 142), roof=(70, 52, 76),
                  door=(66, 48, 44), dark=95, stars=1),
    'dawn':  dict(sky_top=(250, 150, 150), sky_bot=(255, 224, 162), far=(206, 124, 142), palm=(112, 62, 92),
                  road=(98, 98, 118), walk=(176, 158, 164), wall=(255, 222, 198), roof=(190, 88, 86),
                  door=(142, 86, 58), dark=12, stars=0),
    'day':   dict(sky_top=(108, 190, 255), sky_bot=(255, 244, 208), far=(146, 176, 214), palm=(52, 124, 92),
                  road=(98, 100, 112), walk=(204, 200, 194), wall=(255, 240, 210), roof=(212, 94, 82),
                  door=(152, 94, 58), dark=0, stars=0),
}

def pal_mix(a, b, t):
    A, B = PALS[a], PALS[b]
    out = {}
    for k in A:
        out[k] = mix(A[k], B[k], t) if isinstance(A[k], tuple) else A[k] + (B[k] - A[k]) * t
    return out

# (absolute time, palette name) keyframes for the whole film
PAL_KEYS = [(0, 'dusk'), (13, 'dusk'), (27, 'storm'), (76, 'storm'), (98, 'night'), (130, 'night'),
            (140, 'dawn'), (147, 'day')]

def pal_at(T):
    if T <= PAL_KEYS[0][0]:
        return pal_mix(PAL_KEYS[0][1], PAL_KEYS[0][1], 0)
    for i in range(len(PAL_KEYS) - 1):
        t0, a = PAL_KEYS[i]
        t1, b = PAL_KEYS[i + 1]
        if T <= t1:
            return pal_mix(a, b, ease_io((T - t0) / (t1 - t0)))
    return pal_mix(PAL_KEYS[-1][1], PAL_KEYS[-1][1], 0)

# ---------------------------------------------------------------- the slippers
BLUE, BLUE_L, BLUE_D = (82, 182, 236), (150, 222, 252), (36, 98, 152)
OUT = (22, 52, 92)
YEL, YEL_D = (255, 200, 52), (206, 140, 12)

def _foot():
    p = skia.Path()
    p.moveTo(-34, -6)
    p.cubicTo(-46, -6, -47, -22, -45, -52)
    p.cubicTo(-44, -96, -62, -120, -60, -150)
    p.cubicTo(-58, -182, -30, -192, 0, -192)
    p.cubicTo(30, -192, 58, -182, 60, -150)
    p.cubicTo(62, -120, 44, -96, 45, -52)
    p.cubicTo(47, -22, 46, -6, 34, -6)
    p.cubicTo(20, 3, -20, 3, -34, -6)
    p.close()
    return p

FOOT = _foot()
_FOOT_SH = None

def shadow(c, x, gy, air=0.0, s=0.78, w=1.0, a=80):
    k = 1 / (1 + max(0, air) / 170)
    rx, ry = 52 * s * w * k, 9 * s * k
    oval(c, x, gy + 4, rx, ry, fill((0, 0, 0), a * k))

def blink_open(t, period=3.4, seed=0.0):
    ph = (t + seed) % period
    if ph < 0.15:
        return 1 - math.sin(math.pi * ph / 0.15)
    return 1.0

def _eye(c, cx, cy, f, side, kind):
    es, op = f['es'], f['open']
    rx, ry = 15 * es, 17 * es * op
    if op < 0.14:      # closed eye = smile arc
        pth = skia.Path()
        pth.moveTo(cx - 13, cy + 1)
        pth.quadTo(cx, cy + (-12 if f.get('happyclose') else 10), cx + 13, cy + 1)
        c.drawPath(pth, stroke(OUT, 4))
        return
    oval(c, cx, cy, rx, ry, fill((255, 255, 255)))
    oval(c, cx, cy, rx, ry, stroke(OUT, 3))
    pr = 7.5 * min(1.25, es)
    px = clamp(f['px'], -1, 1) * (rx - pr - 1)
    py = clamp(f['py'], -1, 1) * max(0, ry - pr - 1)
    c.save()
    c.clipPath(_oval_path(cx, cy, rx - 1.2, ry - 1.2), skia.ClipOp.kIntersect, True)
    oval(c, cx + px, cy + py, pr, pr * min(1, max(.6, op + .2)), fill((26, 30, 46)))
    oval(c, cx + px - 2.5, cy + py - 3, 2.6, 2.6, fill((255, 255, 255)))
    c.restore()
    if kind == 'R':    # Kanan has lashes
        for dx, dy in ((-1, -1), (0.2, -1.5)):
            c.drawLine(cx + side * (rx - 1) + dx * 0, cy - ry + 3, cx + side * (rx + 7), cy - ry - 3 + dy,
                       stroke(OUT, 3))

def _oval_path(cx, cy, rx, ry):
    p = skia.Path()
    p.addOval(R(cx - rx, cy - ry, 2 * rx, 2 * ry))
    return p

def _mouth(c, f):
    m, mo = f['mouth'], f['mo']
    y = -46
    if m == 'smile':
        p = skia.Path(); p.moveTo(-14, y - 2); p.quadTo(0, y + 12, 14, y - 2)
        c.drawPath(p, stroke(OUT, 4))
    elif m == 'big':
        p = skia.Path(); p.moveTo(-18, y - 4); p.quadTo(0, y + 30 * (0.5 + 0.5 * mo), 18, y - 4); p.close()
        c.drawPath(p, fill((120, 34, 56))); c.drawPath(p, stroke(OUT, 3.5))
    elif m == 'open':
        ry = 5 + 17 * mo
        oval(c, 0, y + ry * .35, 13, ry, fill((120, 34, 56)))
        oval(c, 0, y + ry * .35 + ry * .45, 8, ry * .42, fill((235, 110, 130)))
        oval(c, 0, y + ry * .35, 13, ry, stroke(OUT, 3.5))
    elif m == 'o':
        r = 5 + 5 * mo
        oval(c, 0, y + 2, r, r * 1.1, fill((120, 34, 56))); oval(c, 0, y + 2, r, r * 1.1, stroke(OUT, 3.5))
    elif m == 'sad':
        p = skia.Path(); p.moveTo(-13, y + 6); p.quadTo(0, y - 8, 13, y + 6)
        c.drawPath(p, stroke(OUT, 4))
    elif m == 'wobble':
        p = skia.Path(); p.moveTo(-15, y + 2)
        p.cubicTo(-8, y - 6, -3, y + 8, 0, y + 1); p.cubicTo(3, y - 6, 8, y + 8, 15, y + 2)
        c.drawPath(p, stroke(OUT, 4))
    elif m == 'grit':
        rrect(c, -15, y - 6, 30, 12, 4, fill((255, 255, 255)))
        rrect(c, -15, y - 6, 30, 12, 4, stroke(OUT, 3.5))
        for i in (-5, 5):
            c.drawLine(i, y - 6, i, y + 6, stroke(OUT, 2))
    else:  # flat
        c.drawLine(-10, y, 10, y, stroke(OUT, 4))

def slipper(c, x, y, s=0.78, rot=0, sx=1, sy=1, pivot=0, kind='L', face=None, lag=(0, 0), flip=1,
            alpha=255, extra=None):
    """Draw a slipper character. (x,y) = base centre. kind 'L' = Kaliwa, 'R' = Kanan."""
    f = dict(open=1, es=1, px=0, py=0, brow=0, mouth='smile', mo=0, blush=1, happyclose=False)
    if face:
        f.update(face)
    if alpha < 255:
        c.saveLayerAlpha(None, int(alpha))
    else:
        c.save()
    c.translate(x, y)
    c.translate(0, -pivot * s)
    c.rotate(rot)
    c.translate(0, pivot * s)
    c.scale(s * flip * sx, s * sy)
    # thickness (sole edge)
    c.save(); c.translate(3, 10); c.drawPath(FOOT, fill(BLUE_D)); c.restore()
    c.drawPath(FOOT, fill(BLUE, shader=lin(-50, -192, 44, 0, BLUE_L, BLUE)))
    hl = skia.Path(); hl.moveTo(-41, -62); hl.cubicTo(-40, -100, -52, -124, -50, -152)
    c.drawPath(hl, stroke((255, 255, 255), 6, 90))
    c.drawPath(FOOT, stroke(OUT, 4.5))
    # strap (yellow Y)
    for sd in (-1, 1):
        sp = skia.Path(); sp.moveTo(sd * 50, -116); sp.quadTo(sd * 28, -150, 0, -160)
        c.drawPath(sp, stroke(YEL_D, 21));
    for sd in (-1, 1):
        sp = skia.Path(); sp.moveTo(sd * 50, -116); sp.quadTo(sd * 28, -150, 0, -160)
        c.drawPath(sp, stroke(YEL, 14))
    c.drawCircle(0, -160, 11, fill(YEL)); c.drawCircle(0, -160, 11, stroke(YEL_D, 3.5))
    # tuft / flower follow-through (lags behind the motion)
    lx = clamp(lag[0], -30, 30); ly = clamp(lag[1], -26, 26)
    if kind == 'L':
        for i, (ox, k) in enumerate(((-5, 0.8), (0, 1.0), (5, 0.9))):
            tp = skia.Path(); tp.moveTo(ox, -168)
            tp.quadTo(ox + lx * .35 * k + ox, -184 + ly * .4 * k, ox * 2.2 + lx * k, -193 + ly * k - 2 * (1 - abs(i - 1)))
            c.drawPath(tp, stroke(OUT, 4.5))
    else:
        fx, fy = 12 + lx * .8, -184 + ly * .8
        tp = skia.Path(); tp.moveTo(0, -168); tp.quadTo(4 + lx * .3, -178, fx, fy + 4)
        c.drawPath(tp, stroke((60, 140, 70), 4))
        for k in range(5):
            a = k * 2 * math.pi / 5 + 0.3 + lx * .02
            c.drawCircle(fx + 8 * math.cos(a), fy + 8 * math.sin(a), 6.5, fill((255, 120, 170)))
            c.drawCircle(fx + 8 * math.cos(a), fy + 8 * math.sin(a), 6.5, stroke((190, 60, 110), 1.8))
        c.drawCircle(fx, fy, 5, fill((255, 226, 90)))
    # face
    if f['blush']:
        oval(c, -34, -54, 8, 5, fill((255, 120, 150), 120)); oval(c, 34, -54, 8, 5, fill((255, 120, 150), 120))
    _eye(c, -20, -80, f, -1, kind)
    _eye(c, 20, -80, f, 1, kind)
    b = f['brow']
    if b:
        by = -80 - 17 * f['es'] - 5
        c.drawLine(-32, by, -9, by - 9 * b, stroke(OUT, 4.2))
        c.drawLine(32, by, 9, by - 9 * b, stroke(OUT, 4.2))
    _mouth(c, f)
    if extra:
        extra(c)
    c.restore()

# ---------------------------------------------------------------- particles (frame-by-frame simulation)
class Sim:
    """Straight-ahead particle simulation: each frame is computed from the previous one."""
    def __init__(self, events):
        self.events = sorted(events, key=lambda e: e[0])
        self.i = 0
        self.t = 0.0
        self.ps = []
        self.rng = random.Random(7)

    def spawn(self, kind, x, y, n=1, **kw):
        r = self.rng
        for _ in range(n):
            if kind == 'splash':
                a = r.uniform(-2.6, -0.55) if not kw.get('up') else r.uniform(-2.2, -0.9)
                sp = r.uniform(140, 420) * kw.get('power', 1)
                self.ps.append(dict(k='drop', x=x + r.uniform(-10, 10), y=y, vx=math.cos(a) * sp, vy=math.sin(a) * sp,
                                    life=r.uniform(.5, .9), age=0, sz=r.uniform(3, 7), gy=kw.get('gy', 9999)))
            elif kind == 'note':
                self.ps.append(dict(k='note', x=x + r.uniform(-14, 14), y=y, vx=r.uniform(-10, 10), vy=-r.uniform(45, 80),
                                    life=1.8, age=0, sz=r.uniform(.8, 1.2), ph=r.uniform(0, 6), col=kw.get('col', (255, 255, 255))))
            elif kind == 'heart':
                a = r.uniform(-2.5, -0.65); sp = r.uniform(60, 190)
                self.ps.append(dict(k='heart', x=x + r.uniform(-20, 20), y=y + r.uniform(-10, 10), vx=math.cos(a) * sp, vy=math.sin(a) * sp,
                                    life=r.uniform(1.4, 2.2), age=0, sz=r.uniform(7, 14), ph=r.uniform(0, 6)))
            elif kind == 'z':
                self.ps.append(dict(k='z', x=x, y=y, vx=18, vy=-34, life=2.2, age=0, sz=1 + 0.25 * self.rng.random(), ph=0))
            elif kind == 'spark':
                a = r.uniform(0, 6.28); sp = r.uniform(40, 220)
                self.ps.append(dict(k='spark', x=x, y=y, vx=math.cos(a) * sp, vy=math.sin(a) * sp, life=r.uniform(.6, 1.2),
                                    age=0, sz=r.uniform(5, 11), ph=r.uniform(0, 6)))
            elif kind == 'sweat':
                self.ps.append(dict(k='drop', x=x, y=y, vx=kw.get('vx', 60), vy=-kw.get('vy', 140), life=.7, age=0, sz=5.5, gy=9999))
            elif kind == 'leaf':
                self.ps.append(dict(k='leaf', x=x, y=y, vx=0, vy=0, life=99, age=0, sz=1, ph=r.uniform(0, 6)))

    def step(self, dt):
        self.t += dt
        while self.i < len(self.events) and self.events[self.i][0] <= self.t:
            e = self.events[self.i]
            self.spawn(e[1], e[2], e[3], e[4] if len(e) > 4 else 1, **(e[5] if len(e) > 5 else {}))
            self.i += 1
        keep = []
        for p in self.ps:
            p['age'] += dt
            if p['age'] > p['life']:
                continue
            if p['k'] == 'drop':
                p['vy'] += 1100 * dt
                p['x'] += p['vx'] * dt; p['y'] += p['vy'] * dt
                if p['y'] > p['gy'] and p['vy'] > 0:
                    continue
            elif p['k'] == 'note':
                p['x'] += (p['vx'] + 26 * math.sin(p['ph'] + p['age'] * 4)) * dt; p['y'] += p['vy'] * dt
            elif p['k'] in ('heart', 'spark'):
                p['vx'] *= (1 - 1.8 * dt); p['vy'] = p['vy'] * (1 - 1.8 * dt) - (35 if p['k'] == 'heart' else 0) * dt
                p['x'] += p['vx'] * dt; p['y'] += p['vy'] * dt
            elif p['k'] == 'z':
                p['x'] += p['vx'] * dt; p['y'] += p['vy'] * dt
            keep.append(p)
        self.ps = keep

    def advance_to(self, t):
        dt = 1.0 / FPS
        while self.t + dt <= t + 1e-6:
            self.step(dt)

    def draw(self, c):
        for p in self.ps:
            u = p['age'] / p['life']
            a = 255 * (1 - u) ** .7
            if p['k'] == 'drop':
                oval(c, p['x'], p['y'], p['sz'] * .8, p['sz'], fill((190, 230, 255), 230 * (1 - u * .6)))
            elif p['k'] == 'note':
                c.save(); c.translate(p['x'], p['y']); c.scale(p['sz'], p['sz']); c.rotate(-15)
                cc = p['col']
                c.drawOval(R(-7, -5, 14, 10), fill(cc, a)); c.drawLine(6, -1, 6, -26, stroke(cc, 3, a))
                fl = skia.Path(); fl.moveTo(6, -26); fl.quadTo(16, -22, 14, -12)
                c.drawPath(fl, stroke(cc, 3, a)); c.restore()
            elif p['k'] == 'heart':
                s = p['sz'] * min(1, p['age'] * 5)
                hp = skia.Path(); hp.moveTo(0, s * .9); hp.cubicTo(-s * 1.4, -s * .1, -s * .7, -s * 1.1, 0, -s * .35)
                hp.cubicTo(s * .7, -s * 1.1, s * 1.4, -s * .1, 0, s * .9)
                c.save(); c.translate(p['x'], p['y']); c.drawPath(hp, fill((255, 90, 130), a)); c.restore()
            elif p['k'] == 'spark':
                s = p['sz'] * (1 - u * .5) * (0.7 + 0.3 * math.sin(p['age'] * 24 + p['ph']))
                sp = skia.Path(); sp.moveTo(0, -s); sp.quadTo(0, 0, s, 0); sp.quadTo(0, 0, 0, s); sp.quadTo(0, 0, -s, 0); sp.quadTo(0, 0, 0, -s)
                c.save(); c.translate(p['x'], p['y']); c.drawPath(sp, fill((255, 240, 150), a)); c.restore()
            elif p['k'] == 'z':
                text(c, 'Z', p['x'], p['y'], 30 * p['sz'] * (0.6 + .5 * u), (230, 240, 255), a, outline=None)

# ---------------------------------------------------------------- hopping (pose to pose)
def hop_pose(t, t0, x0, x1, h, ant=.22, air=.55, land=.12, rec=.30, squash=.68):
    """Pose of a hop. Returns dict(x, air, rot, sx, sy, phase) or None if t outside [t0, t0+dur]."""
    dur = ant + air + land + rec
    u = t - t0
    if u < 0 or u > dur:
        return None
    d = 1 if x1 >= x0 else -1
    if u < ant:                       # ANTICIPATION: crouch + lean back
        k = ease_io(u / ant)
        sy = lerp(1, squash, k)
        return dict(x=x0 - d * 5 * k, air=0, rot=-d * 9 * k, sy=sy, sx=1 / sy, phase='ant')
    u -= ant
    if u < air:                       # AIR: stretch up, arc, stretch down
        v = u / air
        arc = 4 * v * (1 - v)
        sy = kf(v, [(0, .78), (.12, 1.32), (.5, 1.0), (.85, 1.14), (1, 1.2)], lambda q: q)
        sy = kf(v, [(0, squash), (.10, 1.30), (.5, 1.0), (.88, 1.14), (1, 1.2)], smooth)
        return dict(x=lerp(x0 - d * 5, x1, v), air=h * arc, rot=d * kf(v, [(0, -8), (.25, 8), (.5, 4), (1, 14)], smooth),
                    sy=sy, sx=1 / sy, phase='air')
    u -= air
    if u < land:                      # IMPACT: squash
        k = ease_out(u / land)
        sy = lerp(1.2, squash - .08, k)
        return dict(x=x1, air=0, rot=d * lerp(14, 3, k), sy=sy, sx=1 / sy, phase='land')
    u -= land                         # RECOVER: spring overshoot (follow-through)
    sp = spring(u / rec, 3.2, 5.5)
    sy = lerp(squash - .08, 1.0, sp)
    return dict(x=x1, air=0, rot=d * 3 * (1 - clamp(u / rec)), sy=sy, sx=1 / sy, phase='rec')

def hop_track(t, hops, x_start):
    """hops = list of dict(t0,x0,x1,h,**opts). Returns pose at time t (idle pose between hops)."""
    x = x_start
    for hp in hops:
        opts = {k: v for k, v in hp.items() if k not in ('t0', 'x0', 'x1', 'h')}
        pose = hop_pose(t, hp['t0'], hp['x0'], hp['x1'], hp['h'], **opts)
        if pose is not None:
            return pose
        if t > hp['t0']:
            x = hp['x1']
    br = 0.012 * math.sin(2 * math.pi * 0.7 * t)
    return dict(x=x, air=0, rot=0, sy=1 + br, sx=1 / (1 + br), phase='idle')

def lagvec(fn, t, k=1.6, dt=.06):
    """Tuft follow-through: lags behind the movement. fn(t) -> (x, air)."""
    a, b = fn(t), fn(t - dt)
    return ((b[0] - a[0]) * k * 1.0, (a[1] - b[1]) * k * 0.8 + (b[0] - a[0]) * 0.0)

# ---------------------------------------------------------------- the world
_rng = random.Random(3)
FAR = [(i * 120 + _rng.randint(-30, 30), _rng.randint(70, 190), _rng.randint(70, 130), _rng.randint(0, 2)) for i in range(34)]
PALMS = [(240, 1.0), (790, 0.8), (1380, 1.1), (1900, .9), (2500, 1.0), (3000, .8), (-300, 1.0)]
STARS = [(_rng.random() * W, _rng.random() * 330, _rng.random() * 6.28, _rng.uniform(1, 2.2)) for _ in range(70)]
RAIN = [(_rng.random(), _rng.random(), _rng.uniform(.8, 1.4), _rng.random()) for _ in range(320)]
RIPPLE = [(_rng.random() * W, GY + 4 + _rng.random() * 110, _rng.uniform(.6, 1.6), _rng.random()) for _ in range(46)]

def draw_sky(c, pal, T=0):
    c.drawRect(R(0, 0, W, H), fill((0, 0, 0), shader=lin(0, 0, 0, GY, pal['sky_top'], pal['sky_bot'])))
    if pal['stars'] > 0.02:
        for x, y, ph, r in STARS:
            c.drawCircle(x, y, r * (.7 + .3 * math.sin(T * 2 + ph)), fill((255, 255, 240), 220 * pal['stars']))

def draw_far(c, cam, pal):
    base = pal['far']
    for x, h, w, kind in FAR:
        sx = x - cam * 0.25
        if sx < -200 or sx > W + 200:
            continue
        y = GY - 20 - h
        c.drawRect(R(sx, y, w, h + 20), fill(base))
        if kind == 1:
            c.drawPath(poly([(sx - 6, y), (sx + w / 2, y - 26), (sx + w + 6, y)]), fill(mix(base, (0, 0, 0), .12)))
        # tiny lit windows
        if pal['stars'] > .3:
            for wy in range(int(y) + 14, int(GY) - 40, 30):
                for wx in range(int(sx) + 10, int(sx + w) - 10, 22):
                    if (wx * 7 + wy * 13) % 5 == 0:
                        c.drawRect(R(wx, wy, 8, 10), fill((255, 214, 120), 210 * pal['stars']))

def draw_palms(c, cam, pal, T):
    col_ = pal['palm']
    for x, sc in PALMS:
        sx = x - cam * 0.55
        if sx < -250 or sx > W + 250:
            continue
        top = (sx + 40 * sc, GY - 20 - 330 * sc)
        tr = skia.Path(); tr.moveTo(sx, GY - 20); tr.quadTo(sx + 10 * sc, GY - 190 * sc, top[0], top[1])
        c.drawPath(tr, stroke(col_, 16 * sc))
        sway = math.sin(T * 1.3 + x) * 5
        for k in range(7):
            a = -math.pi + k * math.pi / 6 + .15
            ex = top[0] + math.cos(a) * 120 * sc + sway
            ey = top[1] + math.sin(a) * 60 * sc + 70 * sc * (1 if math.cos(a) * math.cos(a) > .3 else .3)
            fr = skia.Path(); fr.moveTo(*top); fr.quadTo((top[0] + ex) / 2, top[1] - 40 * sc, ex, ey)
            c.drawPath(fr, stroke(col_, 11 * sc))

def draw_ground(c, cam, pal):
    c.drawRect(R(0, GY - 14, W, H - GY + 14), fill(pal['road']))
    c.drawRect(R(0, GY - 30, W, 30), fill(pal['walk']))
    c.drawRect(R(0, GY - 6, W, 6), fill(mix(pal['walk'], (0, 0, 0), .25)))
    # dashed road marking
    off = -(cam % 160)
    for i in range(-1, 10):
        c.drawRect(R(off + i * 160, GY + 74, 90, 8), fill((235, 230, 200), 150))

def draw_house(c, cam, pal, lit):
    x0 = -cam
    if x0 > W + 50 or x0 + 720 < -50:
        return
    wall, roof = pal['wall'], pal['roof']
    c.drawRect(R(x0 + 40, 330, 620, GY - 330 - 14), fill(wall))
    c.drawRect(R(x0 + 40, GY - 70, 620, 56), fill(mix(wall, (0, 0, 0), .12)))
    c.drawPath(poly([(x0 + 10, 338), (x0 + 130, 258), (x0 + 570, 258), (x0 + 690, 338)]), fill(roof))
    for i in range(0, 64):
        xx = x0 + 22 + i * 10.5
        t_ = clamp((xx - (x0 + 10)) / 680)
        c.drawLine(xx, 338 - 2, xx + 0 + (65 * (1 - 2 * abs(t_ - .5)) * 0), 262 + 80 * (1 - min(1, 2 * min(t_, 1 - t_) * 3.2)), stroke(mix(roof, (0, 0, 0), .22), 2))
    c.drawRect(R(x0 + 10, 336, 680, 9), fill(mix(roof, (0, 0, 0), .3)))
    # door
    c.drawRect(R(x0 + 330, 440, 120, GY - 440 - 14), fill(pal['door']))
    c.drawRect(R(x0 + 330, 440, 120, GY - 440 - 14), stroke(mix(pal['door'], (0, 0, 0), .5), 5))
    for yy in (462, 520):
        c.drawRect(R(x0 + 344, yy, 92, 46), stroke(mix(pal['door'], (0, 0, 0), .35), 3))
    c.drawCircle(x0 + 432, 520, 5, fill((240, 200, 90)))
    for wx in (120, 520):
        win = R(x0 + wx, 395, 104, 92)
        c.drawRect(win, fill((70, 96, 128)))
        if lit > 0:
            c.drawRect(win, fill((255, 214, 120), 255 * lit))
        for gx in range(1, 4):
            c.drawLine(x0 + wx + gx * 26, 395, x0 + wx + gx * 26, 487, stroke(mix(wall, (0, 0, 0), .5), 3))
        c.drawLine(x0 + wx, 441, x0 + wx + 104, 441, stroke(mix(wall, (0, 0, 0), .5), 3))
        c.drawRect(win, stroke(mix(wall, (0, 0, 0), .45), 5))
    # doorstep
    c.drawRect(R(x0 + 290, STEP_Y + 8, 240, GY - STEP_Y - 8 - 6), fill(mix(pal['walk'], (0, 0, 0), .2)))
    c.drawRect(R(x0 + 290, STEP_Y, 240, 10), fill(mix(pal['walk'], (255, 255, 255), .15)))

def draw_tindahan(c, cam, pal, T, lit):
    x0 = 1150 - cam
    if x0 > W + 80 or x0 + 400 < -80:
        return
    body = (86, 176, 160)
    c.drawRect(R(x0, 410, 370, GY - 410 - 14), fill(body))
    c.drawPath(poly([(x0 - 22, 414), (x0 + 28, 356), (x0 + 342, 356), (x0 + 392, 414)]), fill((172, 96, 84)))
    for i in range(0, 36):
        c.drawLine(x0 - 14 + i * 11.2, 412, x0 + 18 + i * 9.6, 360, stroke((120, 66, 58), 2))
    # counter window
    win = R(x0 + 40, 452, 290, 98)
    c.drawRect(win, fill((52, 54, 70)))
    if lit > 0:
        c.drawRect(win, fill((255, 208, 110), 235 * lit))
    for i in range(14):   # hanging sachets (chichirya)
        cc = ((235, 70, 70), (255, 200, 40), (60, 170, 230), (90, 200, 120))[i % 4]
        c.drawRect(R(x0 + 52 + i * 20, 458, 14, 30 + (i % 3) * 8), fill(cc))
    for i in range(7):
        cc = ((235, 150, 60), (200, 90, 180), (90, 160, 230))[i % 3]
        c.drawRect(R(x0 + 50 + i * 40, 520, 30, 26), fill(cc))
    c.drawRect(win, stroke((60, 40, 30), 7))
    c.drawRect(R(x0 + 30, 548, 310, 14), fill((150, 100, 60)))
    # sign
    c.drawRect(R(x0 + 70, 410, 230, 38), fill((226, 60, 60)))
    c.drawRect(R(x0 + 70, 410, 230, 38), stroke((255, 255, 255), 3))
    text(c, 'SARI-SARI STORE', x0 + 185, 438, 20, (255, 255, 255), 255)

def draw_lamp(c, cam, xw, pal, glow):
    x = xw - cam
    if x < -60 or x > W + 60:
        return
    c.drawRect(R(x - 6, 250, 12, GY - 250 - 14), fill((54, 58, 70)))
    c.drawPath(poly([(x - 6, 252), (x - 6, 238), (x + 34, 238), (x + 40, 250)]), fill((54, 58, 70)))
    c.drawOval(R(x + 14, 244, 36, 14), fill((250, 240, 190) if glow > .2 else (140, 140, 140)))

def draw_lights(c, cam, pal, T, lamp_flicker=1.0, house_lit=0, tind_lit=0):
    """Additive glow drawn after the darkness overlay."""
    d = pal['dark'] / 95.0
    if d < 0.02:
        return
    def glow(x, y, r, color, a):
        p = skia.Paint(); p.setAntiAlias(True)
        p.setShader(rad(x, y, r, color, color, a, 0)); p.setBlendMode(skia.BlendMode.kPlus)
        c.drawCircle(x, y, r, p)
    for xw in (1050, 1850, 2650):
        glow(xw - cam + 32, 260, 190, (255, 220, 140), 120 * d * lamp_flicker)
    glow(1335 - cam, 480, 230, (255, 210, 120), 90 * d * tind_lit)
    for wx in (172, 572):
        glow(wx - cam, 441, 150, (255, 210, 120), 85 * d * house_lit)

def draw_puddles(c, cam, pal, T):
    for xw, w in ((300, 120), (700, 160), (1000, 140), (1500, 110), (2150, 150), (2400, 130), (2700, 150)):
        x = xw - cam
        if x < -200 or x > W + 200:
            continue
        oval(c, x, GY + 28, w, 11, fill(mix(pal['sky_bot'], pal['road'], .35), 190))
        oval(c, x - w * .25, GY + 25, w * .35, 3.5, fill((255, 255, 255), 80))

def pond_range():
    return 1660, 1960

def draw_pond(c, cam, pal, T):
    a, b = pond_range()
    x0, x1 = a - cam, b - cam
    if x1 < -20 or x0 > W + 20:
        return
    base = mix(pal['sky_bot'], (60, 130, 190), .55)
    p = skia.Path()
    p.addOval(R(x0, GY - 2, x1 - x0, 62))
    c.drawPath(p, fill(base, 235))
    c.drawPath(p, stroke(mix(pal['walk'], (0, 0, 0), .15), 4))
    for k in range(3):
        u = (T * .5 + k / 3) % 1
        oval(c, (x0 + x1) / 2 + 70 * math.sin(k * 2.1), GY + 28, 20 + 80 * u, 4 + 12 * u, stroke((255, 255, 255), 2, 150 * (1 - u)))

def surf_y(xw, T, wl, wave=None):
    """World water surface height (screen y) at world x."""
    y = wl + math.sin(xw * .02 - T * 2.6) * 4 + math.sin(xw * .047 - T * 4.1) * 2
    if wave is not None:
        wx, amp = wave
        y -= amp * math.exp(-((xw - wx) / 95.0) ** 2)
    return y

def draw_water(c, cam, wl, T, wave=None, alpha=170):
    if wl >= H - 2:
        return
    top = skia.Path()
    xs = list(range(-20, W + 40, 14))
    first = True
    for x in xs:
        y = surf_y(x + cam, T, wl, wave)
        if first:
            top.moveTo(x, y); first = False
        else:
            top.lineTo(x, y)
    surf = skia.Path(top)
    top.lineTo(W + 40, H + 10); top.lineTo(-20, H + 10); top.close()
    c.drawPath(top, fill((0, 0, 0), shader=lin(0, wl - 30, 0, H, (74, 160, 206), (28, 84, 140), alpha, 235)))
    c.drawPath(surf, stroke((235, 248, 255), 3.5, 190))
    # streaks showing the flow
    for k in range(14):
        sx = ((k * 211 + T * 150 * (1 + (k % 3) * .3)) % (W + 200)) - 100
        sy = wl + 18 + (k * 37) % (H - wl - 24 if H - wl > 30 else 30)
        c.drawLine(sx, sy, sx + 40 + (k % 4) * 16, sy, stroke((255, 255, 255), 2.5, 70))

def draw_rain(c, T, intensity, wind=.25):
    if intensity <= 0.01:
        return
    n = int(len(RAIN) * min(1, intensity))
    p = skia.Path()
    for i in range(n):
        x0, ph, sp, ln = RAIN[i]
        y = ((ph * (H + 120)) + T * 900 * sp) % (H + 120) - 60
        x = (x0 * (W + 300) + T * 900 * sp * wind) % (W + 300) - 60
        l = 26 + 30 * ln
        p.moveTo(x, y); p.lineTo(x - l * wind, y - l)
    c.drawPath(p, stroke((215, 230, 250), 2.2, 120 * min(1, intensity + .2)))
    # ripples on the street
    for i, (rx, ry, rate, ph) in enumerate(RIPPLE):
        if i > n * len(RIPPLE) / len(RAIN):
            break
        u = (T * rate * .9 + ph) % 1
        oval(c, rx, ry, 4 + 20 * u, (4 + 20 * u) * .28, stroke((235, 245, 255), 1.8, 170 * (1 - u)))

def overlay_dark(c, pal, k=1.0, tint=(8, 12, 40)):
    a = pal['dark'] * k
    if a > 1:
        c.drawRect(R(0, 0, W, H), fill(tint, a))

def vignette(c, a=110):
    p = skia.Paint(); p.setAntiAlias(True)
    p.setShader(rad(W / 2, H / 2, 780, (0, 0, 0), (0, 0, 0), 0, a))
    c.drawRect(R(0, 0, W, H), p)

def jeepney(c, x, gy, T, sc=1.0, face=-1, pitch=0.0, wob=0.0):
    """Cartoon jeepney. face=-1: nose points left. x = centre."""
    c.save()
    c.translate(x, gy)
    c.scale(sc * -face * -1 if False else sc, sc)
    c.scale(1 if face == -1 else -1, 1)
    c.translate(-95 * (0 if face == -1 else 0), 0)
    c.rotate(pitch)
    c.translate(0, wob)
    # body
    c.drawOval(R(-230, -8, 480, 22), fill((0, 0, 0), 55))
    body = skia.Path()
    body.moveTo(-250, -60); body.lineTo(-250, -120)
    body.quadTo(-250, -150, -215, -150); body.lineTo(-140, -150); body.lineTo(-120, -205)
    body.quadTo(-115, -222, -90, -222); body.lineTo(200, -222)
    body.quadTo(236, -222, 236, -186); body.lineTo(236, -60); body.close()
    c.drawPath(body, fill((255, 196, 40)))
    c.drawPath(body, stroke((40, 30, 50), 5))
    c.drawRect(R(-250, -108, 486, 24), fill((226, 52, 70)))
    c.drawRect(R(-250, -84, 486, 10), fill((40, 120, 220)))
    # windows with passengers
    for i in range(4):
        wx = -92 + i * 70
        c.drawRect(R(wx, -204, 56, 52), fill((150, 210, 240)))
        oval(c, wx + 28, -170, 14, 15, fill((60, 50, 70), 200))
        c.drawRect(R(wx, -204, 56, 52), stroke((40, 30, 50), 4))
    # windshield
    c.drawPath(poly([(-205, -146), (-142, -146), (-126, -202), (-136, -202)]), fill((170, 225, 250)))
    # roof rack + label
    c.drawLine(-100, -228, 200, -228, stroke((200, 200, 215), 6))
    c.save(); c.translate(55, 0)
    if face == 1:
        c.scale(-1, 1)      # keep the lettering readable when the jeepney is mirrored
    text(c, 'STOP PLEASE', 0, -92, 17, (255, 255, 255), 255, outline=(40, 30, 50), ow=4)
    c.restore()
    # headlight
    c.drawCircle(-248, -92, 11, fill((255, 250, 200)))
    # bumper
    c.drawRect(R(-258, -64, 14, 16), fill((210, 210, 225)))
    c.drawRect(R(222, -64, 18, 16), fill((210, 210, 225)))
    # wheels
    for wx in (-150, 130):
        c.drawCircle(wx, -34, 36, fill((34, 34, 42)))
        c.drawCircle(wx, -34, 17, fill((190, 190, 205)))
        ang = T * 14 * face * -1
        for k in range(5):
            a = ang + k * 2 * math.pi / 5
            c.drawLine(wx, -34, wx + 15 * math.cos(a), -34 + 15 * math.sin(a), stroke((90, 90, 105), 3))
    c.restore()

def fade_black(c, a):
    if a > 0.004:
        c.drawRect(R(0, 0, W, H), fill((0, 0, 0), 255 * clamp(a)))

def caption(c, who, line, a=1.0):
    if a <= .01:
        return
    f = font(30, False)
    wd = f.measureText(line)
    nm = {'L': 'Kaliwa', 'R': 'Kanan', 'N': ''}[who]
    nw = font(30, True).measureText(nm + ':  ') if nm else 0
    tw = wd + nw
    x = W / 2 - tw / 2
    rrect(c, x - 22, H - 82, tw + 44, 54, 27, fill((10, 14, 30), 150 * a))
    if nm:
        c.drawString(nm + ':', x, H - 44, font(30, True), fill(BLUE_L if who == 'L' else (255, 170, 205), 255 * a))
    c.drawString(line, x + nw, H - 44, f, fill((255, 255, 255), 255 * a))
