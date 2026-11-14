#!/bin/bash
# renders both versions (0-6 s), muxes them and builds a labelled side-by-side
cd "$(dirname "$0")"
s=$(date +%s)
for M in paint blender; do
  BG=$M python3 comp5.py frames fr_$M 0-89 > log_$M.0 2>&1 &
  BG=$M python3 comp5.py frames fr_$M 90-179 > log_$M.1 2>&1 &
done
wait
echo "composite frames took $(( $(date +%s) - s )) s"
for M in paint blender; do
  ffmpeg -v error -y -r 30 -i fr_$M/f%05d.jpg -i audio6.wav -c:v libx264 -crf 18 -pix_fmt yuv420p -c:a aac -b:a 192k -shortest cmp_$M.mp4
done
ffmpeg -v error -y -i cmp_paint.mp4 -i cmp_blender.mp4 -filter_complex \
 "[0:v]drawbox=x=0:y=0:w=iw:h=54:color=black@0.55:t=fill,drawtext=fontfile=/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf:text='A  WITHOUT BLENDER':x=(w-tw)/2:y=12:fontsize=26:fontcolor=white[a];[1:v]drawbox=x=0:y=0:w=iw:h=54:color=black@0.55:t=fill,drawtext=fontfile=/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf:text='B  WITH BLENDER':x=(w-tw)/2:y=12:fontsize=26:fontcolor=0xffd640[b];[a][b]hstack=inputs=2[v]" \
 -map "[v]" -map 0:a -c:v libx264 -crf 18 -pix_fmt yuv420p -c:a aac -b:a 192k cmp_side_by_side.mp4
echo done
