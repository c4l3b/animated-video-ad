"""Assemble a rough cut from a cut list, to preview pacing and music against the picture.

    python3 roughcut.py cuts.json out.mp4 [--music bed.wav] [--music-db -8] [--vo vo.wav]

cuts.json is a list of segments in order, matching the script's cut table:
    [{"clip": "clips/01-hook-anim.mp4", "in": 0.0, "out": 3.0, "speed": 1.0}, ...]
A clip used twice (two ranges) is just two entries. Prints each cut's start time in the result,
so the cut table's "Time" column can be checked against the music's bar lines. Not for publishing:
the person's editor (Camtasia, Premiere, CapCut...) does the real cut and the voice-over.
"""
import argparse
import json
import subprocess
from pathlib import Path

ap = argparse.ArgumentParser()
ap.add_argument('cuts')
ap.add_argument('out')
ap.add_argument('--music')
ap.add_argument('--music-db', type=float, help='music level after normalising it to -16 LUFS; default -8 dB alone, -16 dB under --vo')
ap.add_argument('--music-at', type=float, default=0.0, help='shift the music: +s starts it later (silence first), -s skips its first s seconds; use it to land the beat entry on a cut')
ap.add_argument('--vo', help='voice-over track already placed on the cut timeline (place_vo.py)')
a = ap.parse_args()

cuts = json.loads(Path(a.cuts).read_text())
root = Path(a.cuts).parent
first = Path(cuts[0]['clip']) if Path(cuts[0]['clip']).is_absolute() else root / cuts[0]['clip']
# Output takes the first clip's size, so vertical and square cuts work too.
W, H = subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=width,height',
                       '-of', 'csv=p=0', str(first)], capture_output=True, text=True, check=True).stdout.strip().split(',')[:2]
args, fc, t = [], '', 0.0
for i, c in enumerate(cuts):
    clip = Path(c['clip']) if Path(c['clip']).is_absolute() else root / c['clip']
    args += ['-i', str(clip)]
    speed = c.get('speed', 1.0)
    fc += f"[{i}:v]trim={c['in']}:{c['out']},setpts=(PTS-STARTPTS)/{speed},fps=30,scale={W}:{H},setsar=1[v{i}];"
    print(f"{t:6.2f}s  {clip.name}  {c['in']}-{c['out']} @ {speed}x")
    t += (c['out'] - c['in']) / speed
fc += ''.join(f'[v{i}]' for i in range(len(cuts))) + f'concat=n={len(cuts)}:v=1:a=0[v]'
maps = ['-map', '[v]']
audio, k = [], len(cuts)
if a.music:
    db = a.music_db if a.music_db is not None else (-16 if a.vo else -8)
    args += ['-i', a.music]
    shift = f'adelay={int(a.music_at * 1000)}:all=1,' if a.music_at > 0 else (f'atrim=start={-a.music_at},asetpts=PTS-STARTPTS,' if a.music_at < 0 else '')
    fc += f';[{k}:a]{shift}loudnorm=I=-16:TP=-1.5,volume={db}dB,afade=t=out:st={max(0, t - 0.5)}:d=0.5[m]'
    audio.append('[m]'); k += 1
if a.vo:
    args += ['-i', a.vo]
    fc += f';[{k}:a]anull[vo]'
    audio.append('[vo]')
if audio:
    fc += f";{''.join(audio)}amix=inputs={len(audio)}:normalize=0[a]" if len(audio) > 1 else f';{audio[0]}anull[a]'
    maps += ['-map', '[a]', '-c:a', 'aac', '-b:a', '192k']
subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', *args, '-filter_complex', fc, *maps,
                '-t', f'{t:.3f}', '-c:v', 'libx264', '-crf', '20', '-pix_fmt', 'yuv420p', a.out], check=True)
print(f'{t:6.2f}s  end -> {a.out}')
