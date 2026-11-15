---
name: fable-animation-1
description: Make a FableVerse animated history Short end to end with the combined pipeline (locked v5 cast, cloud or RTX 3050 rendering) - true story with a twist, ~125-word escalating script, ElevenLabs voice script, user's voiceover kept untouched, word-timed shots, bean-head cartoon characters in a painted ink-outlined 3D world (three.js inside Remotion), dense SFX, 360p preview and fix clips, 1080x1920 final with pass/fail QA, 4 thumbnails, posting kit and vidIQ posting. Use for any new FableVerse Short, any cartoon/animated history or "what if" Short, or when the user says "fable animation 1".
---

# Fable Animation 1

The user's chosen mix of the `shorts-pipeline` engine (build quality) and the FableVerse channel workflow (approvals, previews, posting).
Everything is code: world, characters, camera and sound. No AI video generator, no Blender.

## What's in this folder
| Path | Use |
|---|---|
| `templates/starter/` | Remotion project skeleton (pinned working versions, tsconfig, `src/index.ts`, `src/Root.tsx`) |
| `templates/bridge/` | Full example short (world, characters, ink, lens blur, grade, story/camera). Copy to `src/videos/<name>/` |
| `templates/beats/camera.ts` | Camera governor `govern()` |
| `templates/audio/` | Synth SFX, score, mix (`mix.py`: set music to -6 dB under voice), loudness |
| `templates/voice/` | `align.py` (voice -> words.json), `placeholder_words.py`. `tighten_energy.py` is NOT used (voice stays untouched) |
| `templates/scripts/` | `stills.mjs`, `render_chunks.ps1` (has `-Scale`, `-Out`, `-From`, `-To`), `dump_story.mjs`, `short_qa.py`, `sbs_sheet.py`, merge helpers |
| `scripts/` | QA: `pacing_check.py`, `cam_speed.py`, `flicker_check.py` |
| `references/` | `SCRIPT_FORMULA.md`, `STYLE_BIBLE.md`, `reports/*.md` (measured look/motion/pacing targets), `characters_v5_optionB.jpg` (locked cast) |
| `templates/characters/chars.ts` | **Locked FableVerse cast (v5 Option B)** drawn on character cards: Napoleon, Berthier, Tsar, hunters, farmer, shako soldiers, drummer; 14 expressions; bunnies (side/front/back, 7 coats); props (musket, stick, clipboard, carrot), thought bubbles, quill, hat pin |
| `templates/napoleon/` | Second full short ("Napoleon vs Bunnies", 44.6 s): `story.ts` (24 shots from words.json, hold/track cameras, per-shot DOF), `stage.ts` (who/where/expression per frame, camp life, foreground tufts), `world.ts` (field + camp, war-map tent, treaty tent, farm, carriage, crates, campfires; uses ../bridge modules), `Napoleon.tsx`, `captions.tsx` (pop captions, Poppins 900) |
| `templates/scripts/clip.mjs` | Linux/cloud renderer: bundle once + renderMedia for a frame range (`node scripts/clip.mjs out.mp4 from to scale concurrency`) |

Reference reports are for look and pacing only. Story, characters, lines and shots are always original. Never copy another channel's characters, shots or frames.

## Standing rules
- **Topic:** the user picks it every time. Titles on the schedule are not confirmed.
- **Facts:** true history with a twist, every claim researched with a source; drop single-source or unclear claims. Don't present a legend as fact ("legend says" if the user wants it). No real living people as characters or the butt of a joke, nothing graphic, nothing political.
- **Voice:** the user records it in ElevenLabs (Eleven v4, "Roger", stability 50, similarity 75, Language English, audio effects off). Never generate or connect ElevenLabs yourself. **Never cut pauses, re-time, speed-change or edit the voice.** The picture is timed to the voice exactly as recorded.
- **Credits:** never spend vidIQ or any tool credits without first stating the cost of each step and getting a yes.
- **Progress line** at every step: which video, step done, what's next, overall progress against the schedule.
- Self-review every frame through contact sheets before sending anything; fix what looks bad without being asked.
- Keep a `NOTES.md` per project and save after every step.

## Pipeline
1. **Topic and facts.** User gives the topic. Pick one surprising true story with a physical cause and effect (must be visual), ideally someone doubted or mocked and proven right or wrong. Facts + sources at the top of `SCRIPT.md`.
2. **Script** (~125 words, under 1 minute; tagged reads run long). Read `references/SCRIPT_FORMULA.md` first.
   - Shape: **hook** (0-3 s, no names/years/places, hides a question) -> **stakes + doubt** -> **ladder** of 4-6 rungs, a bigger event every 5-7 s -> **lowest point** -> **reversal** -> **reveal as the last line** (or loop into the hook).
   - **No date or background line right after the hook**; go straight to the next action.
   - One protagonist, <= 3 speaking roles, 2-4 lines of mockery/doubt. No explanation section, no moral.
   - Plain spoken English, contractions, numbers as words, never describe what the viewer already sees.
   - Send it as readable plain text (not a code block) with word count, estimated length and the self-check table. **Wait for approval.**
3. **Voice script.** After approval send ONE paste-safe paragraph (no line breaks) labelled **"Voice script for <title>"** with inline v4 tags (`[mysterious]`, `[short pause]`, `[excited]`, `[whispers]`, `[chuckles]`...). Spoken words must equal the approved script. The user records and uploads.
4. **Timing.** Convert the upload to 48 kHz wav `voice/<name>/voice.wav`, then
   `python -I voice/align.py SCRIPT.md voice/<name>/voice.wav src/videos/<name>/words.json` (needs `pip install faster-whisper`).
   Hand-fix words.json only if alignment is wrong; never touch the audio. Before the voice exists, use `placeholder_words.py`.
5. **Shot plan.** Copy `templates/starter/` (first time) and `templates/bridge/` to `src/videos/<name>/`, register the composition in `src/Root.tsx` at **1080x1920, 30 fps**.
   - Cue every shot from a word: `C(line, wordIndex)` = word start - 2 frames, so the voice drives all timing.
   - Write `SHOTS.md` first (read `references/reports/pacing.md`): every visual event against words.json.
     - An event at least every 1.5 s; nothing frozen > 0.5 s.
     - An insert or prop for every claim and number (map with pin, stopwatch, document + stamp, counter). At least half the concrete nouns/numbers get one.
     - Faces or key prop >= 40 % of frame height for >= 70 % of screen time; faces always above the caption line. Wides <= 2 s. No empty half-frames.
     - >= 3 light/mood states across the acts; the reveal gets its own visual world.
     - Frame 0 is a tight, already-moving shot of the hero and the odd thing; last frame lands on a hit or matches frame 0 for a loop.
6. **Camera** (`templates/beats/camera.ts`, wrap every shot in `govern()`): eye-level only (within +/-12 deg): wide, side, three-quarter, over-the-shoulder, medium. Smooth 3D glides (smootherstep 20-30 f, never < 18 f, >= 45 f apart). Holds are still except a subtle push-in (~4.5 %/s, punch beats <= 18 %/s). Hard cuts only at place/time changes or travel > ~7 m. No orbit drift, sway or handheld. Impact kicks are fine. Close-ups only on punch lines.
7. **World** (`lights.ts`, `shade.ts`, `build.ts`, `paint.ts`, `world.ts`): each location at its own x slot (0, 400, 800...). Muted brick/cream/ochre/terracotta albedos, warm grey stone, ochre wood with near-black seams; never lemon or lavender. Ink #030303. Bloom thr 1.0, int .5. Film grain OFF.
8. **Characters** (`toon.ts`, `cast.ts`, `cardshade.ts`): original FableVerse **bean-head** characters, plum outline #241726, stick limbs, ~3.5 head-heights, blinks every 0.5-2.3 s, walk bob 5 %. No lip sync on narration; they act with expressions and poses. Render a character test sheet before using a new design.
9. **Sound** (`audio/`): `node scripts/dump_story.mjs <name> out/<name>/story.json`, then a per-short `audio/<name>_sound.py` -> `out/<name>/mix.wav` (48 kHz, exact length) + cues.md.
   - A crisp effect on nearly every action (about one hit per 0.7 s): whoosh on every cut, footsteps, swishes, ticks, gulps, paper, stamps, impacts, creaks. Ambience bed per location. A sting/impact on the twist.
   - Music: light orchestral/pizzicato or march, **6 dB under the voice** (set every `MUSIC_TARGET` section in `mix.py` to -6.0). Voice is gain-only. Master -15 LUFS, -1 dBTP limiter. Voice always clear over music. Use the user's real SFX packs when given.
   - Lock picture timing first; any timing change means re-running the sound.
10. **Captions** (drawn in the composition or burned in at mux), 1-2 words per chunk from words.json, quote marks stripped. **Choose the style per video by what reads better on that short's backgrounds** (render a still with each and pick):
    - **Pop style:** bold white, dark outline + soft shadow, pops in on its word, key words and numbers in yellow (bigger pop with overshoot), centred at y ~ 69 % of height.
    - **Plain style:** white heavy sans (Segoe UI Black) ~74 px, ~5 px black stroke + soft shadow, as-spoken case, fixed line at y ~ 70 %, no pop.
    No other on-screen labels; in-world numerals/signs are fine (never mirrored).
11. **Stills check:** `COMP=<Id> node scripts/stills.mjs out/<name>/x_ 100,400,900 0.5` (set `REMOTION_TMP`). Contact-sheet, check the readability traps below, fix before rendering.
12. **360p preview:** `powershell -File scripts/render_chunks.ps1 -Name <name> -Comp <Id> -Scale 0.3333333333333333 -Out preview -Concurrency 2 -Tmp D:\remotion-tmp`, mux with mix.wav (`-map 0:v:0 -map 1:a:0 -c:v copy -c:a aac -b:a 160k`). Send it and wait.
13. **Fix rounds:** list concrete numbered fixes, let the user pick. Re-render only the changed part as a short clip: the change plus 1 s before and after, merging changes within 2-3 s into one clip (`-From/-To`, `-Out fix_<n>`). Stills for look-only fixes. Repeat until the user says "Done". Undo = restore the exact previous version, then ask.
14. **Final:** `render_chunks.ps1 -Name <name> -Comp <Id> -Scale 1 -Out final -Concurrency 2 -Tmp D:\remotion-tmp`, then
    `ffmpeg -i video.mp4 -i mix.wav -map 0:v:0 -map 1:a:0 -c:v copy -c:a aac -b:a 320k final.mp4`. Upload copy ~5.5 Mbps (< 40 MB).
15. **QA (all must pass):**
    - `python scripts/short_qa.py final.mp4 out/<name>/qa shots.json`: black/white/frozen/pop frames, loudness, sheets.
    - `python scripts/pacing_check.py final.mp4`: median MAD/s >= 15, longest quiet <= 0.9 s, last 10 s no calmer than median, length 35-60 s. Exit 1 = a target failed.
    - `python scripts/cam_speed.py final.mp4`: p90 <= 20 px/f, frames >= 40 px/f <= 2 %. (Measured on 1080 wide.)
    - `python scripts/flicker_check.py final.mp4`: A-B-A frames; planned cuts/flashes show too, check by eye.
16. **Thumbnails:** 4 options A-D, 9:16 clean scene still (no captions), big bold headline at the top (white + yellow, dark outline), soft glow on the key character, red arrow. Wait for approval; keep only the approved one.
17. **Posting kit** as separate copy-paste blocks:
    - **Title:** calm curiosity style ("Why X...", "How X worked"), matching the chosen thumbnail.
    - **Description:** one-line hook, the story, "📌 Accuracy note", one comment question, "🔔 Subscribe to @FableVerse — Stories Beyond Imagination.", then `#shorts #history #animation #funnyhistory #fableverse` + 2-3 topic hashtags.
    - **Tags:** start with `FableVerse, FableVerse stories, Stories Beyond Imagination, animated stories, animated history, funny history, history animation, history shorts, cartoon history, history facts, life lessons, story time`, then topic tags; < 500 characters, < 30 tags. Check the channel name hasn't changed.
    - **Pinned comment:** a playful question (the user posts and pins it).
18. **Posting (vidIQ, all free steps):** the user uploads the final MP4 to Google Drive folder "Animation" (folder ID 1PajVoHSBZhhrYbapdetxBZfBh2FYNUxs); share anyone-with-link, import with `vidiq_video_upload`. Thumbnail: upload to the same Drive folder, share, `vidiq_upload_image` with `https://drive.usercontent.google.com/download?id=<id>&export=download`. `vidiq_social_post_draft_create` for YouTube (categoryId 27) + Instagram; show the draft, ask privacy, **Unlisted first**, Public only after the user checks and says "yes". Then `vidiq_social_post_status` and give the link. Remind the user to set Drive files back to Restricted.
    - Post only at **7:30 AM or 11:45 PM IST** (tier-one audience). Channel: FableVerse (@FableVerse.creative), same Shorts on Instagram.
    - Keep the Claude Sheet "FableVerse 30-Day Posting Schedule" (https://claude.ai/artifact/VGcHJfk6GTYaD3fJL1HnoT) status in step: Planned > Scripted > Voiceover > Preview > Ready > Scheduled > Posted. Read it before planning.
    - Every 3 days, ask whether to run a performance analysis (state any credit cost first).

## Before sending anything
- Faces visible and above the captions in every shot; no empty half-frames; nothing cut at frame edges.
- Captions in sync; no lip sync on narration; voice untouched.
- Every cut has a whoosh, every action a sound; the voice is always clear over the music.
- All designs original. Progress line included; any credit cost stated up front.

## Where to render (measured Nov 2026)
- **Cloud session (no GPU):** works with software WebGL. `GL=swangle`, `BROWSER=/opt/pw-browsers/chromium_headless_shell-*/chrome-headless-shell-linux64/chrome-headless-shell`,
  inputProps `{"post":{"dpr":0.3333}}` for 360p, `node scripts/clip.mjs out.mp4 0 <last> 0.3333333333333333 2`.
  Speed: ~1.3 s/frame with concurrency 2 -> **44 s short = ~28 min at 360p**. Single stills are slow (~35 s each, shaders recompile) - batch them in one `stills.mjs` call (~9 s each).
  Scale must make integer sizes: use 0.3333333333333333 (not 0.3333333).
- **Laptop RTX 3050 (Windows):** much faster (360p ~10-15 min, 1080p ~45-60 min). Cloud chats can NOT reach the laptop for this account (Remote Control folders show "not available");
  use a **local Claude Code session on the laptop** (Claude desktop app -> Code -> local session in the project folder): `git pull`, then
  `npx remotion render <Comp> out\x.mp4 --scale=0.3333333333333333 --concurrency=2 --gl=angle`. Full guide: repo `remotion/LAPTOP_RENDER.md`.
- Project lives in GitHub `fableversecreative/Animation-project-` (branch `claude/greeting-dbsr4p`, folder `remotion/`). Build in the cloud, push, render on either side.
- Tooling in a fresh cloud box: Node 22 + ffmpeg present; `npm install` in the project (~30 s, 372 MB), `pip install scipy fonttools brotli` for the audio templates,
  Poppins ExtraBold/Black from `@fontsource/poppins` (convert woff2 -> ttf with fontTools for Python captions). Whisper model downloads are blocked:
  time the voice with `ffmpeg silencedetect` (-45/-35/-30 dB, d 0.18; phrases map 1:1 to the script lines, words spread by syllables).
- Drive connector downloads only files < 10 MB and returns small text files as base64 inline: ask for code/folders as a **zip on GitHub** (25 MB/file via the web upload page) instead.

## Look lessons from the Napoleon build (do these by default)
- **Cast:** always use `templates/characters/chars.ts` (v5 Option B: big round shaded head, small dark eyes with heavy lids, thick brows, bean torso, trouser legs + chunky boots, thick sleeves + white gloves). The user rejected tall egg heads with dot eyes (look asleep) and cute big-eye/blush chibi faces.
- **Material index bug:** never pick a material with `arr[(k + Math.floor(x)) % n]` - negative x gives `undefined` and Batch renders it **pure white** (looked like white blobs on every tree). Use `((v % n) + n) % n`.
- Distant hills must be dark forest greens (#4f7344 ...) and low; pale hill domes read as clouds. Sky clouds at >= 20 deg elevation (y ~250 at 650 m).
- Fog pushed back (day 60-520 m) so mid-distance trees keep their colour. Golden light: lift `shade` to ~[0.42,0.33,0.44] or the ground turns navy; front-light golden shots that look at grass (`az` 120-140).
- Life in every wide: background soldiers/townsfolk cards idling and walking, campfires (flame card + small translucent grey smoke, opacity <= 0.32, size <= 1.5 m), cannons, barrels, stacked muskets, standards.
- Ground: tiled grassHD + a broad light/dark patch overlay (NOINK, depthWrite off) + many SHORT crossed-card tufts (0.1-0.22 m, light greens, thin 55 % outline). Tall dark tufts look like reeds.
- Foreground framing only at frame edges, never across a face; DOF cInf: CU/insert 12-13, MS 7-9, wides 3-4.
- War map / signs: unlit `MeshBasicMaterial` canvas textures (lit ones go dark inside tents); redraw per state (cache one texture per state).
- Faces stay above the caption line (captions at y ~1325): look target at face height, chin clear by ~120 px.

## How the user wants to work
- Tell the user **what you are doing, where (cloud / laptop) and roughly how long**, at every step; no need to ask permission for builds or test renders.
- Ask before Blender, credit spends, deletes and anything posted. Comparison clips (A/B) are welcome when a choice is expensive.
- Self-review contact sheets before every send; list proposed fixes as numbers.

## Setup gotchas (Windows laptop)
- Use React 18 + @react-three/fiber 8 + @react-three/postprocessing 2 (newer versions render blank). The starter package.json pins them.
- Set `REMOTION_TMP` / `-Tmp` to a big drive; Remotion never deletes `remotion-webpack-bundle-*` / `puppeteer_dev_chrome_profile-*` (60+ GB). Clear them when nothing renders.
- Two GPUs: `npx remotion browser ensure`, set `chrome-headless-shell.exe` to High performance in Windows graphics settings, render with concurrency 2.
- PowerShell 5 `Set-Content -Encoding utf8` writes a BOM and breaks webpack; write files BOM-free. `[IO.File]` needs absolute paths. Patch source with a small Python script, not PS aliases.
- In JS strings write `"D:/remotion-tmp"`, never backslashes. Scratch `.ts` files inside `out/` break `tsc`: name them `.txt`.
- Kenney GLBs are optional; 404s are harmless.
- Ink is its own pass before the blur. R3F clamps dpr >= 1. Sub-agents may not write files: ask for a short final message and save it yourself.

## World and framing traps (check every set/shot)
- Portrait framing: at distance d and fov 40 the frame is only ~ +/-0.2 d wide.
- Face height ~1.55 m: look at ~1.36 to keep faces above captions.
- Rooms need shadowless ceilings; inside walls/tubes `cast = false`, black end caps.
- Each set's ground inside its own x slot, never coplanar with another. Never rotate a set group far from the origin.
- Shots start 2 frames before their word: clamp any (t - word time) index at 0. A rolling card pivots at its soles: re-centre it.
- Flat faces away from the sun go navy: turn the sun (az ~150). Distant boxes read as tower blocks: use painted cards.
- Props < ~2 m from the lens become blobs. Paper props: polygons, not ellipses. In-world text inside the visible width, never mirrored.
- Hair: wavy front, a quiff, a few swept strands from one parting (even strands read as a knitted cap).
- Glossy (roughness .35) makes blobs; .7 is safe. Painted signs: unlit material. Swings: two ropes to a wide plank. Period-correct flags.
- Golden rim light: inner rim only. Free unused unique pose textures (VRAM). Judge dark-on-dark limbs at full size.
- Objects sit on surfaces; one design per recurring object; characters face where they act; statues and paintings never move.
