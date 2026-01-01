#!/bin/bash
# GPU-accelerated video encoding using NVENC
# Usage: ./gpu-encode.sh input.mp4 output.mp4 [preset]

set -e

INPUT="$1"
OUTPUT="$2"
PRESET="${3:-medium}"

if [ -z "$INPUT" ] || [ -z "$OUTPUT" ]; then
    echo "Usage: $0 input.mp4 output.mp4 [preset]"
    echo "Presets: fastest, fast, medium, slow, quality, best"
    exit 1
fi

# Map presets to NVENC presets
case $PRESET in
    fastest) NVENC_PRESET="p1" ;;
    fast)    NVENC_PRESET="p2" ;;
    medium)  NVENC_PRESET="p4" ;;
    slow)    NVENC_PRESET="p5" ;;
    quality) NVENC_PRESET="p6" ;;
    best)    NVENC_PRESET="p7" ;;
    *)       NVENC_PRESET="p4" ;;
esac

echo "==================================="
echo "AIDP Video Forge - GPU Encode"
echo "==================================="
echo "Input:  $INPUT"
echo "Output: $OUTPUT"
echo "Preset: $PRESET (NVENC: $NVENC_PRESET)"
echo "==================================="

# Check for NVIDIA GPU
if ! command -v nvidia-smi &> /dev/null; then
    echo "Warning: nvidia-smi not found, GPU may not be available"
fi

# Run FFmpeg with GPU acceleration
ffmpeg -hide_banner -y \
    -hwaccel cuda \
    -hwaccel_output_format cuda \
    -i "$INPUT" \
    -c:v h264_nvenc \
    -preset "$NVENC_PRESET" \
    -rc vbr \
    -cq 23 \
    -b:v 0 \
    -maxrate 50M \
    -bufsize 100M \
    -c:a aac \
    -b:a 128k \
    -movflags +faststart \
    "$OUTPUT"

echo ""
echo "==================================="
echo "Encoding complete!"
echo "Output: $OUTPUT"
echo "==================================="
