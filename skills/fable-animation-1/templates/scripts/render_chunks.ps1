# Resumable final render (Windows PowerShell). Renders <out>/part_<a>.mp4 for every frame range not finished yet
# (a part counts as finished only once its .done marker exists), then concatenates them into <out>/video.mp4.
# usage: powershell -File scripts/render_chunks.ps1 -Name <video folder> -Comp <CompositionId> [-Concurrency 2] [-Size 500] [-Only <first frame of one part>]
#   Total frames come from src/videos/<Name>/story.ts (TOTAL) via scripts/dump_story.mjs. Output: out/<Name>/final.
#   To redo a part, delete it and its .done file, then run again.
# Keep concurrency low: every Remotion tab holds its own 2K WebGL world (MSAA targets, 4096 shadow map, HD textures).
# On a laptop GPU with ~6 GB of VRAM, 8 default tabs crashed the PC; 2 tabs peaked around 4.5 GB.
param([Parameter(Mandatory=$true)][string]$Name, [Parameter(Mandatory=$true)][string]$Comp,
      [int]$Concurrency = 2, [int]$Size = 500, [int]$Only = -1, [string]$Tmp = "",
      [string]$Scale = "1", [string]$Out = "final", [int]$From = 0, [int]$To = -1)
# fable-animation-1: -Scale 1 = 1080x1920 final; -Scale 0.3333333333333333 -Out preview = 360x640 preview.
# -From/-To render only a frame range (fix clips). Output folder: out/<Name>/<Out>.
$ErrorActionPreference = "Stop"
Set-Location (Split-Path $PSScriptRoot -Parent)
$root = (Get-Location).Path
if ($Tmp) { New-Item -ItemType Directory -Force $Tmp | Out-Null; $env:TEMP = $Tmp; $env:TMP = $Tmp }
$outDir = "out/$Name/$Out"
New-Item -ItemType Directory -Force $outDir | Out-Null
$ErrorActionPreference = "Continue"
$total = [int]((node scripts/dump_story.mjs $Name | ConvertFrom-Json).TOTAL)
$ErrorActionPreference = "Stop"
$end = $total; if ($To -ge 0) { $end = [Math]::Min($To + 1, $total) }
"$Comp : frames $From-$($end - 1) of $total -> $outDir (scale $Scale)"
# Remotion's own headless shell (npx remotion browser ensure). On a laptop with two GPUs, set this exe to
# "High performance" in Windows Settings > System > Display > Graphics, or Chrome renders on the integrated GPU.
$shell = Get-ChildItem "$root/node_modules/.remotion/chrome-headless-shell" -Recurse -Filter "chrome-headless-shell*.exe" -ErrorAction SilentlyContinue | Select-Object -First 1
$browserArgs = @(); if ($shell) { $browserArgs = @("--browser-executable", $shell.FullName) }
$parts = @()
for ($a = $From; $a -lt $end; $a += $Size) {
  $b = [Math]::Min($a + $Size, $end) - 1
  $p = "$outDir/part_{0:d4}.mp4" -f $a
  $parts += $p
  if (Test-Path "$p.done") { "skip $p (done)"; continue }
  if ($Only -ge 0 -and $a -ne $Only) { continue }
  "render frames $a-$b -> $p (concurrency $Concurrency)"
  # stderr lines (404s for the optional Kenney models) are not failures in PS 5.1: judge by the exit code only
  $ErrorActionPreference = "Continue"
  npx remotion render src/index.ts $Comp $p --frames="$a-$b" --concurrency=$Concurrency --codec h264 --crf 16 --scale $Scale --gl angle @browserArgs --log error 2>&1 | Select-String -NotMatch '404|kenney|THREE.Clock|PCFSoft'
  $code = $LASTEXITCODE
  $ErrorActionPreference = "Stop"
  if ($code -ne 0) { throw "render failed for $a-$b (exit $code)" }
  New-Item -ItemType File "$p.done" -Force | Out-Null
}
if ($Only -ge 0) { "rendered only part $Only"; exit 0 }
$list = ($parts | ForEach-Object { "file '" + (Split-Path $_ -Leaf) + "'" }) -join "`n"
[IO.File]::WriteAllText((Join-Path $root "$outDir/parts.txt"), $list, (New-Object Text.UTF8Encoding $false))
ffmpeg -y -loglevel error -f concat -safe 0 -i "$outDir/parts.txt" -c copy "$outDir/video.mp4"
"concatenated $($parts.Count) parts -> $outDir/video.mp4"
