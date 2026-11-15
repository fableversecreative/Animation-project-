# Visual pacing: what keeps the eye from leaving (measured 2026-11-04)

Complements `motion.md`, which covers *how* the camera and characters move (glide curves, push-ins, kicks, blinks).
This file covers *how often the picture changes* and *how the visuals escalate with the story*.

## Method
Seek sampler in the browser on the YouTube player: 10 samples/s, frames shrunk to 54x96 grey, caption band (58-80 % of
the height) excluded.
- **MAD**: mean absolute luma difference between samples 0.1 s apart, on a 0-255 scale. This is the amount of picture change.
- **Hard changes**: samples whose luma histogram changes > 25 %. These are cuts, flashes, whips, snap reframes and big light changes. They are not all true cuts.
- **Quiet run**: the longest stretch with MAD < 1.5, i.e. the picture nearly frozen.
- Contact sheets were taken at 1 frame/s.

| Video | Views | Length | Median MAD/s | Hard changes | Longest quiet |
|---|---|---|---|---|---|
| Ricks: Ancient Jar | 31.3M | 64.9 s | ~17 | ~17 | 0.6 s |
| Ricks: Perfect Railroads | 18.7M | 65.2 s | 18.8 | ~16 | 0.4 s |
| Ricks: Job Nobody Wants | 16.4M | 60.5 s | 16.0 | ~20 | 0.1 s |
| MrPasserby: Movers | 4.3M | 59.3 s | 29.8 | ~60 | 0.1 s |
| MrPasserby: Seed | 1.8M | 65.0 s | 34.8 | 88 | 0.3 s |
| MrPasserby: Paradox | 0.6M | 56.6 s | 14.7 | 44 | 0.9 s |
| **Ours: Newton coins** | 2.1k | 89.6 s | **11.1** | 49 | **2.8 s** |
| **Ours: Edo firefighters** | 1.4k | 71.4 s | 24.5 | 66 | 0 s |

Takeaways:
- **The picture never stops.** None of the hits has a near-frozen stretch longer than 0.9 s. The Newton video held talking-head close-ups of the same face for several seconds (frames 30-37 and 60-69) and froze for 2.8 s.
- **Raw motion is necessary but not enough.** The firefighters video moves as much as the hits but still stalled, because of *what* is on screen (see below), not how fast it moves.
- **There are two valid tempos.** Ricks Clips keeps cuts rare and the camera always gliding. MrPasserby cuts about once a second to a new insert. Both keep the change rate high.

## What the hits show on screen (contact sheets)
1. **A new image every 1-2 s.** This can be a new location, a new framing (≥ 25 % reframe), an insert or a light change. Ricks' jar has ~12 distinct locations or looks in 65 s: throne room, palace-hall wide, city gate, hill at sunset, hill at night, barred window, night street, dawn ruins, inside-the-jar cutaway, dragon extreme close-up, sunrise.
2. **An insert for every concrete noun or number.** The camera cuts to the thing when the word is spoken.
   - Movers: the shop sign, flip phone, call screen, van, socks, a checklist reading "WHO WILL COME LOOKING FOR YOU", a phone left on the table, a "NO ID NEEDED" sign, a "PRIVACY LAW" padlock, a redacted bank statement, a payphone.
   - Ricks' job video: wall clock, inbox on a phone, a "FRI" calendar page, a family photo frame, a red "FIRE EMPLOYEE" button.
   - Text on props is 1-4 big words and is part of the joke.
3. **Subjects fill the frame.** In most shots a face or the key prop takes 40-70 % of the frame height. Wides are 1-2 s establishers only.
   - Our firefighters video spent long stretches on wide street shots with small figures and no clear focus.
   - Our coin video opened on a lone coin with no character.
4. **The light tells the story's arc.** Time of day or mood moves forward with every act; it never stays one look.
   - Jar: day → sunset → night → dawn.
   - Railroad: the grade gets hotter and more orange as "summer" rises.
   - Job: the office turns night-blue as the hero is isolated.
   - Both of our videos stayed in one flat daylight look from start to end.
5. **The reveal gets its own visual world.**
   - Jar: a cutaway inside the jar showing the mechanism.
   - Paradox: a purple stylised "logic" space.
   - Seed: a purple dream zoom for "he had boiled every seed".
   - Movers: a black-and-white flashback for the twist.
   The explanation is never shown in the same set as the story.
6. **Visual escalation tracks the script's ladder.** Each rung is bigger *on screen* too:
   - more things: thousands of flowers filling the hall, then all eight balls dropping;
   - closer framing;
   - stronger colour or heat;
   - bigger roll and kicks toward the climax;
   - literal visual gags at peaks: the boss's face literally turns purple.
7. **The first frame is the hook.** The odd object and the character are in a tight shot and already moving at frame 0: the red fire button, the dragon jar beside the inventor, the engineer on the tracks with a train coming. There is never an establishing wide, a title or a lone object first.
8. **Energy holds to the last frame.**
   - The hits end on a hit: an explosion, the rubble, or a cut to the reveal.
   - Paradox's last frame matches its first (hourglass and scroll), so the loop is seamless.
   - Our firefighters video calmed down for the last 10 s (MAD fell from ~25 to ~10, with slow wide shots) and drifted out.

## Speed is not pace (added 2026-11-04)
The hits keep the eye busy with cuts, inserts and character actions while the camera itself moves gently. Our Jang
short reached the same change rate by swinging the camera hard (scripts/cam_speed.py: p90 32.6 px/f, 9 % of frames
≥ 40 px/f), and the user found it too fast. Get the ≤ 1.5 s events from cuts, inserts and acting. Keep the camera
inside the motion.md limits, which the governor in `templates/beats/camera.ts` enforces.

## Rules for our shot plan (`story.ts`)
- **Visual event every ≤ 1.5 s.** An event is a cut, an insert, a ≥ 25 % reframe, a character action or expression change, an effect sprite, or a light change.
  - List the events against `words.json` in `SHOTS.md` (time, word, event).
  - A gap over 1.5 s is a bug.
  - Holds still creep per motion.md, but a push-in alone is not an event.
- **Never freeze.** No stretch over 0.5 s where nothing on screen changes.
- **Insert list.** Mark every concrete noun and number in the script.
  - Give at least half of them an insert shot or prop card that appears 0-3 f before the word.
  - Prop text is 1-4 words, big, unlit material (see the Gotchas in SKILL.md).
- **Framing.** At least 70 % of screen time has a face or the key prop at ≥ 40 % of frame height. Wides last ≤ 2 s.
- **Light arc.** At least 3 light or mood states, one per act, that progress with the story: day → golden → night, calm → heat, warm → cold.
  - The reversal gets the most extreme look.
  - Use `lights.ts` presets and add night or flashback presets as needed.
- **Reveal world.** The last-10-s reveal plays in a different visual space from the story: a cutaway, a diagram world, a colour-shifted dream, or a B&W flashback.
- **Escalate on screen with the ladder.**
  - Each rung adds one of: more props or extras on screen, a tighter lens, a hotter or darker grade, a bigger roll or kick.
  - Plot a 1-5 "intensity" number per rung in `SHOTS.md`. It must not go down before the reversal.
- **Frame 0 is the hook image.** It's a tight shot of the hero and the odd thing, already in motion. No establisher before the hook line ends.
- **The last word lands on a hit.** An impact kick, a flash, a cut to the reveal image, or a match to frame 0 for a loop. No slow wide fade-out.

## Measuring our cut
Run the same sampler on our render: open the mp4 in a browser, or run the equivalent in Python with OpenCV on the final file. Targets:
- median MAD/s ≥ 15;
- longest quiet ≤ 0.9 s;
- ≥ 1 visual event per 1.5 s;
- MAD in the last 10 s no lower than the median.
