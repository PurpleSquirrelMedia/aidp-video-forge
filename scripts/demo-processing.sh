#!/bin/bash
# Demo script showing Video Forge capabilities
# This script demonstrates GPU vs CPU encoding speed

set -e

echo "╔═══════════════════════════════════════════════════════════╗"
echo "║           AIDP Video Forge - Demo                         ║"
echo "║   GPU-Accelerated Video Processing                        ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo ""

# Check for test video
TEST_VIDEO="${1:-test_input.mp4}"
if [ ! -f "$TEST_VIDEO" ]; then
    echo "Creating test video (10 seconds, 1080p)..."
    ffmpeg -f lavfi -i testsrc=duration=10:size=1920x1080:rate=30 \
           -f lavfi -i sine=frequency=1000:duration=10 \
           -c:v libx264 -preset ultrafast -c:a aac \
           "$TEST_VIDEO" -y 2>/dev/null
fi

echo ""
echo "Test video: $TEST_VIDEO"
echo ""

# CPU Encoding Benchmark
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Benchmark 1: CPU Encoding (libx264)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
CPU_START=$(date +%s.%N)
ffmpeg -hide_banner -loglevel warning -y \
    -i "$TEST_VIDEO" \
    -c:v libx264 -preset medium -crf 23 \
    -c:a aac -b:a 128k \
    output_cpu.mp4
CPU_END=$(date +%s.%N)
CPU_TIME=$(echo "$CPU_END - $CPU_START" | bc)
echo "CPU encoding time: ${CPU_TIME}s"

# GPU Encoding Benchmark
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Benchmark 2: GPU Encoding (h264_nvenc)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
GPU_START=$(date +%s.%N)
ffmpeg -hide_banner -loglevel warning -y \
    -hwaccel cuda -hwaccel_output_format cuda \
    -i "$TEST_VIDEO" \
    -c:v h264_nvenc -preset p4 -cq 23 \
    -c:a aac -b:a 128k \
    output_gpu.mp4 2>/dev/null || {
    echo "GPU encoding failed - NVENC not available"
    GPU_TIME="N/A"
}
if [ -z "$GPU_TIME" ]; then
    GPU_END=$(date +%s.%N)
    GPU_TIME=$(echo "$GPU_END - $GPU_START" | bc)
    echo "GPU encoding time: ${GPU_TIME}s"
fi

# Calculate speedup
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Results"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "CPU (libx264):    ${CPU_TIME}s"
if [ "$GPU_TIME" != "N/A" ]; then
    SPEEDUP=$(echo "scale=2; $CPU_TIME / $GPU_TIME" | bc)
    echo "GPU (h264_nvenc): ${GPU_TIME}s"
    echo ""
    echo "🚀 GPU Speedup: ${SPEEDUP}x faster!"
else
    echo "GPU: Not available (requires NVIDIA GPU with NVENC)"
fi

# Cleanup
rm -f output_cpu.mp4 output_gpu.mp4

echo ""
echo "Demo complete!"
echo "Deploy on AIDP for decentralized GPU compute: https://aidp.store"
