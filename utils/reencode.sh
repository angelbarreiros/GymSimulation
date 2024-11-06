#!/bin/bash

# Create a directory for the speed-adjusted videos
mkdir -p outputs_adjusted

# Calculate the speed factor: to make 24s become 20s, we multiply by (24/20 = 1.2)
# In FFmpeg's PTS (presentation timestamp), we divide by the speed factor
PTS_FACTOR="1/1.2"

# Loop through all MP4 files in the outputs directory
for video in outputs/*.mp4; do
    # Get just the filename without the path
    filename=$(basename "$video")
    
    # Re-encode with speed adjustment and forced 30 fps
    ffmpeg -i "$video" \
           -filter:v "setpts=$PTS_FACTOR*PTS" \
           -filter:a "atempo=1.2" \
           -r 30 \
           -c:v libx264 \
           -preset medium \
           -crf 23 \
           "outputs_adjusted/$filename"
done