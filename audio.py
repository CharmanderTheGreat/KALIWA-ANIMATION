"""Synthesised soundtrack for 'Si Kaliwa' (music, ambience, sound effects). Everything is generated here."""
import math, wave
import numpy as np
import story

SR = 44100
TOTAL = story.TOTAL
N = int(SR * (TOTAL + 0.5))
mix = np.zeros(N, dtype=np.float64)
rng = np.random.default_rng(11)

def add(t0, sig, amp=1.0):
    i0 = int(t0 * SR)
    if i0 >= N or i0 + len(sig) <= 0:
        return
    a = max(0, -i0)
    b = min(len(sig), N - i0)
    mix[i0 + a:i0 + b] += sig[a:b] * amp

def t_(d):
    return np.arange(int(d * SR)) / SR

def env_ad(n, a=.005, d=.2, curve=3.0):
    t = np.arange(n) / SR
    e = np.minimum(1, t / max(a, 1e-4)) * np.exp(-t * curve / max(d, 1e-3))
    return e

def bandpass_noise(d, lo, hi):
    n = int(d * SR)
    x = rng.standard_normal(n)
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(n, 1 / SR)
    X[(f < lo) | (f > hi)] = 0
    y = np.fft.irfft(X, n)
    return y / (np.max(np.abs(y)) + 1e-9)

def sweep(f0, f1, d, curve=1.0):
    t = t_(d)
    k = (t / d) ** curve
    f = f0 + (f1 - f0) * k
    ph = 2 * np.pi * np.cumsum(f) / SR
    return np.sin(ph)

# ---------------------------------------------------------------- sound effects
def fx_blip(f=430, amp=.3):
    d = .075
    t = t_(d)
    s = np.sign(np.sin(2 * np.pi * f * t)) * .35 + np.sin(2 * np.pi * f * t) * .65
    s += .3 * np.sin(2 * np.pi * f * 2 * t)
    return s * env_ad(len(t), .004, d, 4.5) * amp

def fx_boing(amp=.5, up=1):
    d = .32
    s = sweep(210, 640, d, .6) if up else sweep(640, 200, d)
    t = t_(d)
    s = s * (1 + .25 * np.sin(2 * np.pi * 26 * t))
    return s * env_ad(len(t), .006, d, 4.0) * amp

def fx_thud(f=140, amp=.5):
    d = .28
    s = sweep(f, f * .45, d, .5) * env_ad(int(d * SR), .002, d, 7)
    n = bandpass_noise(d, 80, 900) * env_ad(int(d * SR), .001, .08, 6) * .5
    return (s + n) * amp

def fx_chime(amp=.35):
    d = 1.1
    t = t_(d)
    s = np.sin(2 * np.pi * 880 * t) + .6 * np.sin(2 * np.pi * 1320 * t) + .25 * np.sin(2 * np.pi * 1760 * t)
    return s * env_ad(len(t), .004, d, 5) * amp * .5

def fx_yawn(amp=.3):
    d = 1.0
    t = t_(d)
    s = sweep(330, 190, d) * (1 + .2 * np.sin(2 * np.pi * 5 * t))
    e = np.sin(np.pi * t / d) ** 1.5
    return s * e * amp

def fx_hum(vol=.5, dur=4.0):
    mel = [523.25, 587.33, 659.25, 523.25, 659.25, 698.46, 783.99, 783.99, 880, 783.99, 659.25, 587.33, 523.25]
    dura = [.5, .5, .5, .5, .5, .5, 1.0, .5, .5, .5, .5, .5, 1.0]
    out = np.zeros(int(dur * SR) + SR)
    tt = 0.0
    i = 0
    while tt < dur:
        f = mel[i % len(mel)]
        d = dura[i % len(mel)] * .9
        t = t_(d)
        vib = 1 + .006 * np.sin(2 * np.pi * 5.5 * t)
        ph = 2 * np.pi * np.cumsum(f * vib) / SR
        s = np.sin(ph) + .35 * np.sin(2 * ph) + .12 * np.sin(3 * ph)
        e = np.minimum(1, t / .05) * np.minimum(1, (d - t) / .12)
        j = int(tt * SR)
        out[j:j + len(s)] += s * e * .22
        tt += dura[i % len(mel)]
        i += 1
    return out[:int(dur * SR)] * vol

def fx_wind(dur=4.0, amp=.4):
    n = bandpass_noise(dur, 200, 1400)
    t = t_(dur)
    e = np.sin(np.pi * t / dur) ** 1.2
    return n[:len(t)] * e * amp * .6

def fx_thunder(amp=.9):
    d = 3.2
    n = bandpass_noise(d, 30, 380)
    t = t_(d)
    crack = bandpass_noise(.25, 1500, 7000) * env_ad(int(.25 * SR), .001, .12, 5) * .9
    s = n * env_ad(len(t), .02, d, 5.5) * 1.2
    s[:len(crack)] += crack
    return s * amp * .8

def fx_whoosh(dur=1.5, amp=.6, rise=0):
    n = bandpass_noise(dur, 300, 3500)
    t = t_(dur)
    e = np.sin(np.pi * (t / dur) ** (.7 if rise else 1.0)) ** 1.6
    return n[:len(t)] * e * amp * .8

def fx_splash(amp=1.0):
    d = .65
    n = bandpass_noise(d, 700, 6500)
    t = t_(d)
    s = n * env_ad(len(t), .004, d, 4.5)
    s += .3 * bandpass_noise(d, 120, 500) * env_ad(len(t), .004, .3, 6)
    return s * amp * .7

def fx_squish(amp=.4):
    d = .22
    s = sweep(330, 110, d)
    return s * env_ad(int(d * SR), .004, d, 5) * amp

def fx_honk(amp=.7):
    d = .26
    t = t_(d)
    s = np.sign(np.sin(2 * np.pi * 349 * t)) + np.sign(np.sin(2 * np.pi * 440 * t))
    s = s * .25
    e = np.minimum(1, t / .01) * np.minimum(1, (d - t) / .03)
    return s * e * amp * .45

FX = dict(blip=lambda **k: fx_blip(k.get('f', 430), k.get('amp', .3)),
          boing=lambda **k: fx_boing(k.get('amp', .5), k.get('up', 1)),
          thud=lambda **k: fx_thud(k.get('f', 140), k.get('amp', .5)),
          chime=lambda **k: fx_chime(k.get('amp', .35)),
          yawn=lambda **k: fx_yawn(k.get('amp', .3)),
          hum=lambda **k: fx_hum(k.get('vol', .5), k.get('dur', 4)),
          wind=lambda **k: fx_wind(k.get('dur', 4), k.get('amp', .4)),
          thunder=lambda **k: fx_thunder(k.get('amp', .9)),
          whoosh=lambda **k: fx_whoosh(k.get('dur', 1.5), k.get('amp', .6), k.get('rise', 0)),
          splash=lambda **k: fx_splash(k.get('amp', 1.0)),
          squish=lambda **k: fx_squish(k.get('amp', .4)),
          honk=lambda **k: fx_honk(k.get('amp', .7)))

# ---------------------------------------------------------------- music
NOTE = {'C': 0, 'D': 2, 'E': 4, 'F': 5, 'G': 7, 'A': 9, 'B': 11}
def hz(name, octv):
    return 440.0 * 2 ** ((NOTE[name] - 9 + 12 * (octv - 4)) / 12.0)

CH = {'C': ('C', 'E', 'G'), 'G': ('G', 'B', 'D'), 'Am': ('A', 'C', 'E'), 'F': ('F', 'A', 'C'),
      'Dm': ('D', 'F', 'A'), 'Em': ('E', 'G', 'B')}

def pluck(f, d=.9, amp=.2, bright=1.0):
    t = t_(d)
    s = np.sin(2 * np.pi * f * t) + .45 * bright * np.sin(2 * np.pi * 2 * f * t) * np.exp(-t * 6) + .2 * np.sin(2 * np.pi * 3 * f * t) * np.exp(-t * 9)
    return s * env_ad(len(t), .003, d, 5.0) * amp

def pad(f, d, amp=.08):
    t = t_(d)
    s = np.sin(2 * np.pi * f * t) + .5 * np.sin(2 * np.pi * f * 1.005 * t) + .3 * np.sin(2 * np.pi * f * 2 * t)
    e = np.minimum(1, t / .6) * np.minimum(1, (d - t) / .8)
    return s * e * amp

def arp_section(t0, t1, chords, bpm, vol, octv=4, pattern=(0, 1, 2, 1), bar_beats=4, bright=1.0, melody=None, bass=True, step=.5):
    beat = 60.0 / bpm
    t = t0
    bar = 0
    while t < t1 - 1e-6:
        ch = CH[chords[bar % len(chords)]]
        n = int(bar_beats / step)
        for k in range(n):
            tt = t + k * step * beat
            if tt >= t1:
                break
            nm = ch[pattern[k % len(pattern)] % 3]
            o = octv + (1 if pattern[k % len(pattern)] >= 3 else 0)
            fade = min(1, (t1 - tt) / .8) * min(1, (tt - t0) / .4 + .0)
            add(tt, pluck(hz(nm, o), .9, .17 * vol * fade, bright), 1)
        if bass:
            add(t, pluck(hz(ch[0], octv - 2), 1.6, .26 * vol * min(1, (t1 - t) / .8)), 1)
            add(t + 2 * beat, pluck(hz(ch[2], octv - 2), 1.2, .18 * vol * min(1, (t1 - t) / .8)), 1)
        t += bar_beats * beat
        bar += 1

def rain_bed(t0, t1, amp0, amp1):
    d = t1 - t0
    n = bandpass_noise(d, 1200, 9000)
    t = t_(d)
    a = amp0 + (amp1 - amp0) * (t / d)
    add(t0, n[:len(t)] * a, 1)

S = story.START
T0 = lambda sc, t: S[sc] + t

def build_music():
    # S0 title: bright
    arp_section(0, 8, ['C', 'G', 'Am', 'F'], 112, .9, 4, (0, 1, 2, 1, 3, 2, 1, 2))
    # S1 doorstep (calm then uneasy)
    arp_section(8, 28, ['C', 'G', 'Am', 'F'], 96, .55, 4, (0, 1, 2, 1))
    add(T0('S1', 13.9), pad(hz('A', 2), 7.5, .18), 1)
    # S2 danger: drums + dark pad
    for k in range(int(22 / .5)):
        tt = S['S2'] + k * .5
        add(tt, fx_thud(70 + 10 * (k % 2), .32 + .002 * k), 1)
        if k % 4 == 2:
            add(tt, fx_thud(55, .3), 1)
    add(S['S2'], pad(hz('A', 2), 22, .22), 1)
    add(S['S2'], pad(hz('E', 3), 22, .12), 1)
    # S3 lost: sparse sad arps
    arp_section(S['S3'] + 1.5, S['S3'] + 19, ['Am', 'Dm', 'Em', 'Am'], 58, .55, 4, (0, 2, 1, 2), bright=.6, step=1.0)
    add(S['S3'], pad(hz('A', 2), 20, .12), 1)
    # S4 hopeful build
    arp_section(S['S4'], S['S4'] + 12, ['Am', 'F', 'C', 'G'], 80, .45, 4, (0, 1, 2, 1), bright=.7)
    arp_section(S['S4'] + 12, S['S4'] + 30, ['C', 'G', 'Am', 'F'], 104, .75, 4, (0, 1, 2, 1, 3, 2, 1, 2), bright=1.0)
    for k in range(6):
        add(S['S4'] + 13.2 + k * .05, fx_boing(.0001, 1), 1)
    # S4 victory sparkle on landing
    for i, f in enumerate((784, 988, 1175, 1568)):
        add(S['S4'] + 15.5 + i * .08, pluck(f, .9, .22), 1)
    # S5 comic walking bass, then sad, then hopeful rise
    t = S['S5'] + 0.0
    k = 0
    while t < S['S5'] + 4.4:
        add(t, pluck(hz(['C', 'E', 'G', 'E'][k % 4], 3), .25, .22, .5), 1)
        t += .375; k += 1
    add(S['S5'] + 5.3, fx_thud(80, .5), 1)
    arp_section(S['S5'] + 8.0, S['S5'] + 14.2, ['Am', 'Dm'], 54, .45, 4, (0, 2, 1, 2), bright=.5, step=1.0)
    for i, (n, o) in enumerate((('C', 5), ('E', 5), ('G', 5), ('C', 6))):
        add(S['S5'] + 14.4 + i * .28, pluck(hz(n, o), .9, .22), 1)
    arp_section(S['S5'] + 15.6, S['S5'] + 20, ['F', 'G', 'C', 'G'], 100, .7, 4, (0, 1, 2, 1, 3, 2, 1, 2))
    # S6 warm reunion
    arp_section(S['S6'], S['S6'] + 7, ['Am', 'F'], 60, .4, 4, (0, 2, 1, 2), bright=.5)
    arp_section(S['S6'] + 7, S['S6'] + 22, ['C', 'G', 'Am', 'F'], 84, .75, 4, (0, 1, 2, 1, 3, 2, 1, 2))
    add(S['S6'] + 7.0, pluck(hz('C', 6), 1.0, .2), 1)
    # S7 reprise and end
    arp_section(S['S7'], S['S7'] + 14, ['C', 'G', 'Am', 'F'], 112, .85, 4, (0, 1, 2, 1, 3, 2, 1, 2))
    add(S['S7'] + 13.0 - 0.1, pad(hz('C', 3), 1.2, .08), 1)

def build_ambience():
    # rain follows the visuals
    rain_bed(T0('S1', 14.2), S['S1'] + 24, .0, .055)
    rain_bed(S['S2'], S['S2'] + 22, .06, .075)
    rain_bed(S['S3'], S['S3'] + 20, .07, .065)
    rain_bed(S['S4'], S['S4'] + 30, .06, .028)
    rain_bed(S['S5'], S['S5'] + 14, .028, .0)

def build_sfx():
    for (T, kind, kw) in story.SFX:
        if kind not in FX:
            continue
        if kind == 'hum' and kw.get('vol', 1) <= 0.01:
            continue
        sig = FX[kind](**kw)
        add(T, sig, 1.0)

def main(path):
    build_music()
    build_ambience()
    build_sfx()
    y = mix.copy()
    # gentle limiter + normalise
    y = np.tanh(y * 1.1)
    peak = np.max(np.abs(y))
    y = y / peak * .89
    # master fade in/out
    n = len(y)
    fi = int(.15 * SR); fo = int(1.2 * SR)
    y[:fi] *= np.linspace(0, 1, fi)
    end = int(TOTAL * SR)
    y[end - fo:end] *= np.linspace(1, 0, fo)
    y[end:] = 0
    y = y[:end]
    pcm = (y * 32767).astype('<i2')
    with wave.open(path, 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes(pcm.tobytes())
    print('audio written', path, len(pcm) / SR, 's', 'peak', peak)

if __name__ == '__main__':
    import sys
    main(sys.argv[1])
