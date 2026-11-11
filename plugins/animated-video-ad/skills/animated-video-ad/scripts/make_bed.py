"""Subtle, licence-free music bed for a short ad, timed to its cuts. Needs only numpy.

Shape: a quiet suspended pad under the hook (0 to --groove-at), then a soft groove (kick, shaker,
plucked arpeggio, bass, pad; Am F C G, one chord per 4-beat bar), a small riser, and a resolving
C chord that rings out over the last --end-hold seconds (the end card).

At 120 bpm a bar is 2 s, so with --groove-at 3 chord changes land at 3, 5, 7, 9 ... s. Put cuts
on those times (or on any beat, every 0.5 s) and the picture feels locked to the music.

    python3 make_bed.py --total 30 --out bed-30s.wav
    python3 make_bed.py --total 59 --groove-at 3 --end-hold 3 --bpm 120 --out bed-60s.wav

Output peaks at -3 dBFS (about -15 LUFS). Under a voice-over set it about -20 dB in the editor.
"""
import wave
from pathlib import Path

import numpy as np

SR = 48000
BEAT = 0.5          # set from --bpm
GROOVE_AT = 3.0     # set from --groove-at
END_HOLD = 3.0      # set from --end-hold
rng = np.random.default_rng(7)

NOTE = {'C': 0, 'D': 2, 'E': 4, 'F': 5, 'G': 7, 'A': 9, 'B': 11}
def hz(name, octave):
    return 440 * 2 ** ((NOTE[name] + 12 * (octave + 1) - 69) / 12)

CHORDS = {  # pad voicing, arp notes, bass root
    'Am': ([('A', 3), ('C', 4), ('E', 4)], [('A', 4), ('C', 5), ('E', 5), ('C', 5)], ('A', 2)),
    'F':  ([('F', 3), ('A', 3), ('C', 4)], [('F', 4), ('A', 4), ('C', 5), ('A', 4)], ('F', 2)),
    'C':  ([('G', 3), ('C', 4), ('E', 4)], [('C', 5), ('E', 5), ('G', 5), ('E', 5)], ('C', 3)),
    'G':  ([('G', 3), ('B', 3), ('D', 4)], [('G', 4), ('B', 4), ('D', 5), ('B', 4)], ('G', 2)),
    'Esus': ([('E', 3), ('A', 3), ('B', 3)], [], ('E', 2)),
}
PROG = ['Am', 'F', 'C', 'G']


def t_axis(dur):
    return np.arange(int(dur * SR)) / SR


def place(buf, sig, at):
    i = int(at * SR)
    n = min(len(sig), len(buf) - i)
    if n > 0:
        buf[i:i + n] += sig[:n]


def soft_saw(f, dur, harmonics=7):
    t = t_axis(dur)
    return sum(np.sin(2 * np.pi * f * k * t + rng.uniform(0, 6.28)) / k ** 1.4 for k in range(1, harmonics + 1))


def pad(chord, dur, attack=0.6, release=0.8):
    t = t_axis(dur + release)
    sig = sum(soft_saw(hz(*n) * d, dur + release) for n in CHORDS[chord][0] for d in (0.997, 1.003))
    env = np.minimum(1, t / attack) * np.clip((dur + release - t) / release, 0, 1)
    return sig * env


def pluck(f, dur=0.45):
    t = t_axis(dur)
    return (np.sin(2 * np.pi * f * t) + 0.3 * np.sin(4 * np.pi * f * t)) * np.exp(-t * 9) * np.minimum(1, t / 0.004)


def kick():
    t = t_axis(0.35)
    f = 45 + 75 * np.exp(-t * 30)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 11)


def shaker():
    t = t_axis(0.06)
    n = rng.standard_normal(len(t))
    n = np.diff(n, prepend=0)          # crude high-pass
    return n * np.exp(-t * 70)


def bass(f, dur):
    t = t_axis(dur)
    return np.sin(2 * np.pi * f * t) * np.minimum(1, t / 0.02) * np.exp(-t * 1.2)


def lowpass(x, cutoff):
    spec = np.fft.rfft(x)
    fr = np.fft.rfftfreq(len(x), 1 / SR)
    return np.fft.irfft(spec / np.sqrt(1 + (fr / cutoff) ** 4), len(x))


def reverb(x, secs=2.2, wet=0.25):
    t = t_axis(secs)
    ir = rng.standard_normal(len(t)) * np.exp(-t * 3.2)
    ir = lowpass(ir, 5000)
    n = len(x) + len(ir)
    y = np.fft.irfft(np.fft.rfft(x, n) * np.fft.rfft(ir, n), n)[:len(x)]
    return x + wet * y / np.max(np.abs(y)) * np.max(np.abs(x))


def build(total):
    end_at = total - END_HOLD                       # groove stops, end chord rings
    pads, arps, drums, low = (np.zeros(int((total + 1) * SR)) for _ in range(4))

    # Hook: quiet suspended pad that swells into the downbeat at 3 s.
    p = pad('Esus', GROOVE_AT, attack=2.5, release=0.4)
    place(pads, p * 0.6, 0)

    t, bar = GROOVE_AT, 0
    while t < end_at - 1e-6:
        chord = PROG[bar % 4]
        bar_len = min(4 * BEAT, end_at - t)
        place(pads, pad(chord, bar_len, attack=0.25, release=0.5), t)
        place(low, bass(hz(*CHORDS[chord][2]), bar_len), t)
        for i in range(int(round(bar_len / (BEAT / 2)))):
            at = t + i * BEAT / 2
            place(arps, pluck(hz(*CHORDS[chord][1][i % 4])) * (0.9 if i % 2 == 0 else 0.6), at)
            if i % 2 == 0:
                place(drums, kick() * 0.9, at)
            else:
                place(drums, shaker() * 0.25, at)
        t += bar_len
        bar += 1

    # Small noise riser into the end card.
    r = t_axis(1.0)
    place(drums, lowpass(rng.standard_normal(len(r)), 3000) * (r / 1.0) ** 3 * 0.12, end_at - 1.0)

    # End card: C chord, one shimmer arp, long ring-out.
    place(pads, pad('C', END_HOLD * 0.6, attack=0.05, release=END_HOLD * 0.4) * 1.1, end_at)
    place(low, bass(hz('C', 3), END_HOLD), end_at)
    place(drums, kick(), end_at)
    for i, n in enumerate([('C', 5), ('E', 5), ('G', 5), ('C', 6)]):
        place(arps, pluck(hz(*n), 1.5) * 0.7, end_at + i * 0.12)

    mix = lowpass(pads, 1800) * 0.10 + reverb(arps, wet=0.35) * 0.16 + drums * 0.35 + lowpass(low, 400) * 0.30
    mix = mix[:int(total * SR)]
    fade = int(0.6 * SR)
    mix[-fade:] *= np.linspace(1, 0, fade)
    mix *= 10 ** (-3 / 20) / np.max(np.abs(mix))   # peak -3 dBFS; turn it down in Camtasia
    # Light stereo: delay the right channel 9 ms on the pad/arp-heavy mix.
    d = int(0.009 * SR)
    right = np.concatenate([mix[:d], mix[:-d]]) * 0.9 + mix * 0.1
    return np.stack([mix, right], axis=1)


def write(path, stereo):
    pcm = (np.clip(stereo, -1, 1) * 32767).astype('<i2')
    with wave.open(str(path), 'wb') as w:
        w.setnchannels(2), w.setsampwidth(2), w.setframerate(SR)
        w.writeframes(pcm.tobytes())


if __name__ == '__main__':
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument('--total', type=float, required=True, help='length in seconds')
    ap.add_argument('--out', required=True)
    ap.add_argument('--bpm', type=float, default=120)
    ap.add_argument('--groove-at', type=float, default=3.0, help='when the beat starts (end of the hook)')
    ap.add_argument('--end-hold', type=float, default=3.0, help='seconds of ring-out for the end card')
    a = ap.parse_args()
    BEAT, GROOVE_AT, END_HOLD = 60 / a.bpm, a.groove_at, a.end_hold
    out = build(a.total)
    assert out.shape[0] == int(a.total * SR) and np.max(np.abs(out)) <= 1.0
    write(Path(a.out), out)
    print(a.out, f'{a.total:g} s, groove at {GROOVE_AT:g} s, end chord at {a.total - END_HOLD:g} s')
