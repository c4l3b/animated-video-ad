---
name: animated-video-ad
description: Turn an app or product into a short promo/ad video built from HTML animations recorded to MP4 clips, with real screenshots, video frames and data from the product, plus a shot-by-shot script, voice-over lines, cut order with trims and speeds, music (ElevenLabs Music, a generated licence-free bed, or the user's own track), an optional ElevenLabs voice-over placed on the cuts, and a rough-cut preview. Use this whenever someone wants a social ad, promo video, product demo video, explainer clip, launch video, feature teaser or "video for our website/Instagram/YouTube/LinkedIn" about their software, even if they only say "make a video showing how the app works" or "I want to record some clips for an ad". Also use it to redo or add a single shot, re-time clips, or write the voice-over and editing instructions for an existing set of animation clips.
---

# Animated video ad

Build each shot of a product video as a small HTML page that animates **real** product material
(screenshots, video frames, exported data, actual numbers), record each page to a clean MP4, and
hand the person a script doc that tells them exactly how to cut the clips together and what to say.
The person joins clips and records voice-over in their own editor (Camtasia, Premiere, CapCut...).

Why this works better than screen recording the real app: every shot is framed, paced and
zoomed for video; nothing flickers, loads or shows private data; text is big enough for a phone;
and a change ("make that line shorter", "slower zoom") is an edit and a re-record, not a reshoot.
It still looks honest because the pixels and numbers are the product's own.

## Workflow

1. **Agree the story** (one message, then go).
2. **Gather real material** from the product.
3. **Build one page per shot** from `assets/`.
4. **Check pages** with screenshots, fix, repeat.
5. **Record clips** with `scripts/record.cjs`; verify with contact sheets.
6. **Write the script doc** (`references/script-doc.md`).
7. **Audio and rough cut:** music (ElevenLabs, generated, or their own; `references/music.md`), an optional ElevenLabs voice-over (`references/voiceover.md`); preview with `scripts/roughcut.py`.
8. **Send** the clips, the doc and the preview; iterate on feedback shot by shot.

Put everything in one folder the person owns, e.g. `video/` or `video-scripts/`:
```
<name>-anim/     pages (one .html per shot), base.css, logo, frames/ subfolders
<name>-clips/    recorded MP4s: 01-hook-anim.mp4, 02-setup-anim.mp4 ... + README.md
<name>-music/    bed WAVs, roughcut preview, cuts.json
<Name>.md        the script doc
```

### 1. Story

Pick the length (default 30 s; offer a 45–60 s cut from the same clips) and the call to action.

Pick the frame shape from where the ad will run, and build the pages at that size (not 16:9 cropped
later; cropping loses text and the person has to reframe every shot):

| Placement | Size |
|---|---|
| Instagram Reels/Stories, TikTok, YouTube Shorts, Facebook Reels | 1080×1920 (9:16) |
| Instagram/Facebook feed | 1080×1350 (4:5) |
| LinkedIn or X feed | 1080×1080 (1:1) or 1080×1350 |
| YouTube, website, landing page, presentations, unspecified | 1920×1080 (16:9) |

Several placements: build for the main one and say in the doc how to reframe for the others. For
vertical, keep text out of the top ~250 px and bottom ~350 px, where the platform draws its own UI.
Then outline 6–9 shots, one idea each, in this arc:

- **Hook (≈3 s):** the problem, in the viewer's words. A question works ("Invoice still unpaid after 30 days? Now what?").
- **Setup (≈4 s):** how little it takes to start.
- **Core features (2–3 shots, 4–5 s each):** the product doing its job, with the result landing on screen.
- **Proof (≈3 s):** a real number. Big, simple, true.
- **Fits your workflow (≈3 s):** export, integration, sharing.
- **End card (≈3 s):** logo, one-line promise, CTA button, URL.

**Lead with positives.** Show what the product does well and how easy it is. Don't build a shot
around the product's failure cases or workarounds, even a clever one; an ad that explains how the
tool copes when it's wrong reads as "it's often wrong". A quick, confident fix by the user ("wrong
category? click it, pick the right one, done") is fine; a shot about edge-case mechanics is not.

If the person hasn't said, state your outline and assumptions in one short message and start
building; it's cheaper to change a recorded shot than to debate it in the abstract.

In that same message, ask about the audio (unless they already said), and keep building while
they decide; audio isn't needed until step 7. Use the question tool if there is one. First check
whether an ElevenLabs MCP is connected (tools such as `creative_generate_speech`,
`creative_list_voices`, a `music` node type); if it is, lead with it.

Music:
- **ElevenLabs Music** (recommended when connected): you generate an instrumental bed timed to
  the cut on their ElevenLabs account. Not connected: you write the prompt, they generate it at
  elevenlabs.io/music and send the file back.
- **Generate it here:** a quiet, licence-free bed made by `make_bed.py`, free and instant.
- **Bring their own:** a track they already have or licensed.

Voice-over:
- **ElevenLabs voice** (when connected): you pick a voice and generate the read, then place each
  line at its cue. The person can still record their own later.
- **Record it themselves** from the clean read in the doc (the default without ElevenLabs).

ElevenLabs spends credits on their account: price it first (`estimate_only`) and say the cost in
the question. If they asked for music without saying which, or you reach step 7 with no answer,
generate the free bed so the preview has sound, and repeat the question in the final message with
the ElevenLabs prompt already written.

### 2. Real material

Look in the product's repo, data folders, exports, databases, test fixtures and recordings.
For each shot, collect:

- **Pictures:** screenshots of the real UI, or frames extracted from real video
  (`ffmpeg -ss T -i in.mp4 -frames:v N frames/f%03d.jpg`). Several frames make motion.
  To screenshot a web UI (local HTML or a URL), use `scripts/grab.cjs`: full view plus named
  elements at 3x, and it prints each element's box for framing:
  `node <skill>/scripts/grab.cjs app.html <pages>/shots --size 1280x800 goal=.goal logo="header .logo"`.
  Behind a login, ask the person for screenshots rather than signing in.
- **Numbers:** actual values from the product's output (times, counts, rows). Write down where each
  came from; it goes in the doc's "Where the numbers come from".
- **Positions:** coordinates of things to highlight, in the source image's pixels (from the app's
  own output where possible, e.g. detection boxes, or measured by viewing the image).

Gaps are normal; handle them openly:
- **No logo file:** crop it from a real UI screenshot (header, app icon) or rebuild it exactly from
  the product's own CSS/SVG. Say so in the doc and ask for the real file.
- **A needed screen doesn't exist in what you have** (e.g. a setup form): draw it in the product's
  own style, and label the shot as staged in the doc so the person can swap in the real screen.

Never invent a statistic. If a moment must be staged (a dramatised hook), label it in the doc.
Respect the product's own terminology and claims rules (e.g. a product that must never call its
numbers "guaranteed" or "official") — check project docs/memory for such rules before writing copy.

### 3. Build pages

Copy `assets/base.css`, `assets/shot.js`, `assets/shot-template.html` and `assets/end-card.html`
into the pages folder. `shot.js` holds the helpers every page uses (`show`/`hide`, `cursorTo`,
`click`, `typeText`, `countUp`, `frameTo`, `preload`) and the auto-play; load it before the page's
own script and don't copy helpers into pages. Each page:

- Is a fixed stage at the chosen size: set `--w`/`--h` in `base.css` (e.g. `1080px`/`1920px`).
  The templates are laid out for 16:9, so re-lay positions for other shapes (stack panels
  vertically for 9:16; on vertical, titles start below ~250 px, not at the template's 96 px).
  Text sizes ≥ 26 px; titles 80–100 px. It will be watched on a phone.
- Has one top-level `async function start()` holding the whole timeline (`await sleep(ms)`
  between beats). `shot.js` exposes it; with `#manual` in the URL it waits, opened normally it
  auto-plays once fonts and images are ready, so the person can preview by double-clicking.
- Preloads every image it swaps in later (`preload(frames)` at top level) so nothing pops in on
  camera; the recorder and checker wait for them.
- **Ends on a held, complete state** (result shown, all text on) so the editor can trim anywhere
  near the end and hold the last frame.
- Draws marks in an `<svg viewBox="0 0 W H" preserveAspectRatio="xMidYMid slice">` sized to the
  source image, so app coordinates drop in without conversion and stay aligned when the stage
  shape crops the picture.
- Looks like the product: swap the tokens in `base.css` (`--accent`, `--hi`, `--ok`, `--ink`,
  fonts) for the product's own colours and fonts. For a light-themed product also flip the text
  colour, `.shade`, `.panel` and `.bg` to light versions; a dark ad around a light app looks
  like someone else's product.
- Shows UI screenshots at their native pixel size inside `.world` (set
  `.world { transform-origin:0 0 }` and the `<img>` to its natural CSS size) and frames them with
  `frameTo(x, y, scale)`, which puts screenshot point (x, y) at the stage centre; boxes from
  `grab.cjs` give the points. Not `object-fit:cover`, which crops a screenshot unpredictably when
  its shape doesn't match the stage.
- Keeps product text readable: UI text that ends up under ~22 px on the stage (a 14 px label in a
  screenshot that isn't zoomed) is unreadable on a phone. Zoom in on it, or rebuild that piece
  (a card, an alert) in the product's own style with its exact text at a readable size, and say
  in the doc which pieces were rebuilt.

Shot patterns that worked:

| Pattern | How |
|---|---|
| Product in action | Frame sequence swapped in `<img>` every 33–40 ms, boxes/labels drawn per frame, a result row pops into a side panel at the moment it happens. |
| Zoom to the detail | `.world` with `transform-origin` on the detail, add `.zoom` (scale 1.5–1.6, 1.2 s ease). |
| User does a step | `await cursorTo(button)` then `await click(button)`: the cursor glides to the element's measured centre, ripples, the button presses, then the result. Type with `typeText(el, text)` (55 ms a character; keep any typed string under ~1 s). |
| Step through frames | Prev/next buttons pressed in rhythm, frame number readout, the decisive frame marked. |
| Two views agree | Two pictures side by side, the same moment marked in both, a badge stating the agreement. |
| Proof | Table rows slide in (120 ms apart), then 2–3 stat cards; count the hero number up with `countUp(el, n)` (~700 ms). |
| Data out | Results list and a file/integration panel fill in the same beat, with a "live" indicator. |
| End card | Line sweep, logo, tagline, CTA button pop, URL. |

Point the cursor at elements, never at hand-typed coordinates: `cursorTo(el)` measures the element
when the cursor moves, so a zoom, a re-layout or another stage shape can't leave it clicking empty
space. `click(el)` logs an error if the tip isn't on `el`, and `check.cjs` fails on it. Use
`cursorTo({x, y})` only for a point that isn't an element. Take a check screenshot at the moment
of each click: a click that lands is the one thing viewers notice when it's wrong.

Show and hide with `show(el)` / `hide(el)` from `shot.js`. `.on` uses `!important`, so any other
class added next to it to hide or move the element silently does nothing; always take `.on` off
first (that's what `hide` does). For a custom exit, `el.classList.replace('on', 'my-exit')`.

Keep the timeline brisk: 0.3–0.7 s between beats, ≈1 s to read a title. Each clip is usually
4–8 s; a step-through shot can run 15 s because the editor will trim and speed it.

Crop anything the source has burned in that shouldn't show (camera date/time, status bars, private
names) by scaling `.world` slightly from the opposite edge (e.g. `scale(1.08)` from the bottom).
Don't rely on `backdrop-filter` to hide things: it doesn't render in the screencast.

### 4. Check before recording

```bash
node <skill>/scripts/check.cjs <pages-dir> <chk-dir> hook:400:1500:3200 live:800:3000:6000
```
Takes screenshots at those ms after `start()` (it deliberately does not await `start()`; awaiting
only ever shows the end state) and prints page errors. Read the screenshots. Check especially:
- marks sit on the right thing (box on the right person, a line on the leading edge, not a
  trailing foot or a bystander; detector tracks can switch to someone else mid-sequence, so
  stitch or hand-fix boxes);
- nothing is cut off at the edges, text doesn't overlap the subject;
- every number on screen matches the source.

### 5. Record

```bash
node <skill>/scripts/record.cjs <pages-dir> <clips-dir> hook=01-hook-anim=4200,setup=02-setup-anim=5000
```
`page=outName=ms`: record for ms (animation length + ~1 s held end). Each clip comes out at its
page's size (`--w`×`--h`), 30 fps, H.264 CRF 16, silent. `check.cjs` and `roughcut.py` follow the
same size, so no script edits are needed for vertical or square. Needs Chrome (or Playwright's Chromium) and Playwright
(`npm i -g playwright` once if `pw.cjs` can't find it), plus ffmpeg.

Clips run the requested ms plus ~0.3 s. The first frame is the page before `start()`'s first beat,
so In points usually start at 0.1–0.3 s; read them off the contact sheet.

Verify every clip without watching it:
```bash
bash <skill>/scripts/sheet.sh <clips-dir>/03-live-anim.mp4 sheet.jpg 2
```
Read the contact sheet: timing of each beat, nothing squashed or cut off, last frame complete.
Note the in/out seconds of the useful part of each clip; they go in the cut table.

Name clips `NN-name-anim.mp4` in story order (`04b`, `04c` for alternates) and write a short
`README.md` in the clips folder listing them.

### 6. Script doc

Follow `references/script-doc.md`. The cut table (time, clip, in–out, speed, what you see,
VO start, line) is the heart of it; the rest is what the person needs to finish without you.
Voice-over: ~2.5 words per second, conversational, one line per shot, CTA said out loud
("Try it free. Click the link, or visit example.com.").

Most social video is watched muted, Reels and TikTok included. Always give the cut table an
"On screen" column and make the on-screen text carry the story by itself. Where there is a
voice-over (Reels, TikTok, Shorts), also add burned-in captions in the editor steps, placed in
the vertical safe zone and dropped on shots whose title already says the line. For feeds with no
voice-over planned (LinkedIn, X, Facebook feed), make the voice-over optional and skip captions. Music levels: give dB for Premiere/Resolve/Camtasia; in CapCut and iMovie, which
use a percentage slider, about 10–15% under a voice and 35–45% alone.

### 7. Audio and rough cut

Do whichever options the person picked (step 1). Read `references/music.md` before making music
and `references/voiceover.md` before an ElevenLabs voice-over.

- **ElevenLabs Music:** a `music` node, `eleven_music_v2_5`, `instrumental: true`, duration a few
  seconds over the cut. It doesn't follow timings in the prompt exactly, so measure where its beat
  comes in and shift it onto a cut with `roughcut.py --music-at`.
- **Generate:** `python3 <skill>/scripts/make_bed.py --total 30 --groove-at 3 --end-hold 3 --out <music>/bed-30s.wav`.
- **Their track:** fit it to the cut (start point, end on the end card, fade).
- **ElevenLabs voice-over:** one take of the clean read, then `scripts/place_vo.py` cuts it into
  lines and puts each at its "VO starts" time, reporting any line that runs into the next.

You can't listen to any of it: check audio as a picture (waveform, spectrum, loudness) and tell
the person you checked it only that way.

```bash
python3 <skill>/scripts/roughcut.py <music>/cuts.json <music>/roughcut-preview.mp4 --music <music>/bed-30s.wav [--music-at S] [--vo <music>/vo-30s.wav]
```
`cuts.json` mirrors the cut table. It prints each cut's start time: compare with the table.
Music is normalised and set 8 dB down alone, 16 dB under a voice-over. With an ElevenLabs
voice-over the preview is close to a finished ad; still say it's a preview and the person's
editor makes the final.

### 8. Deliver and iterate

Send the clips (or the rough-cut preview) and the doc with the file-sending tool if there is one.
Feedback usually targets one shot ("that label is on his back foot"): fix the page, re-check,
re-record only that clip, update its row in the doc (in–out, speed, line), re-send it. When the
person changes direction ("focus on the positives"), rework the affected shots' story, not just
their wording, and say what changed.

## Lessons (each cost a re-record)

- Screencast without `Emulation.setDeviceMetricsOverride` captures ~993 px tall and stretches it;
  `record.cjs` sets it. If you write your own recorder, keep that.
- A clip opening on a long static frame means the first screencast timestamp wasn't clamped.
- Await nothing in checks; screenshot during the animation.
- A box from a tracker may belong to a different person early in a sequence; verify per frame.
- Static backgrounds with people in them distract from a setup shot; pick an empty frame.
- Repeated numbers (a line number next to a place number) confuse; cut redundant columns.
- Fade lists in at the top edge (mask) instead of hard-clipping rows.
