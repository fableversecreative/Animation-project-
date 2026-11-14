# Render "Napoleon vs Bunnies" on the laptop (RTX 3050)

## One-time setup (~10 min)
1. Install **Node.js 22 LTS** from https://nodejs.org (default options). Restart the PC once.
2. Install **Git** from https://git-scm.com (default options), or download this repo as a ZIP from GitHub
   (green "Code" button -> Download ZIP, branch `claude/greeting-dbsr4p`) and unzip it.
3. Open **PowerShell** in the `remotion` folder (Shift + right-click inside the folder -> "Open PowerShell window here").
4. Run once:
   ```
   npm install
   npx remotion browser ensure
   ```
5. Windows Settings -> System -> Display -> Graphics: add
   `%USERPROFILE%\.remotion\chrome-headless-shell\...\chrome-headless-shell.exe` (search the folder) and set it to **High performance** (RTX 3050).

## Render the 360p preview (~15-20 min)
```
npx remotion render NapoleonShort out/napoleon_360p.mp4 --scale=0.3333333333333333 --concurrency=2 --gl=angle
```
## Render the 1080x1920 final (after fixes, ~1 h)
```
npx remotion render NapoleonShort out/napoleon_final.mp4 --concurrency=2 --gl=angle --crf=18
```
The voice + music + SFX (`public/napoleon/mix.wav`) are included automatically.
Close Chrome / other apps and keep the charger plugged in while rendering.

## Upload
Put the MP4 in Google Drive > Animation and tell Claude "uploaded".
