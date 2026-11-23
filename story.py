"""Scenes for 'Si Kaliwa'. Times inside a scene are local seconds (t); T = absolute film time."""
import math
from engine import *

START = {'S0': 0, 'S1': 8, 'S2': 32, 'S3': 54, 'S4': 74, 'S5': 104, 'S6': 124, 'S7': 146}
DUR = {'S0': 8, 'S1': 24, 'S2': 22, 'S3': 20, 'S4': 30, 'S5': 20, 'S6': 22, 'S7': 14}
TOTAL = 160
KX, NX = 372, 462          # home positions of Kaliwa (left slipper) and Kanan (right slipper) on the step
S = 0.78                   # character scale

SFX = []                   # (absolute T, kind, params)  -> consumed by audio.py
CAP = {k: [] for k in START}
SIMEV = {k: [] for k in START}

def sf(sc, t, kind, **kw):
    SFX.append((START[sc] + t, kind, kw))

def cap(sc, t0, t1, who, text, shout=False):
    CAP[sc].append((t0, t1, who, text, shout))
    base = {'L': 430, 'R': 560, 'N': 500}[who]
    n = max(2, int(len(text) * (0.42 if shout else 0.5)))
    for i in range(n):
        tt = t0 + 0.08 + (t1 - t0 - 0.3) * i / max(1, n - 1)
        sf(sc, tt, 'blip', f=base * (1 + 0.22 * math.sin(i * 1.9 + len(text))) * (1.35 if shout else 1.0),
           amp=0.55 if shout else 0.32)

def hop_sfx(sc, hops, big=1.0):
    for h in hops:
        a = h.get('ant', .22); ai = h.get('air', .55)
        sf(sc, h['t0'] + a, 'boing', amp=.5 * big, up=1)
        sf(sc, h['t0'] + a + ai, 'thud', f=150, amp=.5 * big)

def ground_y(x):
    return GY - (GY - STEP_Y) * smooth((x - 255) / 35) * smooth((565 - x) / 35)

def lying_base(gy, s=S):
    return gy + 95 * s - 36

def fc(t, seed=0.0, **kw):
    d = dict(open=1.0)
    d.update(kw)
    d['open'] = min(d['open'], blink_open(t, 3.4, seed))
    return d

def bg(c, T, cam, house_lit=None, tind_lit=None, lamp=1.0, dk=1.0):
    pal = pal_at(T)
    auto = clamp(pal['dark'] / 70.0)
    hl = auto if house_lit is None else house_lit
    tl = auto if tind_lit is None else tind_lit
    draw_sky(c, pal, T); draw_far(c, cam, pal); draw_palms(c, cam, pal, T)
    draw_ground(c, cam, pal); draw_house(c, cam, pal, hl); draw_tindahan(c, cam, pal, T, tl)
    for xw in (1050, 1850, 2650):
        draw_lamp(c, cam, xw, pal, lamp)
    draw_puddles(c, cam, pal, T); draw_pond(c, cam, pal, T)
    overlay_dark(c, pal, dk)
    draw_lights(c, cam, pal, T, lamp, hl, tl)
    return pal

def finish(c, T, pal, rain=0.0, grade=.35, vig=110, flash=0.0, wind=.25):
    draw_rain(c, T, rain, wind)
    overlay_dark(c, pal, grade)
    vignette(c, vig)
    if flash > 0.01:
        c.drawRect(R(0, 0, W, H), fill((255, 255, 255), 255 * clamp(flash)))

def draw_caps(c, sc, t):
    for (t0, t1, who, line, shout) in CAP[sc]:
        if t0 - .02 <= t <= t1 + .2:
            a = smooth((t - t0) / .15) * smooth((t1 + .15 - t) / .2)
            if shout:
                sh = (math.sin(t * 61) * 5, math.cos(t * 53) * 4) if t < t1 else (0, 0)
                sz = 98 * (1 + .08 * math.sin(t * 20))
                text(c, line, W / 2 + sh[0], 205 + sh[1], sz, (255, 244, 170), 255 * a, outline=(70, 24, 50), ow=12)
            else:
                caption(c, who, line, a)

def fades(c, t, dur, fin=.35, fout=.4):
    fade_black(c, (1 - clamp(t / fin)) if fin else 0)
    fade_black(c, clamp((t - (dur - fout)) / fout) if fout else 0)

def zoom_begin(c, z, cx, cy):
    c.save(); c.translate(cx, cy); c.scale(z, z); c.translate(-cx, -cy)

def star(c, x, y, r, a=255):
    sp = skia.Path(); sp.moveTo(0, -r); sp.quadTo(0, 0, r, 0); sp.quadTo(0, 0, 0, r); sp.quadTo(0, 0, -r, 0); sp.quadTo(0, 0, 0, -r)
    c.save(); c.translate(x, y); c.drawPath(sp, fill((255, 236, 120), a)); c.restore()

def dizzy(c, t, x, ytop, a=255):
    for k in range(3):
        ang = t * 7 + k * 2.09
        star(c, x + math.cos(ang) * 44, ytop + math.sin(ang) * 11, 11, a)

def draw_char(c, x, by, pose, face, kind, lag=(0, 0), flip=1, pivot=0, gy=None, alpha=255, shadow_on=True):
    air = pose.get('air', 0)
    if shadow_on:
        shadow(c, x, gy if gy is not None else by, air)
    slipper(c, x, by - air, s=S, rot=pose['rot'], sx=pose['sx'], sy=pose['sy'], pivot=pivot, kind=kind, face=face,
            lag=lag, flip=flip, alpha=alpha)

def arc_guide(c, cam, x0, x1, gy, h, a=170, upto=1.0):
    n = 18
    for i in range(1, n):
        v = i / n
        if v > upto:
            break
        c.drawCircle(lerp(x0, x1, v) - cam, gy - 80 - h * 4 * v * (1 - v), 3.6, fill((255, 255, 255), a))

def leaf(c, x, y, rot, a=255):
    c.save(); c.translate(x, y); c.rotate(rot)
    p = skia.Path(); p.moveTo(-34, 0); p.quadTo(0, -22, 34, 0); p.quadTo(0, 22, -34, 0)
    c.drawPath(p, fill((92, 190, 98), a)); c.drawPath(p, stroke((34, 98, 52), 3, a))
    c.drawLine(-30, 0, 30, 0, stroke((34, 98, 52), 2.5, a)); c.restore()

def coconut(c, x, y, sx=1, sy=1):
    c.save(); c.translate(x, y); c.scale(sx, sy)
    c.drawCircle(0, -20, 21, fill((126, 84, 52))); c.drawCircle(0, -20, 21, stroke((60, 36, 24), 3.5))
    for dx, dy in ((-6, -26), (6, -26), (0, -14)):
        c.drawCircle(dx, dy, 3, fill((50, 30, 20)))
    c.restore()

def bubble(c, x, y, w, h, tail=(-1, 1)):
    c.drawOval(R(x - w / 2, y - h / 2, w, h), fill((255, 255, 255), 238))
    c.drawOval(R(x - w / 2, y - h / 2, w, h), stroke((120, 140, 180), 3))
    for i, r in enumerate((15, 10, 6)):
        cx = x + tail[0] * (w / 2 - 10 + (i + 1) * 20); cy = y + h / 2 + 4 + i * 20
        c.drawCircle(cx, cy, r, fill((255, 255, 255), 238)); c.drawCircle(cx, cy, r, stroke((120, 140, 180), 2.5))

# ====================================================================== S0  TITLE (0-8 s)
LET = "KALIWA"
def s0(c, t, st):
    st.advance_to(t)
    T = t
    zoom_begin(c, lerp(1.0, 1.05, t / 8), 640, 430)
    pal = bg(c, T, 0, house_lit=.0, tind_lit=0)
    shadow(c, KX, STEP_Y); shadow(c, NX, STEP_Y)
    pl = hop_pose(t, 5.3, KX, KX, 75, ant=.2, air=.5, land=.12, rec=.32)
    pr = hop_pose(t, 5.38, NX, NX, 75, ant=.2, air=.5, land=.12, rec=.32)
    br = 0.015 * math.sin(2 * math.pi * .6 * t)
    pl = pl or dict(rot=0, sx=1 / (1 + br), sy=1 + br, air=0)
    pr = pr or dict(rot=0, sx=1 / (1 - br), sy=1 - br, air=0)
    happy = t > 5.0
    slipper(c, KX, STEP_Y - pl.get('air', 0), s=S, rot=pl['rot'], sx=pl['sx'], sy=pl['sy'], kind='L',
            face=fc(t, 0, mouth='big' if happy else 'smile', mo=.6, es=1.1 if happy else 1))
    slipper(c, NX, STEP_Y - pr.get('air', 0), s=S, rot=pr['rot'], sx=pr['sx'], sy=pr['sy'], kind='R', flip=-1,
            face=fc(t, 1.1, mouth='big' if happy else 'smile', mo=.6, es=1.1 if happy else 1))
    st.draw(c)
    c.restore()
    pal = pal_at(T)
    finish(c, T, pal, 0, grade=.2, vig=120)
    # bouncing title letters (squash and stretch on every landing)
    f = font(128)
    ws = [f.measureText(ch) for ch in LET]
    x = 640 - sum(ws) / 2
    idx = 0
    for ch, w in zip(LET, ws):
        if ch != ' ':
            ti = .6 + .16 * idx; idx += 1
            u = (t - ti) / .5
            if u >= 0:
                if u < 1:
                    y = lerp(-170, 235, ease_in(u)); sy = 1.25; sx = .82
                else:
                    tau = (t - ti - .5) / .65
                    sy = lerp(.52, 1, spring(tau, 2.4, 6.0)); sx = 1 / sy; y = 235
                c.save(); c.translate(x + w / 2, y); c.scale(sx, sy)
                colr = (255, 214, 82) if idx <= 2 else (255, 250, 240)
                c.drawString(ch, -w / 2, 6, f, stroke((70, 36, 66), 14, 255))
                c.drawString(ch, -w / 2, 0, f, stroke((70, 36, 66), 14, 255))
                c.drawString(ch, -w / 2, 0, f, fill(colr))
                c.restore()
        x += w
    a = smooth((t - 4.3) / .8)
    text(c, 'A story of two slippers', 640, 300, 40, (255, 255, 255), 255 * a, bold=False, outline=(70, 36, 66), ow=8)
    a2 = smooth((t - 5.6) / .8)
    text(c, 'A short animation  •  The 12 Principles of Animation', 640, 345, 22, (255, 240, 220), 230 * a2, bold=False, outline=(70, 36, 66), ow=5)
    fades(c, t, 8, fin=.5, fout=.4)

for i in range(8):
    sf('S0', .6 + .16 * i + .5, 'thud', f=110 + i * 14, amp=.5)
sf('S0', 4.3, 'chime', amp=.35)
sf('S0', 5.3 + .2, 'boing', amp=.5, up=1); sf('S0', 5.38 + .2, 'boing', amp=.45, up=1)
sf('S0', 6.0, 'thud', f=150, amp=.4)

# ====================================================================== S1  DOORSTEP (24 s)
SIMEV['S1'] = ([(0.2, 'z', KX + 30, STEP_Y - 175), (1.3, 'z', KX + 30, STEP_Y - 175)] +
               [(9.0 + .55 * i, 'note', (KX if i % 2 == 0 else NX), STEP_Y - 200, 1, dict(col=(BLUE_L if i % 2 == 0 else (255, 170, 205)))) for i in range(7)] +
               [(18.0, 'sweat', KX + 30, STEP_Y - 150, 1, dict(vx=50, vy=120))])
cap('S1', 2.4, 4.2, 'R', 'Kaliwa, wake up!')
cap('S1', 4.6, 6.9, 'L', 'Aw! It is so early...')
cap('S1', 7.1, 8.8, 'R', 'It is already evening.')
cap('S1', 9.2, 11.6, 'L', "Come on, let's sing our song!")
cap('S1', 12.0, 13.8, 'L', 'Wait... why is it getting dark?')
cap('S1', 16.0, 18.4, 'R', 'Stay close to the door!')
cap('S1', 19.0, 20.8, 'L', 'We stay together, okay?')
cap('S1', 21.0, 22.6, 'R', 'Promise.')
sf('S1', 1.9, 'yawn', amp=.3); sf('S1', 2.1, 'boing', amp=.3, up=1); sf('S1', 3.55, 'thud', f=120, amp=.4)
sf('S1', 3.75 + .16, 'boing', amp=.6, up=1); sf('S1', 3.75 + .16 + .5, 'thud', f=150, amp=.5)
sf('S1', 9.0, 'hum', vol=.55, dur=3.9)
sf('S1', 12.0, 'wind', dur=5, amp=.4)
sf('S1', 14.05, 'thunder', amp=.9)
sf('S1', 14.0 + .16, 'boing', amp=.5, up=1); sf('S1', 14.0 + .16 + .5, 'thud', f=150, amp=.45)
sf('S1', 22.9, 'whoosh', dur=1.0, amp=.5)

def s1(c, t, st):
    st.advance_to(t)
    T = START['S1'] + t
    zoom_begin(c, lerp(1.0, 1.12, ease_io(t / 23)), 417, 470)
    pal = bg(c, T, 0, house_lit=clamp((t - 12.5) / 8))
    # ---- Kaliwa
    bump = math.sin(math.pi * clamp((t - 3.45) / .35)) if 3.45 < t < 3.8 else 0
    kx = KX - 14 * bump
    krot = -10 * bump
    gust = clamp((t - 11.8) / 1.5)
    lagw = (13 * gust * (0.8 + .2 * math.sin(t * 9)), -2 * gust)
    if t < 3.75:
        sl = 0.022 * math.sin(2 * math.pi * .45 * t)
        pk = dict(rot=krot, sx=1 / (1 + sl), sy=1 + sl, air=0)
        fk = dict(open=.04, mouth='smile', blush=1)
        lag_k = (0, 0)
    else:
        hp = hop_pose(t, 3.75, KX, KX, 95, ant=.16, air=.5, land=.1, rec=.3, squash=.72)
        hp2 = hop_pose(t, 14.0, KX, KX, 45, ant=.12, air=.35, land=.1, rec=.3, squash=.78)
        pk = hp or hp2
        phase = pk['phase'] if pk else 'idle'
        if pk is None:
            sw = 0
            if 9.0 <= t < 13.2:
                sw = 6 * math.sin(2 * math.pi * .8 * (t - 9.0))
            br = 0.012 * math.sin(2 * math.pi * .7 * t)
            pk = dict(rot=sw, sx=1 / (1 + br), sy=1 + br, air=0)
            if t >= 21.0:
                pk['rot'] = 5
            elif t >= 16.0:
                pk['rot'] = 6 * smooth((t - 16.0) / 1.0)
        if 3.75 <= t < 4.7:
            u = (t - 3.75)
            fk = dict(es=1.5 if u > .16 else 1.0, mouth='open', mo=1.0, brow=1, open=1)
        elif 4.7 <= t < 9.0:
            fk = fc(t, .3, open=.62, mouth='flat', brow=-.3)
            if 7.1 < t < 8.6:
                fk = fc(t, .3, open=.55, mouth='open', mo=.7)
        elif 9.0 <= t < 12.0:
            fk = dict(open=.04, happyclose=True, mouth='big', mo=.4 + .3 * math.sin(t * 7))
        elif 12.0 <= t < 14.0:
            fk = fc(t, .3, es=1.15, mouth='o', mo=.4, brow=.8, px=-.3, py=-.7)
        elif 14.0 <= t < 15.2:
            fk = dict(es=1.5, mouth='open', mo=1, brow=1)
        else:
            fk = fc(t, .3, es=1.12, mouth='wobble', brow=1, px=.5)
        lag_k = lagw if t > 11.8 else (0, 0)
    if pk is None:
        pk = dict(rot=0, sx=1, sy=1, air=0)
    # ---- Kanan
    xn = NX - 18 * bump
    nrot = -10 * bump
    if t < 1.8:
        sl = 0.022 * math.sin(2 * math.pi * .45 * t + 1)
        pn = dict(rot=0, sx=1 / (1 + sl), sy=1 + sl, air=0)
        fn_ = dict(open=.04, mouth='smile')
    else:
        syn = kf(t, [(1.8, 1.0), (2.15, .8), (2.45, 1.3), (3.1, 1.0)], ease_io)
        if t > 3.1:
            syn = 1.0
        hpn = hop_pose(t, 14.0 + .06, NX, NX, 38, ant=.12, air=.35, land=.1, rec=.3, squash=.82)
        if hpn is not None:
            pn = hpn
        else:
            sw = 0
            if 9.0 <= t < 13.2:
                sw = -6 * math.sin(2 * math.pi * .8 * (t - 9.0))
            br = 0.012 * math.sin(2 * math.pi * .7 * t + 1)
            sy_ = syn if t < 3.1 else (1 + br)
            pn = dict(rot=sw, sx=1 / sy_, sy=sy_, air=0)
            if t >= 16.0:
                pn['rot'] = -6 * smooth((t - 16.0) / 1.0)
        if 2.1 <= t < 2.9:
            fn_ = dict(es=1.1, mouth='open', mo=1.0, open=.3)
        elif t < 9.0:
            fn_ = fc(t, 1.1, mouth='smile', px=-.6 if 3.0 < t < 4.5 else 0)
        elif t < 12.0:
            fn_ = dict(open=.04, happyclose=True, mouth='big', mo=.35 + .3 * math.sin(t * 7 + 1))
        elif t < 14.0:
            fn_ = fc(t, 1.1, mouth='smile', brow=.5, px=-.2, py=-.6)
        elif t < 15.2:
            fn_ = dict(es=1.3, mouth='o', mo=.8, brow=.8)
        elif t < 21.0:
            fn_ = fc(t, 1.1, mouth='flat', brow=.7, px=.6)
        else:
            fn_ = fc(t, 1.1, mouth='smile', brow=.4, es=1.05)
    lag_n = lagw if t > 11.8 else (0, 0)
    # water rises from t = 15
    wl = lerp(730, 576, ease_in((t - 15) / 8.5)) if t > 15 else 800
    draw_char(c, kx, STEP_Y, pk, fk, 'L', lag=lag_k, gy=STEP_Y)
    draw_char(c, xn, STEP_Y, pn, fn_, 'R', lag=lag_n, flip=-1, gy=STEP_Y)
    draw_water(c, 0, wl, T, None, 150)
    st.draw(c)
    c.restore()
    fl = max(180 * math.exp(-(t - 14.0) * 12) if t >= 14.0 else 0, 130 * math.exp(-(t - 14.26) * 14) if t >= 14.26 else 0)
    finish(c, T, pal_at(T), rain=clamp((t - 14.2) / 5.5), grade=.4, vig=125, flash=fl / 255)
    draw_caps(c, 'S1', t)
    fades(c, t, 24, .35, .6)

# ====================================================================== S2  SWEPT AWAY (22 s)
def wave_x(t): return KX + 330 * (t - 4.8)
def wave_amp(t): return 90 * smooth((t - 2.3) / 1.2) * (1 - smooth((t - 6.8) / 2.5))
WL2 = 576

def _foam():
    ev = []
    for k in range(30):
        t = 3.2 + .1 * k
        x = wave_x(t)
        y = surf_y(x, START['S2'] + t, WL2, (x, wave_amp(t))) - 4
        ev.append((t, 'splash', x, y, 2, dict(up=True, gy=y + 40, power=.8)))
    ev += [(4.85, 'splash', KX, 520, 16, dict(gy=700, power=1.2)), (5.1, 'splash', NX, 520, 12, dict(gy=700, power=1.0)),
           (5.95, 'splash', 802, WL2 - 6, 14, dict(gy=700, power=1.1)),
           (10.4, 'sweat', NX - 22, STEP_Y - 120, 1, dict(vx=-8, vy=10)), (11.3, 'sweat', NX + 22, STEP_Y - 120, 1, dict(vx=8, vy=10))]
    return ev
SIMEV['S2'] = _foam()
cap('S2', 0.6, 2.4, 'L', 'The current is so strong!')
cap('S2', 2.5, 4.1, 'R', 'Hold on!')
cap('S2', 5.1, 6.7, 'L', 'KANAAAN!', shout=True)
cap('S2', 7.0, 9.4, 'R', 'KALIWAAA!', shout=True)
cap('S2', 11.0, 12.5, 'R', 'Promise...')
cap('S2', 14.2, 16.0, 'L', 'Kanan...')
cap('S2', 18.0, 19.7, 'L', "I'll come home!")
sf('S2', 0.0, 'whoosh', dur=2.5, amp=.25)
sf('S2', 3.4, 'whoosh', dur=1.6, amp=.7, rise=1)
sf('S2', 4.85, 'splash', amp=1.0); sf('S2', 4.95, 'boing', amp=.6, up=1); sf('S2', 5.1, 'splash', amp=.7)
sf('S2', 5.95, 'splash', amp=.8)
sf('S2', 7.2, 'boing', amp=.5, up=1)
sf('S2', 13.0, 'splash', amp=.15)
sf('S2', 20.6, 'thud', f=110, amp=.35)

def _kan2(t):
    """Kanan during the wave scene (returns pose, face, lag)."""
    lag = (0, 0)
    if t < 2.5:
        br = .012 * math.sin(2 * math.pi * .7 * t + 1)
        p = dict(rot=0, sx=1 / (1 + br), sy=1 + br, air=0)
        f = fc(t, 1.1, brow=.8, mouth='flat', px=-.5)
    elif t < 4.9:
        k = ease_io((t - 2.5) / 1.0)
        sy = lerp(1, .9, k)
        p = dict(rot=0, sx=1 / sy, sy=sy, air=0)
        f = fc(t, 1.1, es=1.2, mouth='grit', brow=-.6, px=-.7)
    elif t < 6.2:
        k = out_back((t - 4.9) / .5)
        sy = lerp(.9, 1.45, clamp(k, 0, 1.3)); rt = lerp(0, 22, ease_out((t - 4.9) / .45))
        p = dict(rot=rt, sx=1 / sy, sy=sy, air=0)
        f = dict(es=1.5, mouth='open', mo=1, brow=1, px=1, py=-.3)
        lag = (-16, 4)
    elif t < 7.0:
        k = ease_io((t - 6.2) / .8)
        sy = lerp(1.45, .95, k)
        p = dict(rot=lerp(22, 0, k), sx=1 / sy, sy=sy, air=0)
        f = dict(es=1.4, mouth='open', mo=.7, brow=1, px=1)
    elif t < 9.5:
        p = hop_pose(t, 7.0, NX, NX, 60, ant=.12, air=.5, land=.1, rec=.5, squash=.7)
        if p is None:
            p = dict(rot=0, sx=1, sy=1, air=0)
        f = dict(es=1.7, mouth='open', mo=1, brow=1, px=1)
    else:
        k = ease_io((t - 9.5) / 2.0)
        sy = lerp(1, .84, k)
        p = dict(rot=-7 * k, sx=1 / sy, sy=sy, air=0)
        f = fc(t, 1.1, open=.55, mouth='sad', brow=1, px=1, py=.5)
        lag = (0, 18 * k)
    return p, f, lag

def s2(c, t, st):
    st.advance_to(t)
    T = START['S2'] + t
    if t < 13.0:
        pal = bg(c, T, 0, house_lit=1.0)
        wave = (wave_x(t), wave_amp(t))
        # Kaliwa
        if t < 4.8:
            if t < 4.2:
                br = .012 * math.sin(2 * math.pi * .7 * t)
                pk = dict(rot=2.2 * math.sin(t * 42) if t > .3 else 0, sx=1 / (1 + br), sy=1 + br, air=0)
                fk = fc(t, .3, es=1.15 if t < 3.2 else 1.4, mouth='wobble' if t < 3.2 else 'o', mo=.5, brow=1,
                        px=.6 if t < 3.2 else -1)
            else:
                k = ease_io((t - 4.2) / .55)
                sy = lerp(1, .72, k)
                pk = dict(rot=-6 * k, sx=1 / sy, sy=sy, air=0)
                fk = dict(es=1.4, mouth='o', mo=.8, brow=1, px=-1)
            draw_char(c, KX, STEP_Y, pk, fk, 'L', gy=STEP_Y)
        else:
            u = t - 4.8
            if u < 1.15:
                v = u / 1.15
                xc = KX + 430 * v
                yc = lerp(STEP_Y - 95 * S, WL2 - 8, v) - 160 * 4 * v * (1 - v)
                rot = 62 * smooth(v) + 360 * smooth(v)
            else:
                d = t - 5.95
                xc = 802 + 90 * d + 120 * d * d
                yc = surf_y(xc, T, WL2, wave) - 8
                rot = 62 + 7 * math.sin(3 * t)
            if xc < 1450:
                fk = dict(es=1.45, mouth='open', mo=.6 + .4 * math.sin(t * 14), brow=1, px=-1, py=-.4)
                slipper(c, xc, yc + 95 * S, s=S, rot=rot, sx=.84 if u < 1.15 else 1, sy=1.2 if u < 1.15 else 1,
                        pivot=95, kind='L', face=fk, lag=(-14 if u < 1.15 else -6, 6))
        pn, fn_, lagn = _kan2(t)
        draw_char(c, NX, STEP_Y, pn, fn_, 'R', lag=lagn, flip=-1, gy=STEP_Y)
        draw_water(c, 0, WL2, T, wave, 150)
        st.draw(c)
        finish(c, T, pal_at(T), rain=1.0, grade=.4, vig=125)
        a = smooth((t - 12.3) / .55)
    else:
        cam = 1000 + 750 * ease_io((t - 13.0) / 8.8)
        sxk = lerp(520 + 22 * math.sin(.9 * t), 550, smooth((t - 19) / 2.5))
        xw = cam + sxk
        pal = bg(c, T, cam)
        wl = 583 if t < 19 else lerp(583, 730, ease_io((t - 19) / 2.8))
        # drifting debris (sachets, bottle)
        for i, (x0, kind) in enumerate(((1200, 0), (1380, 1), (1620, 0), (1900, 2), (2100, 0))):
            xd = x0 + 55 * (t - 13)
            yd = surf_y(xd, T, 583) - 6 + 3 * math.sin(t * 3 + i)
            if wl < 700 and t > 20:
                yd = min(yd + 0, GY + 20)
            sx_ = xd - cam
            if -60 < sx_ < W + 60 and wl < 700:
                continue
            if -60 < sx_ < W + 60:
                if kind == 0:
                    c.drawRect(R(sx_ - 12, yd - 8, 24, 14), fill((235, 70, 70))); c.drawRect(R(sx_ - 12, yd - 8, 24, 14), stroke((255, 255, 255), 2))
                elif kind == 1:
                    rrect(c, sx_ - 5, yd - 36, 10, 40, 4, fill((120, 200, 230, ), 220))
                else:
                    c.drawOval(R(sx_ - 28, yd - 8, 56, 14), fill((100, 190, 100)))
        cyc = min(surf_y(xw, T, wl) - 8, GY - 34)
        rot = lerp(62 + 8 * math.sin(2 * t), 85, smooth((t - 19.3) / 1.5))
        if t < 17.0:
            fk = fc(t, .3, es=1.2, mouth='sad', brow=1, px=-.8, py=.2)
        elif t < 19.8:
            fk = fc(t, .3, es=1.1, mouth='grit', brow=-1, px=-.4)
        elif t < 20.6:
            fk = dict(open=.5, mouth='wobble', brow=.5)
        else:
            fk = dict(open=.6, mouth='wobble', brow=0, px=math.cos(5 * t), py=math.sin(5 * t))
        slipper(c, sxk, cyc + 95 * S, s=S, rot=rot, pivot=95, kind='L', face=fk, lag=(-5, 4))
        if t > 20.4:
            dizzy(c, t, sxk, cyc - 70, 255 * smooth((t - 20.4) / .4))
        draw_water(c, cam, wl, T, None, 150)
        finish(c, T, pal_at(T), rain=1.0, grade=.4, vig=125)
        a = 1 - smooth((t - 13.0) / .55)
    draw_caps(c, 'S2', t)
    fade_black(c, a)
    if t > 21.7:
        fade_black(c, (t - 21.7) / .3 * 0.0)

# ====================================================================== S3  LOST (20 s)
H3 = [dict(t0=10.4, x0=2300, x1=2275, h=30, ant=.35, air=.45, land=.14, rec=.3, squash=.7),
      dict(t0=14.2, x0=2275, x1=2210, h=65, ant=.22, air=.55, land=.12, rec=.32, squash=.68),
      dict(t0=17.0, x0=2210, x1=2090, h=130, ant=.3, air=.7, land=.12, rec=.36, squash=.64)]
cap('S3', 4.0, 5.8, 'L', 'Where am I...?')
cap('S3', 6.2, 8.0, 'R', 'Promise...')
cap('S3', 8.6, 10.2, 'L', "I'll come home!")
cap('S3', 12.2, 13.5, 'L', 'Ouch!')
cap('S3', 17.0, 18.9, 'L', 'I can do this!')
hop_sfx('S3', H3)
sf('S3', 11.34, 'thud', f=90, amp=.7); sf('S3', 11.9, 'thud', f=70, amp=.5)
sf('S3', 3.2, 'squish', amp=.4); sf('S3', 3.7, 'boing', amp=.4, up=1)
sf('S3', 8.7, 'boing', amp=.4, up=1)
SIMEV['S3'] = [(6.8, 'sweat', 2300 - 20, GY - 95, 1, dict(vx=-6, vy=10)), (7.4, 'sweat', 2300 + 20, GY - 95, 1, dict(vx=6, vy=10))]

def K3(t):
    if t < 10.4:
        if t < 2.4:
            rot = 85 + 3 * math.sin(t * 5) * math.exp(-t * .5)
        elif t < 4.9:
            rot = kf(t, [(2.4, 85), (2.9, 92), (3.7, -14), (4.3, 7), (4.9, 0)])
        else:
            rot = 0
        k = clamp(rot / 85) if rot > 0 else 0
        br = .012 * math.sin(2 * math.pi * .7 * t) if t > 4.9 else 0
        sy = 1 + br
        if 8.6 <= t < 9.4:
            sy = kf(t, [(8.6, 1), (8.85, 1.25), (9.4, 1.0)])
        return dict(x=2300, by=GY + 38 * k, rot=rot, sx=1 / sy, sy=sy, pivot=95 * k, air=0, phase='idle')
    p = hop_track(t, H3, 2300)
    p = dict(p); p['by'] = GY; p['pivot'] = 0
    if 11.34 <= t < 14.2:
        rot = kf(t, [(11.34, 0), (11.85, -90), (12.0, -83), (13.3, -86), (13.75, -3), (14.2, 0)])
        k = clamp(-rot / 85) if rot < 0 else 0
        p.update(x=2275, rot=rot, sx=1, sy=1, air=0, by=GY + 38 * k, pivot=95 * k)
    if t >= 15.09:
        tau = t - 15.09
        if tau < .9:
            p['rot'] += 10 * math.exp(-5 * tau) * math.sin(2 * math.pi * 3 * tau)
    return p

def s3(c, t, st):
    st.advance_to(t)
    T = START['S3'] + t
    pk = K3(t)
    cam = 1750 + (K3(max(0, t - .15))['x'] - 2300) * .6
    pal = bg(c, T, cam)
    if 16.7 < t < 18.3:
        arc_guide(c, cam, 2210, 2090, GY, 130, 170 * smooth((t - 16.7) / .3) * (1 - smooth((t - 17.9) / .4)))
    x = pk['x'] - cam
    # face
    if t < 2.4:
        fk = dict(open=.5, mouth='wobble', px=math.cos(5 * t), py=math.sin(5 * t), brow=.4)
    elif t < 4.0:
        fk = dict(open=.7, mouth='wobble', px=math.cos(5 * t) * (1 - (t - 2.4) / 1.6), py=math.sin(5 * t) * (1 - (t - 2.4) / 1.6))
    elif t < 5.9:
        fk = fc(t, .3, es=1.15, mouth='o', mo=.5, brow=.8, px=math.sin((t - 4) * 2.2) * 1.0)
    elif t < 8.6:
        fk = fc(t, .3, mouth='sad', brow=1, px=.4, py=-.6)
    elif t < 10.4:
        fk = fc(t, .3, es=1.12, mouth='grit', brow=-1)
    elif t < 11.2:
        fk = fc(t, .3, es=1.1, mouth='grit', brow=-.6)
    elif 11.34 <= t < 14.0:
        fk = dict(open=.45, mouth='wobble', brow=.5, px=math.cos(6 * t), py=math.sin(6 * t))
    elif t < 14.2:
        fk = fc(t, .3, mouth='grit', brow=-.6)
    elif t < 17.0:
        fk = fc(t, .3, es=1.1, mouth='grit', brow=-.5) if pk['phase'] != 'air' else dict(es=1.2, mouth='open', mo=.6, brow=.2)
    else:
        fk = dict(es=1.15, mouth='big', mo=.8, brow=-.3) if pk['phase'] == 'air' else fc(t, .3, es=1.15, mouth='big', mo=.5, brow=-.4)
    lag = lagvec(lambda q: (K3(max(0, q))['x'], K3(max(0, q))['air']), t, 1.6)
    # shadow stays on the ground
    if pk['pivot'] == 0:
        shadow(c, x, GY, pk.get('air', 0))
    slipper(c, x, pk['by'] - pk.get('air', 0), s=S, rot=pk['rot'], sx=pk['sx'], sy=pk['sy'], pivot=pk['pivot'], kind='L',
            face=fk, lag=lag)
    if (t < 3.3) or (11.5 < t < 13.4):
        top = GY - (95 * S + 20 if pk['pivot'] > 50 else 160 * S)
        dizzy(c, t, x, top if pk['pivot'] > 50 else top, 255)
    # thought bubble about Kanan
    if 5.8 < t < 8.4:
        a = smooth((t - 5.8) / .4) * (1 - smooth((t - 8.0) / .4))
        bx, by = x + 90, GY - 270
        c.saveLayerAlpha(None, int(255 * a))
        bubble(c, bx, by, 230, 150)
        c.save(); c.clipPath(_oval(bx, by, 113, 73), skia.ClipOp.kIntersect, True)
        c.drawRect(R(bx - 120, by - 80, 240, 160), fill((255, 226, 176)))
        c.drawRect(R(bx - 120, by + 38, 240, 40), fill((190, 170, 150)))
        c.drawRect(R(bx - 60, by + 30, 120, 14), fill((220, 205, 190)))
        bobb = .02 * math.sin(t * 5)
        slipper(c, bx, by + 32, s=.34, kind='R', flip=-1, sy=1 + bobb, sx=1 / (1 + bobb), face=dict(mouth='smile', es=1.05))
        c.restore()
        c.restoreToCount(c.getSaveCount() - 1) if False else None
        c.restore()
    st.draw_world(c, cam) if hasattr(st, 'draw_world') else None
    c.save(); c.translate(-cam, 0); st.draw(c); c.restore()
    finish(c, T, pal_at(T), rain=.75, grade=.4, vig=125)
    draw_caps(c, 'S3', t)
    fades(c, t, 20, .3, .4)

def _oval(cx, cy, rx, ry):
    p = skia.Path(); p.addOval(R(cx - rx, cy - ry, 2 * rx, 2 * ry)); return p

# ====================================================================== S4  THE POND (30 s)
H4 = [dict(t0=1.0, x0=2090, x1=2040, h=45), dict(t0=2.9, x0=2040, x1=1990, h=45),
      dict(t0=14.0, x0=1990, x1=1625, h=200, ant=.45, air=.95, land=.14, rec=.4, squash=.6),
      dict(t0=21.0, x0=1625, x1=1650, h=75, ant=.1, air=.35, land=.1, rec=.3, squash=.75),
      dict(t0=25.5, x0=1650, x1=1540, h=60, ant=.2, air=.5, land=.12, rec=.3),
      dict(t0=27.6, x0=1540, x1=1460, h=60, ant=.2, air=.5, land=.12, rec=.3)]
cap('S4', 4.2, 5.6, 'L', 'Whoa... it is so wide!')
cap('S4', 6.0, 7.7, 'L', "I can't do this...")
cap('S4', 9.4, 11.5, 'L', 'But Kanan is waiting.')
cap('S4', 11.9, 13.8, 'L', 'One... two... THREE!')
cap('S4', 16.2, 17.8, 'L', 'I did it!')
cap('S4', 21.1, 22.4, 'L', 'Whoa, a coconut!')
cap('S4', 23.8, 25.3, 'L', 'Okay, keep going.')
hop_sfx('S4', H4)
sf('S4', 8.0, 'squish', amp=.35); sf('S4', 14.0 + .45, 'boing', amp=.8, up=1)
sf('S4', 14.0 + .45 + .95, 'thud', f=140, amp=.7); sf('S4', 4.3, 'chime', amp=.2)
sf('S4', 20.9, 'thud', f=120, amp=.8); sf('S4', 21.35, 'thud', f=140, amp=.4); sf('S4', 21.65, 'thud', f=160, amp=.25)
SIMEV['S4'] = ([(11.2 + .5 * i, 'sweat', 1990 - 14, GY - 120, 1, dict(vx=-40 + 80 * (i % 2), vy=110)) for i in range(4)] +
               [(15.45, 'spark', 1625, GY - 90, 14)])

def coco_state(t):
    g = 1500.0; h0 = GY + 70
    u = t - 20.0
    if u < 0:
        return None
    tf = math.sqrt(2 * h0 / g)
    if u < tf:
        return -70 + .5 * g * u * u, 1.0, 1.0
    v = g * tf; u -= tf
    while True:
        v *= .48
        tb = 2 * v / g
        if tb < .05 or v < 50:
            return GY, 1.0, 1.0
        if u < tb:
            return GY - (v * u - .5 * g * u * u), 1.0, 1.0
        u -= tb

def X4(t):
    return hop_track(t, H4, 2090)

def s4(c, t, st):
    st.advance_to(t)
    T = START['S4'] + t
    pk = dict(X4(t))
    cam = X4(max(0, t - .3))['x'] - 520
    pal = bg(c, T, cam)
    # pre-jump squash (fake-out) 8.0-8.6
    if pk['phase'] == 'idle' and 8.0 <= t < 8.7:
        sy = kf(t, [(8.0, 1), (8.35, .74), (8.7, 1)], ease_io)
        pk.update(sy=sy, sx=1 / sy, rot=-4 * (1 - sy) / .26)
    if pk['phase'] == 'idle' and 4.4 <= t < 5.2:
        pk['rot'] = -6 * smooth((t - 4.4) / .4)
    if pk['phase'] == 'idle' and 5.6 <= t < 8.0:
        pk['rot'] = -9 * smooth((t - 5.6) / 1.0)
    if pk['phase'] == 'idle' and 8.7 <= t < 11.0:
        pk['rot'] = -9 * (1 - smooth((t - 8.7) / .6)) + 0
    if pk['phase'] == 'idle' and 11.0 <= t < 14.0:
        k = smooth((t - 11.0) / 2.0)
        pk['sy'] = 1 - .08 * k; pk['sx'] = 1 / pk['sy']
    # face
    ph = pk['phase']
    if t < 1.0:
        fk = fc(t, .3, mouth='sad', brow=.5, open=.7)
    elif t < 4.2:
        fk = fc(t, .3, mouth='smile', brow=-.3)
    elif t < 5.8:
        fk = dict(es=1.35, mouth='o', mo=.7, brow=1, px=-.8)
    elif t < 8.0:
        fk = fc(t, .3, es=1.1, mouth='wobble', brow=1, py=.9, px=-.6)
    elif t < 8.7:
        fk = dict(es=1.0, mouth='grit', brow=-.8, px=-.6)
    elif t < 11.0:
        fk = fc(t, .3, mouth='sad', brow=1, px=math.sin((t - 8.7) * 8) * math.exp(-(t - 8.7) * .8))
    elif t < 14.0:
        fk = fc(t, .3, es=1.15, mouth='grit', brow=-1, px=-.7)
    elif ph in ('ant', 'air'):
        fk = dict(es=1.25, mouth='open', mo=.5, brow=-.4, px=-.5) if ph == 'air' else dict(es=1.1, mouth='grit', brow=-1)
    elif t < 17.8:
        fk = fc(t, .3, es=1.2, mouth='big', mo=.8, brow=-.4)
    elif 21.0 <= t < 23.0:
        fk = dict(es=1.6, mouth='open', mo=1, brow=1, px=1) if t < 21.9 else fc(t, .3, es=1.2, mouth='o', mo=.4, brow=.6)
    else:
        fk = fc(t, .3, es=1.05, mouth='smile', brow=-.2)
    lag = lagvec(lambda q: (X4(max(0, q))['x'], X4(max(0, q)).get('air', 0)), t, 1.6)
    # arc guide (arcs) shown while preparing the big jump
    if 13.0 < t < 15.6:
        arc_guide(c, cam, 1990, 1625, GY, 200, 190 * smooth((t - 13.0) / .4) * (1 - smooth((t - 15.1) / .5)),
                  upto=clamp((t - 14.4) / .95) if t > 14.4 else 0.0 + (1.0 if t < 14.4 else 0))
    x = pk['x'] - cam
    shadow(c, x, GY, pk.get('air', 0))
    slipper(c, x, GY - pk.get('air', 0), s=S, rot=pk['rot'], sx=pk['sx'], sy=pk['sy'], kind='L', face=fk, lag=lag)
    # leaf (light) and coconut (heavy) -> timing contrast
    if t > 19.6:
        u = t - 19.6
        ly = min(GY - 8, -50 + 95 * u)
        lx = 1640 + (70 * math.sin(1.8 * u) if ly < GY - 8 else 70 * math.sin(1.8 * ((GY - 8 + 50) / 95)))
        rt = 28 * math.sin(1.8 * u + 1) if ly < GY - 8 else 4
        leaf(c, lx - cam, ly, rt)
    cs = coco_state(t)
    if cs is not None:
        y, sxc, syc = cs
        coconut(c, 1585 - cam, y, sxc, syc)
    if cs is not None and abs(cs[0] - GY) < 1 and 20.88 < t < 20.97:
        pass
    c.save(); c.translate(-cam, 0); st.draw(c); c.restore()
    k = clamp((t - 0) / 30)
    finish(c, T, pal_at(T), rain=lerp(.6, .25, k), grade=.35, vig=125)
    draw_caps(c, 'S4', t)
    fades(c, t, 30, .35, .4)

# ====================================================================== S5  THE JEEPNEY (20 s)
H5 = [dict(t0=1.0, x0=1460, x1=1400, h=50), dict(t0=2.8, x0=1400, x1=1340, h=50),
      dict(t0=15.9, x0=1340, x1=1250, h=115, ant=.3, air=.6, land=.12, rec=.34, squash=.66),
      dict(t0=18.0, x0=1250, x1=1160, h=115, ant=.3, air=.6, land=.12, rec=.34, squash=.66)]
cap('S5', .5, 2.3, 'L', 'Still far, but I can do it.')
cap('S5', 3.0, 4.3, 'L', 'Just one more corner...')
cap('S5', 4.9, 6.6, 'N', 'BEEP BEEP!', shout=True)
cap('S5', 6.9, 8.6, 'L', "AAAH! I'M SOAKED!")
cap('S5', 11.2, 13.4, 'L', "I'm soaked... I'm so tired.")
cap('S5', 15.0, 16.8, 'L', "No. I won't give up.")
cap('S5', 18.4, 19.8, 'L', 'Wait for me, Kanan!')
hop_sfx('S5', H5)
sf('S5', 1.2, 'chime', amp=.15)
sf('S5', 4.6, 'whoosh', dur=3.0, amp=.9); sf('S5', 5.0, 'honk', amp=.7); sf('S5', 5.5, 'honk', amp=.7)
sf('S5', 5.32, 'splash', amp=1.0); sf('S5', 5.4, 'squish', amp=.6)
for i in range(6):
    sf('S5', 8.0 + .15 * i, 'boing', amp=.2, up=(i % 2))
sf('S5', 14.2, 'chime', amp=.4)
S5X = 1340
SIMEV['S5'] = ([(5.32, 'splash', 520 + 820, GY + 6, 46, dict(gy=GY + 80, power=1.7))] +
               [(5.6 + .12 * i, 'sweat', 1340 - 18 + (i % 3) * 18, GY - 110, 1, dict(vx=-30 + 30 * (i % 3), vy=60)) for i in range(18)] +
               [(8.0 + .09 * i, 'sweat', 1340 + (i % 2) * 24 - 12, GY - 120, 2, dict(vx=(-190 if i % 2 else 190), vy=100)) for i in range(11)] +
               [(14.9, 'spark', 1340, GY - 100, 10)])

def jeep_x(t):
    return lerp(-440, 1720, ease_in(clamp((t - 4.5) / 3.0)) * .25 + clamp((t - 4.5) / 3.0) * .75)

def K5(t):
    p = dict(hop_track(t, H5, 1460))
    p.setdefault('rot', 0)
    ph = p['phase']
    if ph == 'idle':
        if 5.28 <= t < 8.0:
            u = t - 5.28
            sy = kf(t, [(5.28, 1), (5.45, .48), (6.4, .6), (7.4, .88), (8.0, 1.0)], ease_out) if u < 1.0 else lerp(.6, 1, ease_io((t - 6.28) / 1.7))
            rot = 28 * math.exp(-u * 2.2) * math.cos(u * 8)
            p.update(sy=sy, sx=1 / sy, rot=rot, x=1340 + 46 * math.exp(-u * 3) * math.sin(min(1, u * 5) * 1.6))
        elif 8.0 <= t < 9.2:
            u = t - 8.0
            p.update(rot=16 * math.exp(-u * 1.8) * math.sin(u * 40), x=1340 + 5 * math.sin(u * 40) * math.exp(-u * 2))
        elif 11.0 <= t < 15.9:
            k = smooth((t - 11.0) / 1.2)
            sy = 1 - .12 * k * (1 - smooth((t - 15.0) / .8)); p.update(sy=sy, sx=1 / sy, rot=-5 * k * (1 - smooth((t - 14.8) / .8)))
    return p

def s5(c, t, st):
    st.advance_to(t)
    T = START['S5'] + t
    pk = K5(t)
    cam = (X4_end := 1460) - 520 if t < 0 else None
    cam = min(1460 - 520, X5c(t))
    pal = bg(c, T, cam)
    # staged spotlight from broken clouds (staging)
    sp = smooth((t - 13.6) / 1.2)
    # puddle under the splash point
    oval(c, 1340 - cam, GY + 28, 150, 12, fill(mix(pal['sky_bot'], pal['road'], .35), 210))
    fk = None
    ph = pk['phase']
    if t < 2.3:
        fk = fc(t, .3, mouth='smile', brow=-.2, open=.8)
    elif t < 4.5:
        fk = fc(t, .3, mouth='smile', brow=-.3)
    elif t < 5.28:
        fk = dict(es=1.45, mouth='o', mo=.9, brow=1, px=-1)
    elif t < 6.9:
        fk = dict(open=.12, mouth='open', mo=1, brow=1)
    elif t < 8.9:
        fk = dict(es=1.4, mouth='open', mo=.8 + .2 * math.sin(t * 20), brow=1, px=1)
    elif t < 11.0:
        fk = fc(t, .3, es=1.0, mouth='wobble', brow=.8, open=.7)
    elif t < 14.4:
        fk = fc(t, .3, es=1.0, mouth='sad', brow=1, py=.7, open=.7)
    elif t < 15.9:
        fk = fc(t, .3, es=1.15, mouth='smile', brow=-.2, py=-1)
    elif ph == 'air':
        fk = dict(es=1.2, mouth='big', mo=.7, brow=-.5)
    else:
        fk = fc(t, .3, es=1.1, mouth='grit', brow=-1) if t < 18.4 else fc(t, .3, es=1.1, mouth='big', mo=.5, brow=-.4)
    lag = lagvec(lambda q: (K5(max(0, q))['x'], K5(max(0, q)).get('air', 0)), t, 1.6)
    if t >= 8.0 and t < 14.0:
        lag = (lag[0], lag[1] + 12 * smooth((t - 9.0) / 1.0))
    # light beam
    if sp > 0.01:
        bx = pk['x'] - cam
        p = skia.Paint(); p.setAntiAlias(True)
        p.setShader(lin(bx, 0, bx, GY, (255, 244, 196), (255, 244, 196), 0, 120 * sp))
        c.drawPath(poly([(bx - 60, 0), (bx + 60, 0), (bx + 150, GY), (bx - 150, GY)]), p)
    x = pk['x'] - cam
    shadow(c, x, GY, pk.get('air', 0))
    slipper(c, x, GY - pk.get('air', 0), s=S, rot=pk['rot'], sx=pk['sx'], sy=pk['sy'], kind='L', face=fk, lag=lag)
    c.save(); c.translate(-cam, 0); st.draw(c); c.restore()
    # jeepney in the near lane
    if 4.4 < t < 7.6:
        xj = jeep_x(t)
        # headlight cone
        pj = skia.Paint(); pj.setAntiAlias(True); pj.setShader(lin(xj + 240, GY, xj + 760, GY, (255, 250, 200), (255, 250, 200), 150, 0))
        c.drawPath(poly([(xj + 240, GY + 28), (xj + 760, GY - 30), (xj + 760, GY + 130), (xj + 240, GY + 52)]), pj)
        jeepney(c, xj, GY + 95, T, 1.0, face=1, pitch=-1.2 * math.sin(t * 22), wob=2.0 * math.sin(t * 40))
        # speed lines
        for i in range(6):
            yy = GY - 120 + i * 34
            c.drawLine(xj - 340 - i * 24, yy, xj - 230 - i * 24, yy, stroke((255, 255, 255), 3, 130))
    finish(c, T, pal_at(T), rain=lerp(.28, 0.0, clamp((t - 8.0) / 6.0)), grade=.35, vig=125)
    draw_caps(c, 'S5', t)
    fades(c, t, 20, .35, .4)

def X5c(t):
    return K5(max(0, t - .3))['x'] - 520

# ====================================================================== S6  REUNION (22 s)
H6K = [dict(t0=.2, x0=1340, x1=1170, h=45), dict(t0=1.4, x0=1170, x1=1000, h=45), dict(t0=2.6, x0=1000, x1=830, h=45),
       dict(t0=3.8, x0=830, x1=660, h=45),
       dict(t0=5.4, x0=660, x1=515, h=175, ant=.5, air=.85, land=.12, rec=.45, squash=.62),
       dict(t0=13.0, x0=515, x1=372, h=135, ant=.3, air=.7, land=.12, rec=.36, squash=.66)]
H6N = [dict(t0=5.0, x0=462, x1=440, h=40, ant=.15, air=.35, land=.1, rec=.3, squash=.78),
       dict(t0=18.6, x0=440, x1=462, h=45, ant=.2, air=.4, land=.1, rec=.34, squash=.75)]
cap('S6', 4.4, 5.3, 'R', 'Kaliwa...?')
cap('S6', 7.6, 9.2, 'L', 'I promised, remember? Together.')
cap('S6', 9.4, 11.4, 'R', "I thought you weren't coming back...")
cap('S6', 11.6, 13.2, 'L', "I would never leave you, Kanan.")
cap('S6', 13.6, 15.6, 'R', "Let's sing our song now.")
hop_sfx('S6', H6K + H6N, big=.9)
sf('S6', 4.45, 'chime', amp=.35)
sf('S6', 15.0, 'hum', vol=.7, dur=6.5)
sf('S6', 7.6, 'chime', amp=.4)
SIMEV['S6'] = ([(7.9 + .3 * i, 'heart', 478, STEP_Y - 190, 1) for i in range(12)] +
               [(15.2 + .55 * i, 'note', (KX if i % 2 == 0 else NX), STEP_Y - 200, 1, dict(col=(BLUE_L if i % 2 == 0 else (255, 170, 205)))) for i in range(10)] +
               [(6.9, 'spark', 478, STEP_Y - 120, 12)])

def kbase(x):
    return ground_y(x)

def s6(c, t, st):
    st.advance_to(t)
    T = START['S6'] + t
    pal = bg(c, T, 0, house_lit=1.0, tind_lit=0.5)
    pkK = hop_track(t, H6K, 1340)
    pkN = hop_track(t, H6N, NX)
    # Kanan waits sadly, then notices Kaliwa coming back from the right
    if pkN['phase'] == 'idle' and t < 4.3:
        k = smooth(t / 1.2)
        sy = 1 - .1 * k
        pkN.update(sy=sy, sx=1 / sy, rot=5 * k)
    if pkN['phase'] == 'idle' and 4.3 <= t < 5.0:
        sy = kf(t, [(4.3, .9), (4.55, 1.38), (5.0, 1.0)], ease_out)
        pkN.update(sy=sy, sx=1 / sy, rot=5 * (1 - smooth((t - 4.3) / .5)))
    xk = pkK['x']
    xn = pkN['x']
    by_k = kbase(xk)
    # who is on the right? (Kaliwa returns from the right and hops over Kanan at 13.0)
    sgn = 1 if xk < xn else -1            # +1: Kaliwa on the left of Kanan
    leanw = smooth((t - 7.6) / .6) * (1 - smooth((t - 12.8) / .3)) + smooth((t - 14.4) / .5) * (1 - smooth((t - 17.4) / .8))
    sway = math.sin(2 * math.pi * .55 * (t - 15.0)) * smooth((t - 15.0) / .6) * (1 - smooth((t - 19.0) / .8)) * 6
    lean_sgn = -1 if t < 13.7 else 1
    rk = pkK['rot'] + (lean_sgn * 9 * leanw + sway if t > 7.4 else 0)
    rn = pkN['rot'] + (-lean_sgn * 9 * leanw + sway if t > 7.4 else 0)
    flipN = 1 if xk > xn else -1          # Kanan always faces Kaliwa
    lookN = 1 if xk > xn else -1          # pupils toward Kaliwa
    lookK = -lookN
    # Kanan's face (she looks toward where Kaliwa was swept: the right)
    if t < 4.3:
        fkn = fc(t, 1.1, mouth='sad', brow=1, px=.9, py=.2, open=.7)
    elif t < 6.9:
        fkn = dict(es=1.7, mouth='open', mo=1, brow=1, px=lookN)
    elif t < 7.6:
        fkn = dict(es=1.3, mouth='big', mo=.7, brow=-.2, px=lookN * .7)
    elif t < 15.0:
        fkn = dict(open=.04, happyclose=True, mouth='big', mo=.4) if 8.0 < t < 9.2 else fc(t, 1.1, es=1.1, mouth='smile', px=lookN * .6, open=.9)
        if 9.4 < t < 11.4:
            fkn = fc(t, 1.1, es=1.2, mouth='wobble', brow=.8, px=lookN * .6)
    else:
        fkn = dict(open=.04, happyclose=True, mouth='big', mo=.4 + .3 * math.sin(t * 7 + 1))
    # Kaliwa's face (he looks left toward home, then at Kanan)
    if t < 3.8:
        fkk = fc(t, .3, mouth='sad', brow=.6, open=.75, px=-.8)
    elif t < 5.4:
        fkk = dict(es=1.5, mouth='open', mo=1, brow=1, px=lookK, py=-.3)
    elif pkK['phase'] in ('air', 'ant'):
        fkk = dict(es=1.3, mouth='big', mo=.8, brow=-.2, px=lookK)
    elif t < 15.0:
        fkk = fc(t, .3, es=1.1, mouth='big', mo=.5, px=lookK * .6) if t < 13.2 else fc(t, .3, mouth='smile', px=lookK * .4)
    else:
        fkk = dict(open=.04, happyclose=True, mouth='big', mo=.4 + .3 * math.sin(t * 7))
    lagK = lagvec(lambda q: (hop_track(max(0, q), H6K, 1340)['x'], hop_track(max(0, q), H6K, 1340).get('air', 0)), t, 1.6)
    lagN = lagvec(lambda q: (hop_track(max(0, q), H6N, NX)['x'], hop_track(max(0, q), H6N, NX).get('air', 0)), t, 1.6)
    shadow(c, xn, kbase(xn), pkN.get('air', 0)); shadow(c, xk, by_k, pkK.get('air', 0))
    slipper(c, xn, kbase(xn) - pkN.get('air', 0), s=S, rot=rn, sx=pkN['sx'], sy=pkN['sy'], kind='R', face=fkn, lag=lagN, flip=flipN)
    slipper(c, xk, by_k - pkK.get('air', 0), s=S, rot=rk, sx=pkK['sx'], sy=pkK['sy'], kind='L', face=fkk, lag=lagK)
    # thought bubble (Kanan imagines Kaliwa coming home)
    if 0.8 < t < 4.2:
        a = smooth((t - .8) / .4) * (1 - smooth((t - 3.8) / .4))
        bx, by = NX + 60, STEP_Y - 270
        c.saveLayerAlpha(None, int(255 * a))
        bubble(c, bx, by, 200, 130)
        sc_ = 1 + .12 * math.sin(t * 6)
        hp = skia.Path(); s_ = 20 * sc_
        hp.moveTo(0, s_ * .9); hp.cubicTo(-s_ * 1.4, -s_ * .1, -s_ * .7, -s_ * 1.1, 0, -s_ * .35)
        hp.cubicTo(s_ * .7, -s_ * 1.1, s_ * 1.4, -s_ * .1, 0, s_ * .9)
        c.save(); c.translate(bx, by); c.drawPath(hp, fill((255, 90, 130))); c.restore()
        c.restore()
    st.draw(c)
    finish(c, T, pal_at(T), rain=0, grade=.3, vig=120)
    draw_caps(c, 'S6', t)
    fades(c, t, 22, .4, .5)

# ====================================================================== S7  THE END + CREDITS (14 s)
H7K = [dict(t0=.8, x0=372, x1=372, h=80, ant=.2, air=.5, land=.12, rec=.32), dict(t0=2.1, x0=372, x1=372, h=95, ant=.22, air=.55, land=.12, rec=.36)]
H7N = [dict(t0=.86, x0=462, x1=462, h=80, ant=.2, air=.5, land=.12, rec=.32), dict(t0=2.16, x0=462, x1=462, h=95, ant=.22, air=.55, land=.12, rec=.36)]
hop_sfx('S7', H7K + H7N, big=.7)
sf('S7', 0.3, 'chime', amp=.4); sf('S7', 3.3, 'chime', amp=.5)
sf('S7', 4.0, 'hum', vol=.5, dur=8.5)
SIMEV['S7'] = ([(0.9, 'spark', 417, STEP_Y - 170, 16), (2.8, 'spark', 417, STEP_Y - 190, 22)] +
               [(1.0 + .45 * i, 'heart', 417, STEP_Y - 190, 1) for i in range(5)] +
               [(4.0 + .6 * i, 'note', (KX if i % 2 == 0 else NX), STEP_Y - 200, 1, dict(col=(BLUE_L if i % 2 == 0 else (255, 170, 205)))) for i in range(14)])
CREDITS = [('KALIWA', 54, True), ('A story of two slippers', 26, False), ('', 18, False),
           ('Created by  Albert Lawrence', 30, True),
           ('Music & sound effects: original, synthesized', 22, False),
           ('', 14, False), ('Thanks for watching!', 30, True)]

def s7(c, t, st):
    st.advance_to(t)
    T = START['S7'] + t
    pal = bg(c, T, 0, house_lit=0, tind_lit=0, lamp=0)
    pk = hop_track(t, H7K, KX); pn = hop_track(t, H7N, NX)
    sw = math.sin(2 * math.pi * .6 * t) * 4 * smooth((t - 3.2) / .5)
    # sunrise glow
    g = skia.Paint(); g.setAntiAlias(True); g.setShader(rad(1000, 260, 520, (255, 236, 170), (255, 236, 170), 150, 0)); c.drawRect(R(0, 0, W, H), g)
    shadow(c, KX, STEP_Y, pk.get('air', 0)); shadow(c, NX, STEP_Y, pn.get('air', 0))
    fk = dict(open=.04, happyclose=True, mouth='big', mo=.5) if (pk['phase'] in ('idle', 'rec', 'land') and 3.0 < t) else dict(es=1.2, mouth='big', mo=.8)
    fn_ = dict(open=.04, happyclose=True, mouth='big', mo=.5) if (pn['phase'] in ('idle', 'rec', 'land') and 3.0 < t) else dict(es=1.2, mouth='big', mo=.8)
    if t < .8:
        fk = fc(t, .3, mouth='big', mo=.5); fn_ = fc(t, 1.1, mouth='big', mo=.5)
    lagK = lagvec(lambda q: (hop_track(max(0, q), H7K, KX)['x'], hop_track(max(0, q), H7K, KX).get('air', 0)), t, 1.6)
    lagN = lagvec(lambda q: (hop_track(max(0, q), H7N, NX)['x'], hop_track(max(0, q), H7N, NX).get('air', 0)), t, 1.6)
    slipper(c, NX, STEP_Y - pn.get('air', 0), s=S, rot=pn['rot'] - sw, sx=pn['sx'], sy=pn['sy'], kind='R', face=fn_, lag=lagN, flip=-1)
    slipper(c, KX, STEP_Y - pk.get('air', 0), s=S, rot=pk['rot'] + sw, sx=pk['sx'], sy=pk['sy'], kind='L', face=fk, lag=lagK)
    st.draw(c)
    finish(c, T, pal_at(T), rain=0, grade=0, vig=90)
    # THE END card
    if 3.2 <= t < 4.2:
        u = (t - 3.2) / 1.0
        tx = smooth(u / .4) * (1 - smooth((u - .7) / .3))
        sy = spring(clamp(u / .6), 2.4, 6.0) if u < .6 else 1
        c.save(); c.translate(640, 190); c.scale(1, sy if sy > 0 else .01)
        text(c, 'THE END', 0, 0, 120, (255, 244, 170), 255 * tx, outline=(70, 24, 50), ow=14)
        c.restore()
    # credits (right side so the characters stay visible)
    if t >= 4.0:
        a = smooth((t - 4.0) / .8)
        rrect(c, 640, 70, 600, 470, 28, fill((10, 12, 30), 165 * a))
        y = 150
        for i, (ln, sz, b) in enumerate(CREDITS):
            appear = 4.4 + i * .45
            la = smooth((t - appear) / .5)
            if ln:
                text(c, ln, 940, y + sz * .35 - (1 - la) * 14, sz, (255, 244, 200) if b else (230, 236, 255), 255 * la * a, bold=b)
            y += sz + 22
    fades(c, t, 14, .4, .8)
