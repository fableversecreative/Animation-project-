# FableVerse: render on the laptop (RTX 3050)

Everything Claude builds is saved in GitHub. The laptop only downloads it and renders it on the RTX 3050.

## A. One-time setup (~15 min)

| Step | What | Link | Where it goes |
|---|---|---|---|
| 1 | Install **Node.js 22 LTS** (Windows Installer .msi, default options, tick "Automatically install the necessary tools" if asked) | https://nodejs.org/en/download | Installs itself (C:\Program Files\nodejs) |
| 2 | Install **Git for Windows** (default options) | https://git-scm.com/download/win | Installs itself |
| 3 | Make the work folder | - | `C:\Users\<you>\Documents\FableVerse` |
| 4 | Open **PowerShell** in that folder (in File Explorer: click the address bar, type `powershell`, press Enter) and download the project: | https://github.com/fableversecreative/Animation-project- | `Documents\FableVerse\Animation-project-` |

```
git clone -b claude/greeting-dbsr4p https://github.com/fableversecreative/Animation-project-.git
cd Animation-project-\remotion
npm install
npx remotion browser ensure
```
(Sign in to GitHub in the window that pops up the first time - the repo is private.)

5. **Use the RTX 3050:** Windows Settings -> System -> Display -> Graphics -> "Add desktop app" ->
   browse to `C:\Users\<you>\.remotion\chrome-headless-shell\` (open the sub-folders) -> `chrome-headless-shell.exe`
   -> Options -> **High performance (NVIDIA GeForce RTX 3050)** -> Save.

## B. Every render

Open PowerShell in `Documents\FableVerse\Animation-project-\remotion`, then:

1. Get Claude's latest changes:
```
git pull
```
2. 360p preview (~10-15 min):
```
npx remotion render NapoleonShort out\napoleon_360p.mp4 --scale=0.3333333333333333 --concurrency=2 --gl=angle
```
3. 1080x1920 final (after fixes, ~45-60 min):
```
npx remotion render NapoleonShort out\napoleon_final.mp4 --concurrency=2 --gl=angle --crf=18
```
The finished video is in `Documents\FableVerse\Animation-project-\remotion\out\`.
Voice + music + sound effects are included automatically.

Tips: plug in the charger, close Chrome and games, Windows power mode = Best performance.

## C. Send it back
Upload the MP4 to Google Drive > **Animation** (https://drive.google.com/drive/folders/1PajVoHSBZhhrYbapdetxBZfBh2FYNUxs)
and tell Claude "uploaded".

## D. Let Claude render on the laptop by itself (future)
So Claude can run renders on the 3050 without you typing commands:
1. Update the **Claude desktop app**: https://claude.ai/download (install over the old one), then quit it from the tray (^ next to the clock -> right-click Claude -> Quit) and open it again.
2. Claude app -> **Settings -> Claude Code -> Remote Control** -> turn it on -> **Add folder** -> choose
   `Documents\FableVerse` (a normal folder, not inside a hidden ".something" folder).
3. Keep the app open and the laptop awake, then tell Claude "check". Claude will send an access request - tap **Allow**.
(Access from cloud chats is still rolling out; if Claude says "not available", step D isn't ready for your account yet and A-C still work.)
