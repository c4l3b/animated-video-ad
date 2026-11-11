# Music

Three ways to get the music. Ask the person which (SKILL.md step 1); lead with ElevenLabs when its
MCP is connected. Whichever it is, the music
should sit under a voice-over without fighting it: quiet, steady, no vocals, no big drops.

Cuts feel locked to music when they land on its beats. At 120 bpm a beat is 0.5 s and a 4-beat
bar is 2 s, so a cut table in whole and half seconds already sits on the beat.

## 1. Generate it here (`scripts/make_bed.py`)

```bash
python3 <skill>/scripts/make_bed.py --total 30 --groove-at 3 --end-hold 3 --out <music>/bed-30s.wav
```

- `--total`: cut length in seconds. `--groove-at`: when the beat starts (the end of the hook).
  `--end-hold`: seconds of ring-out over the end card. `--bpm`: default 120.
- Shape: suspended pad under the hook, soft beat (kick, shaker, plucked arpeggio, bass, pad;
  Am F C G, a chord per bar), a small riser, a resolving C chord over the end card.
- Peaks at -3 dBFS (about -15 LUFS).
- Licence-free: it's synthesised on the spot, no samples.
- You can't listen to it. Check it as a picture and say you did only that:
  ```bash
  ffmpeg -i bed.wav -filter_complex "[0]asplit[a][b];[a]showwavespic=s=1600x240[w];[b]showspectrumpic=s=1600x400:legend=0[s];[w][s]vstack" -frames:v 1 bed.png
  ```
  Look for: quiet start, steady body from `--groove-at`, a lift before the end card, ring-out.

## 2. The person's own track

Ask for the file and, if they know it, its tempo (bpm). Then:
1. Pick the start point in the track: a section that is steady and has no vocals. If the track has a
   clear ending, line that ending up with the end card instead.
2. Trim it to the cut length and fade the last 0.5–1 s (the rough-cut script fades the last 0.5 s).
   `ffmpeg -ss START -t LENGTH -i track.mp3 -af "afade=t=out:st=LENGTH-1:d=1" <music>/track-cut.wav`
3. If the bpm is known, nudge cut times in the table onto beats (multiples of 60/bpm from the
   track's start point). Don't stretch shots more than ~0.2 s to do it.
4. Remind them the licence must cover ads (stock "standard" licences sometimes exclude paid ads;
   editor libraries us## 3. ElevenLabs Music

### With the ElevenLabs MCP connected

1. `creative_create_flow` once for the ad (reuse its `flow_id` for the voice-over too).
2. `creative_add_flow_node`: `node_type: "music"`, `model_id: "eleven_music_v2_5"`,
   `model_parameters: {"duration_seconds": <cut length + 5>, "instrumental": true, "lyrics_type": "instrumental"}`
   and the prompt (below). Check `creative_get_model_schema` if a parameter is refused; names
   change between model versions.
3. `creative_run_flow_nodes` with `estimate_only: true`, tell the person the cost (a 30 s bed was
   450 credits, about $0.09–0.15), then run it with `generations_count: 1` (2 if they want a
   choice). Never call run again to "retry"; each call is charged.
4. Poll `creative_get_flow_run_status` every ~20 s until `all_completed`; download each
   `media[].url` (signed, expires in about two hours) with `curl -o <music>/music-take1.mp3`.
5. Check it as a picture (command in section 1) and find where the beat comes in and where the
   ending starts. **The model treats timings in the prompt as loose hints:** in testing, "groove
   from 3 s" came in at ~10 s and the "end chord at 27 s" became a fade. Don't regenerate for
   that; shift it: `roughcut.py --music-at S` with S = (cut time you want the beat on) − (beat
   entry in the file). Positive starts it later; negative skips its intro. A beat entry on any cut
   reads as intentional.
6. Give the person the flow link from the result so they can make more takes themselves.

### Without the MCP

Write the prompt and settings for them to use at elevenlabs.io/music (instrumental, duration
cut + 5 s); when the file comes back, fit it like their own track (section 2) and with
`--music-at`.

### The prompt

Describe the sound, not the picture, in 2–4 sentences (ElevenLabs' own guidance): genre, mood
and energy, key instruments, tempo, production style, and how the energy moves. Example that
worked:

```
Light, optimistic electronic background bed for a product ad, 120 BPM, steady and understated.
Opens with a soft sustained synth pad, then a gentle kick, light shaker and plucked arpeggio come
in and hold a calm, even groove with no big drops. A small lift near the end resolves into a warm
major chord that rings out. Clean modern production, sits quietly under a voice-over.
```

Match the brand's mood words (warm acoustic for a consumer app, clean electronic for dev tools).
Say "no vocals" or set instrumental; say "no big drops" or it will build like a song.

### Rights

It's the person's ElevenLabs account and plan. ElevenLabs ties commercial use of generated music
to its paid plans; tell them to check their plan covers an ad, and that the terms can change.

s tie that to paid plans, and they can change.

## Levels (put these in the script doc)

| Editor | Under a voice-over | Music alone |
|---|---|---|
| Premiere, Resolve, Camtasia, Final Cut (dB) | about -20 dB | about -8 dB |
| CapCut, iMovie (percent slider) | about 10–15% | about 35–45% |

make_bed.py output peaks at -3 dBFS; ElevenLabs music came out near -17 LUFS. `roughcut.py`
normalises music to -16 LUFS before setting its level, so previews match whatever the source.
In the editor, the person adjusts by ear.

## Rough-cut preview

```bash
python3 <skill>/scripts/roughcut.py <music>/cuts.json <music>/roughcut-preview.mp4 --music <music>/<track> [--music-at S] [--vo <music>/vo.wav]
```
Omit `--music` for a silent preview. It prints each cut's start time: compare with the cut table.
