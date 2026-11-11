# Animated video ad

A skill for Claude Code and Codex that turns your app into a short promo video. Ask for "a 30-second ad for my
app" and the agent builds each shot as a small HTML animation of your **real** screens and numbers,
records every shot to an MP4 clip, and writes you a script doc: which clip goes where, where to
trim, how fast to play it, and what to say over it. You join the clips in your own editor
(CapCut, Premiere, Camtasia, Resolve, iMovie...) and add your voice.

What you get:

- **Clips** at the right shape for where the ad runs: 9:16 for Reels, TikTok and Shorts, 1:1 or
  4:5 for LinkedIn and feeds, 16:9 for YouTube and websites. Silent, 30 fps, each ending on a held
  frame so you can trim freely.
- **A script doc** with editor-specific steps, a cut table (time, clip, in/out, speed, what's on
  screen, when to speak, the line), a clean voice-over read, crop notes for other shapes, where
  every number came from, and checks before you post.
- **Music:** a quiet licence-free bed generated on the spot, your own track fitted to the cuts, or
  an ElevenLabs Music track if you have ElevenLabs connected.
- **Voice-over (optional):** with ElevenLabs connected, the agent picks a voice, generates the read
  and places each line on its cue.
- **A rough-cut preview** of the whole ad with music (and voice), so you can judge the pacing
  before you edit.

The clips use your product's own screenshots, data and wording. It doesn't invent statistics,
labels anything staged, and keeps the story on what your product does well.

## Install

In Claude Code (2.1.275 or later):

```
/plugin install animated-video-ad --marketplace c4l3b/animated-video-ad
```

On older versions: `/plugin marketplace add c4l3b/animated-video-ad`, then
`/plugin install animated-video-ad@animated-video-ad`.

Or copy `plugins/animated-video-ad/skills/animated-video-ad` into `~/.claude/skills/`.

### Codex

Codex reads this repo's plugin catalog as it is:

```
codex plugin marketplace add c4l3b/animated-video-ad
codex plugin add animated-video-ad@animated-video-ad
```

Start a new Codex session afterwards. Or copy `plugins/animated-video-ad/skills/animated-video-ad`
into `~/.agents/skills/` (or `.agents/skills/` in a project to share it with your team).

### ChatGPT

The skill follows the shared `SKILL.md` format, but it records real browser pages and runs
ffmpeg, so it needs a local machine. Use it through Codex (CLI, app or IDE extension) rather than
a ChatGPT chat.

Then ask Claude or Codex something like *"Make a 20-second Instagram ad for my app. The web app is in ./web and
the numbers I can quote are in facts.md."*

### Requirements

The skill records real browser pages, so it needs a computer, not a web sandbox:

- **Google Chrome** (or Playwright's Chromium)
- **Node.js** and **Playwright**: `npm i -g playwright`
- **ffmpeg** (with ffprobe)
- **Python 3** with **numpy** (for the generated music bed and the audio tools)

### ElevenLabs (optional)

If the ElevenLabs MCP is connected, the skill offers ElevenLabs Music and an ElevenLabs voice-over.
It prices each generation first and tells you the cost; generations use your own ElevenLabs
credits (a 30 s music bed plus a 30 s read was about $0.20 in testing). Check that your plan
allows commercial use before running generated audio in a paid ad.

## What's inside

```
plugins/animated-video-ad/
  skills/animated-video-ad/
    SKILL.md              the workflow Claude follows
    assets/               base.css, shot.js helpers, shot and end-card templates
    scripts/              record.cjs (page -> MP4), check.cjs, grab.cjs (screenshots),
                          sheet.sh (contact sheets), roughcut.py, make_bed.py (music),
                          place_vo.py (voice-over on cues)
    references/           script doc layout, music, voice-over
  evals/                  two test products (Shelfie, Pulse) with graders
```

Run the tests with `claude plugin eval plugins/animated-video-ad` (real, billed model runs).

## License

MIT
