#!/usr/bin/env bash
# Contact sheet of a clip, to check a recording without watching it.
#   sheet.sh clip.mp4 out.jpg [fps=2] [cols=6]
# Tiles one frame every 1/fps seconds, each stamped with its time. Also look at the last frame:
#   ffmpeg -sseof -0.1 -i clip.mp4 -frames:v 1 last.jpg
set -euo pipefail
in=$1; out=$2; fps=${3:-2}; cols=${4:-6}
dur=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$in")
n=$(python3 -c "import math;print(max(1,math.ceil($dur*$fps)))")
rows=$(( (n + cols - 1) / cols ))
# Time stamps need ffmpeg's drawtext (not in every build); without it, tiles read left to right,
# one every 1/fps seconds.
stamp=""; ffmpeg -hide_banner -filters 2>/dev/null | grep -q ' drawtext ' && stamp=",drawtext=text='%{pts\:hms}':x=8:y=8:fontsize=22:fontcolor=white:box=1:boxcolor=black@0.6"
ffmpeg -hide_banner -loglevel error -y -i "$in" -vf "fps=$fps,scale=480:-2${stamp},tile=${cols}x${rows}" -frames:v 1 -update 1 "$out"
echo "$out  ($dur s, $n frames)"
