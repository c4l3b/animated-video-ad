# The script doc (what the person edits from)

The person joins the clips in their editor and records the voice-over. The script doc is their
whole brief: they should be able to build the ad from it alone, without reading this conversation.
Write it as `<Name>.md` next to the clips folder. Plain, direct sentences; they're reading it while
dragging clips around.

Sections, in this order:

## 1. Intro (2–3 sentences)
What the clips are (HTML animations of real product data), where they are, their format
(size and shape, 30 fps, silent, each ends on a held frame for trimming). Which cuts the doc covers.

## 2. Editor setup
Numbered steps for their editor (ask which one if unknown; Camtasia, Premiere, DaVinci Resolve,
CapCut and iMovie all work). Cover: project size and frame rate; clips on track 1 in table order
with no gaps; how to trim to In–Out and change clip speed in that editor; plain cuts (a short fade
only into the end card); voice-over on track 2 nudged to the "VO starts" times; music on track 3
with its level; burned-in captions for muted autoplay; export.

## 3. Main cut table
| Time | Clip | In–Out | Speed | What you see | VO starts | Say |
|---|---|---|---|---|---|---|
| 0:00–0:03 | `01-hook-anim.mp4` | 0.0–3.0 | 1× | ... | 0:00.3 | ... |

- Time: where the shot sits in the finished ad. Length = (Out − In) / Speed.
- In–Out: clip seconds to keep. A clip may be used twice ("3.0–6.0, then 11.8–15.2").
- Speed: 1×–1.6×. Faster than ~1.6× makes UI motion look frantic; slow shots need a trim instead.
- VO starts: ~0.2 s after the cut, so the picture lands first.
- Say: the line for that shot. A sentence may run across two shots; say so under the table.

Check the arithmetic: the Time column must add up from the In–Out/Speed values, and the total must
fit the target length. Run `scripts/roughcut.py` on the same cut list and compare its printed cut
times with the table.

## 4. Voice-over, clean read
All lines as one block to read straight through, with a word count. Rule of thumb: about
2.5 words per second for an ad read (30 s ≈ 70–75 words). Say which phrase to drop first if
they run long.

## 5. Longer cut (optional)
Same clips at 1×, full length, plus any extra shots. Table: Order | Clip | Ends at | Say.

## 6. Music
File, where it starts, what happens when (hook pad, groove start, riser, end chord), and the
level under voice (about −20 dB) and without voice (about −8 dB). Name the rough-cut preview file.

## 7. Other shapes
How to reframe each shot for the other placements (which part of the frame to keep), or offer to
re-lay the pages at another size and re-record.

## 8. Where the numbers come from
One bullet per claim on screen: its source (export, query, file) and any caveat. Anything staged
(a dramatised hook, a scenario) is labelled as such here.

## 9. Checks before publishing
Claims the product must not make (house terminology), staged moments, people's faces and names
in real footage (consent or blur), trademarks, third-party logos.

## 10. Editing the animations
Clip → page table, how to open a page (it plays by itself after a beat), where the shared style
lives, and that clips are re-recorded with `record.cjs` after any page change. Mark any older,
superseded clips so they aren't used by mistake.
