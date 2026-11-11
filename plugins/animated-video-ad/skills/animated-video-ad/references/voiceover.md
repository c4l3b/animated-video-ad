# Voice-over with ElevenLabs

Use this when the ElevenLabs MCP is connected (tools such as `creative_generate_speech` and
`creative_list_voices`) and the person chose an ElevenLabs voice. Otherwise the script doc's clean
read is for them to record themselves.

## 1. Write the read for the clock

The cut table's "Say" lines are the script. Before generating, check each line fits its window
(next cue − this cue − ~0.2 s). ElevenLabs voices read at about 2.6–2.8 words per second with
natural pauses, so a 30 s ad holds about 70 words and leaves little air. Cut words first; spoken
numbers and URLs run long ("yourproduct dot com" is four beats).

Write URLs the way they should be said ("example dot com") and numbers in words where the
pronunciation matters ("thirty-eight seconds").

## 2. Pick a voice

`creative_list_voices` with `use_cases: ["advertisement"]`, `languages: ["en"]` (or theirs) and a
descriptive that fits the brand (`confident`, `calm`, `upbeat`). Prefer a voice whose description
mentions product explainers or app demos for software; avoid "salesman" or "dramatic" voices for
anything that should sound trustworthy. Pick one yourself and say which; the person can switch
voices in the ElevenLabs view. A voice_id only ever comes from that list or the person.

## 3. Generate one take

`creative_generate_speech` on the same flow as the music:
- `model_id: "eleven_v4"` (supports direction tags such as `[warmly]` if needed)
- `prompt`: every line in order, a blank line between lines
- `generations_count: 1` (2 if they want to compare)
- call it first with `estimate_only: true` and tell the person the cost (a 30 s read was 441
  credits, about $0.09); it's charged per character, so per-line generations cost about the same

Never call it again to retry; each call is charged. Poll `creative_get_flow_run_status` until
`all_completed`, then download `media[].url` (expires in about two hours):
`curl -sfL -o <music>/vo-take1.mp3 '<url>'`.

## 4. Place each line on its cue

Save the lines to `vo-lines.txt` (one per line, the same text), then:

```bash
python3 <skill>/scripts/place_vo.py <music>/vo-take1.mp3 --script <music>/vo-lines.txt \
  --starts 0.3,3.2,7.2,11.2,16.2,21.2,27.2 --total 30 --out <music>/vo-30s.wav
```

`--starts` are the cut table's "VO starts" times. The voice pauses inside lines too, so the script
splits at the pause nearest where each line should end by word count. Read its output:
- **Line lengths look wrong** (a 10-word line at 0.8 s): a bad split. Generate one take per line
  and pass the files in order instead of one take (no `--script` needed).
- **"runs into the next cue"**: move that cue later if the shot allows (a voice line may start a
  little after its cut), shorten the line, or add `--tempo 1.05`–`1.08` (pitch kept; above ~1.1
  sounds rushed). In testing the 30 s read needed both: two cues moved and `--tempo 1.07`.

Then update the cut table's "VO starts" column to the cues you used. The output is normalised to
-16 LUFS.

## 5. Preview and hand over

`roughcut.py ... --music <music> --vo <music>/vo-30s.wav` mixes the voice over the music (music
16 dB under). Give the person `vo-30s.wav` (already on the cut timeline: drop it at 0:00 on its
own track) and the raw take, and the flow link to try other voices.

Rights: it's their ElevenLabs account; commercial use of generated speech depends on their plan.
Say so once.
