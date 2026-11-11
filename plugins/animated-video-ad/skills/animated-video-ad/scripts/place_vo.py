"""Cut one voice-over take into its lines and place each line at its cue in the cut.

    python3 place_vo.py take.mp3 --script vo-lines.txt --starts 0.3,3.2,7.2,11.2,16.2,21.2,27.2 --total 30 --out vo-30s.wav

The take is one recording of all lines in order. vo-lines.txt has the same lines, one per line of
the file. A voice pauses inside lines too ("Draw the line. Done."), so pauses alone can't find the
line breaks: the script estimates where each break should fall from the word counts and splits at
the pause nearest each estimate. Then it trims each line's silence and puts line i at starts[i].
Check the printed lengths against the script: a line that looks far too short or long means a
wrong split (then generate one take per line and pass them in order instead of one take). A line that would
run into the next cue is reported so you can tighten the script or move the cue; nothing is
sped up or cut off unless you pass --tempo (pitch-preserving, keep it at or under ~1.1).
Needs ffmpeg.

Prints each line's start, length and end, and the gap to the next cue.
"""
import argparse
import re
import subprocess
import sys

ap = argparse.ArgumentParser()
ap.add_argument('take', nargs='+', help='one take of all lines, or one file per line in order')
ap.add_argument('--script', help='text file, one voice-over line per line (needed for a single take)')
ap.add_argument('--starts', required=True, help='comma-separated cue times in seconds, one per line')
ap.add_argument('--total', type=float, required=True, help='length of the cut in seconds')
ap.add_argument('--out', required=True)
ap.add_argument('--min-pause', type=float, default=0.25, help='shortest silence that can separate lines')
ap.add_argument('--noise', default='-38dB', help='silence threshold for ffmpeg silencedetect')
ap.add_argument('--tempo', type=float, default=1.0, help='speed every line up (pitch kept), e.g. 1.06; above ~1.1 sounds rushed')
a = ap.parse_args()
starts = [float(s) for s in a.starts.split(',')]
n = len(starts)

def probe(f):
    return float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', f],
                                capture_output=True, text=True, check=True).stdout)

def silences(f):
    log = subprocess.run(['ffmpeg', '-hide_banner', '-i', f, '-af', f'silencedetect=n={a.noise}:d={a.min_pause}', '-f', 'null', '-'],
                         capture_output=True, text=True).stderr
    return [(float(m.group(1)), float(m.group(2))) for m in re.finditer(r'silence_start: ([\d.]+)[\s\S]*?silence_end: ([\d.]+)', log)]

def speech_bounds(f):
    d, sil = probe(f), silences(f)
    s0 = sil[0][1] if sil and sil[0][0] < 0.05 else 0.0
    s1 = sil[-1][0] if sil and sil[-1][1] >= d - 0.05 else d
    return d, s0, s1, [x for x in sil if x[0] > s0 + 0.05 and x[1] < s1 - 0.05]

if len(a.take) > 1:  # one file per line
    if len(a.take) != n: sys.exit(f'{len(a.take)} files but {n} starts')
    segs = []
    for f in a.take:
        d, s0, s1, _ = speech_bounds(f); segs.append((f, s0, s1, d))
else:
    if not a.script: sys.exit('a single take needs --script with the lines, one per line')
    lines = [l.strip() for l in open(a.script) if l.strip()]
    if len(lines) != n: sys.exit(f'{len(lines)} script lines but {n} starts')
    f = a.take[0]
    d, s0, s1, inner = speech_bounds(f)
    words = [len(l.split()) for l in lines]
    cuts, used = [], set()
    for i in range(1, n):  # expected break after line i, by word share of the speech time
        target = s0 + (s1 - s0) * sum(words[:i]) / sum(words)
        prev = cuts[-1][1] if cuts else s0
        cands = [x for x in inner if x[0] > prev and x not in used]
        if not cands: sys.exit(f'no pause left for the break after line {i}: generate one take per line instead')
        best = min(cands, key=lambda x: abs((x[0] + x[1]) / 2 - target) - 0.5 * (x[1] - x[0]))
        cuts.append(best); used.add(best)
    segs, t = [], s0
    for c0, c1 in cuts:
        segs.append((f, t, c0, d)); t = c1
    segs.append((f, t, s1, d))

pad = 0.04  # keep breaths/consonant tails
inputs, fc, mix = [], '', ''
for i, ((f, s0, s1, d), at) in enumerate(zip(segs, starts)):
    s0, s1 = max(0, s0 - pad), min(d, s1 + pad)
    length = (s1 - s0) / a.tempo
    nxt = starts[i + 1] if i + 1 < n else a.total
    gap = nxt - (at + length)
    flag = '' if gap >= 0.1 else '   <-- runs into the next cue: shorten the line or move the cue'
    print(f'line {i + 1}: {at:6.2f}s  {length:5.2f}s long  ends {at + length:6.2f}s  gap {gap:+.2f}s{flag}')
    inputs += ['-i', f]
    fc += f'[{i}:a]atrim={s0:.3f}:{s1:.3f},asetpts=PTS-STARTPTS,atempo={a.tempo},adelay={int(at * 1000)}:all=1[l{i}];'
    mix += f'[l{i}]'
fc += f'{mix}amix=inputs={n}:normalize=0,loudnorm=I=-16:TP=-1.5:LRA=11,apad,atrim=0:{a.total}[out]'  # voice at -16 LUFS, a normal level for social video
subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', *inputs, '-filter_complex', fc,
                '-map', '[out]', '-ar', '48000', '-ac', '2', a.out], check=True)
print(f'wrote {a.out} ({a.total:g} s)')
