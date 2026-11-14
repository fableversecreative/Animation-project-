---
name: fable-animation-1
description: Make FableVerse animated history Shorts (YouTube @FableVers + Instagram @fableverse.creative) in the premium style - v5 "Option B" characters, Blender 3D background plates on CPU or painted 2.5D sets, one-word captions, full sound. Covers script, voice script, timing, comparison/preview, fixes, final render, thumbnails and posting. Use for every new FableVerse Short.
---

# FableVerse premium Shorts (fable animation 1, Nov 2026)

The user should never have to re-teach any of this. Follow it every time.

## 0. Where everything lives
- **Engine (v3 + v2 premium code):** GitHub `fableversecreative/Animation-project-`, `main` branch, file `fableverse_engine_v3.zip` (60 files: v2/char3, face, set25d, look, props, sfx3, blender/hall_plate.py + textures, napoleon_rabbits project). Fetch with `git show origin/main:fableverse_engine_v3.zip > engine.zip` and unzip.
- **Locked character design (v5 Option B):** branch `claude/greeting-dbsr4p`, folder `character_v5/char5.py` (set `char5.STYLE.update(legs='thick', arms='thick')`).
- **Blender plate + compositor code:** branch `claude/greeting-dbsr4p`, folder `compare_5s/` (plates.py, comp5.py, make_paint.py, run_both.sh).
- **Drive "Animation" folder:** finished MP4s, approved thumbnails, user uploads. The Drive connector only downloads files **under 10 MB**; small code files come back base64 inline and cannot be saved reliably. For bigger files or folders, ask the user to zip and upload to GitHub: `https://github.com/fableversecreative/Animation-project-/upload/main` (25 MB per file, zip folders first, phones cannot upload folders).
- Laptop (RTX 3050) Remote Control folder sharing is NOT available to this account yet; do not wait on it. Everything runs in the cloud session.

## 1. Workflow (user's standing rules)
1. User picks the topic. Offer ideas only when asked. True funny history with a twist, under 1 minute (110-125 words).
2. Plain script first, wait for approval. Then one paste-safe paragraph "Voice script for <title>" with ElevenLabs v4 tags. Voice: Roger (Laid-Back Casual Resonant), stability 50, similarity 75. **Never** use or connect ElevenLabs yourself; the user records and uploads the MP3.
3. **Never spend vidIQ or other credits without stating the cost first and getting a yes.** Free: vidiq_social_post_list, vidiq_social_account_list, vidiq_user_channels, vidiq_video_upload. vidiq_user_videos costs 5 credits.
4. **Ask permission before using Blender**, and state the time it needs.
5. Do not render video until the user says so. Pictures/stills for design questions are fine.
6. 360p preview first; fixes as short clips (changed part + 1 s either side); full 1080x1920 only at the end.
7. 4 thumbnail options (9:16 scene still, big bold headline, red arrow). Save only the approved one to Drive.
8. Post only at **7:30 AM or 11:45 PM IST**, YouTube + Instagram, tier-one audience. vidIQ: Unlisted first, Public after the user checks; publish only on explicit "yes". Remind the user to set Drive files back to Restricted. Scheduled vidIQ posts cannot be cancelled.
9. Progress line every step: Planned > Scripted > Voiceover > Preview > Ready > Scheduled > Posted.
10. Self-review contact sheets before sending anything; fix what looks bad without being asked.
11. After every deliverable, commit + push to the session branch (a stop hook requires a clean tree).

## 2. Voice timing (no internet ASR here)
- Whisper/HuggingFace downloads are blocked. Use `ffmpeg silencedetect` at -45/-35/-30 dB, d=0.18; speech segments map 1:1 to script phrases (check counts match), then spread words by syllables -> `work/timing.json` (phrases) + `work/words.json` (words). Show the user the phrase/time table before animating.

## 3. Characters: v5 Option B (LOCKED, original FableVerse designs)
Learned from studying top premium history Shorts (technique only, never copy their characters):
- **Big round ball head** (r 80) with soft gradient shading (light top, cool bluish bottom), white highlight, thick dark outline (OL 7.5, ink `#231a2e`).
- **Small black oval eyes** with **heavy eyelid lines** (skin-colour lid cap + thick line, tilting with emotion) - gives the cool deadpan look. Shock/scared = white ring eyes with small pupils.
- **Thick tapered brows do most of the acting.** Tiny mouths; big mouths only for shock/scream/grin.
- **Bean torso** with gradient shading and clothes drawn on it (lapels, gold buttons, epaulettes, sash, strap).
- **Legs: v4 style** - trouser tubes (w 22) with chunky boots. **Arms: thick sleeves with white glove mitts.** (User preferred these over thin stick limbs.)
- One signature feature each: Napoleon forelock + big shaded bicorne with cockade; Berthier moustache + red sash + gold-trim bicorne; Tsar blond sideburns + white uniform + plume; hunter beard + rifle strap + tricorne; farmer stubble + straw hat + straw in mouth.
- Emotions: neutral, proud, smug, worried, scared, shocked, angry, sad, deadpan, happy, determined, confused. No lip sync on narration.
- Rejected looks: v3 tall egg heads with dot eyes (looked asleep), v4 cute big-eye/blush chibi style (too childish).

## 4. Backgrounds: Blender plates vs painted
- Blender runs here as the `bpy` pip wheel (Python 3.13, `pip install bpy`, ~430 MB). **Cycles CPU only** (Eevee needs a GPU and fails). OCIO colour management does not load: render **EXR**, load it back with `bpy.data.images.load`, tone-map in numpy (auto exposure to log-average 0.20 + ACES fitted curve + sRGB) and save PNG. OpenCV cannot read EXR here.
- One **still plate per shot** (not per frame). Plates cover design coords x -108..1188, y -192..2112 (1.2x overscan of 1080x1920); export anchor points (feet/head/corners) with `world_to_camera_view` to JSON and composite 2D toons on top; camera moves = 2D push/pan on the plate.
- Field set: 300k + 160k instanced grass blades (particle hair, object instances), flowers, pine/round trees at 55-95 m, displaced distant hills, warm haze cards, camp tents with tricolour flags, Multiple-Scattering sky + low warm sun. Map table: wood_floor.png table, curled parchment.png, brass compass, candle + point light, coins, wax seal, area key light.
- Measured cost at preview size (778x1382, 64 samples): hero field 2:08, map 0:52, close-up 1:44, rabbit close-up 2:56 (total 8 min for 4 plates). Full 1080p plates take roughly 2-3x longer.
- Painted alternative (no Blender): napoleon_rabbits `bgimg()` sets warped to the same plate convention + v2 textures (seconds).
- Verdict from the 0-6 s comparison: Blender clearly wins on prop tables (map) and depth-of-field close-ups; smaller gain on wide fields. Offer the user **A** (painted, ~2 h to preview), **B** (all Blender, ~4-4.5 h), or **mixed** (Blender for key shots, ~3 h).
- Full per-frame Blender animation is not practical on CPU (22-65 h for 44 s). Fake life with 2D overlays (flicker, swaying foreground grass).

## 5. Premium look + editing
- New shot every ~1-1.5 s; close-ups, low and tilted angles; macro prop shots of objects the story names.
- Faces above the caption line: chin must clear y≈1190 (face_y ≈ 1190 - 80*sc*zoom - 80).
- Look stack (v2 look.py): god rays from the sun, dust motes, bloom (thr ≥ 225), warm grade, contrast 1.06, vignette, grain 4; boost Blender plate saturation ~1.18.
- Whip-pan blur on every cut; shake on impacts; hat-stamp / pop-in HUD titles.
- Captions: one word at a time, lowercase, white with heavy dark stroke + soft shadow, y≈1190, small pop-in; key words yellow.
- Map overlays: draw countries in parchment space with light smoothing (Chaikin 1 pass), warp with a homography onto the parchment corners; red conquest pops in sequence.

## 6. Sound
- Whoosh on every cut, a crisp effect about every 0.7 s (pops, stamp, ticks, boing, creak, squeaks, paw rumble, whacks, footsteps, carriage rattle, munching), ambience beds (birds, crickets on comedic pauses, tent room tone), light pizzicato march.
- Mix: music ≈ -7.5 dB under voice with 30% ducking while the voice is on; SFX ≈ -10 dB; loudnorm to -15 LUFS, true peak -1.5.

## 7. Account status (Nov 14 2026)
- Connected in vidIQ: YouTube @FableVers (UCmhlUL9w3S9Tn42boNf8oBA), Instagram @fableverse.creative - both can publish.
- Posted: One Wrong Turn (WW1), Emu War, Dancing Plague (Instagram Dancing Plague scheduled 11:45 PM IST Nov 14).
- In progress: **Napoleon vs Bunnies** - script approved, voice timed (44.2 s, 20 phrases), preview v1 (old style) done, 0-6 s Blender comparison done, v5 Option B characters locked; waiting for the user's background choice (A / B / mixed) and slot.
