# AIDP Video Forge

GPU-Accelerated Video Processing on AIDP Decentralized Compute Network

## Overview

Video Forge transforms video processing workflows by leveraging AIDP's decentralized GPU network for:
- **10-20x faster encoding** with NVENC (H.264/HEVC GPU acceleration)
- **Real-time color grading** with CUDA-accelerated LUT application
- **HDR processing** with GPU tone mapping
- **Distributed batch processing** across multiple GPU nodes

## GPU Usage on AIDP

This project demonstrates deep GPU integration with AIDP:

| Operation | CPU Method | GPU Method (AIDP) | Speedup |
|-----------|------------|-------------------|---------|
| H.264 Encoding | libx264 | h264_nvenc | 15-20x |
| HEVC Encoding | libx265 | hevc_nvenc | 20-30x |
| Scaling | scale | scale_cuda | 5-8x |
| Deinterlacing | yadif | yadif_cuda | 8-10x |
| HDR Tone Map | zscale+tonemap | tonemap_cuda | 15x |
| LUT Application | lut3d | CUDA texture | 10x |

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   Video Forge                           │
├─────────────────────────────────────────────────────────┤
│  Client (Web UI / CLI)                                  │
│  └── Upload video → Select processing → Download result │
├─────────────────────────────────────────────────────────┤
│  Job Orchestrator                                       │
│  └── Queue jobs → Assign to AIDP nodes → Aggregate     │
├─────────────────────────────────────────────────────────┤
│  AIDP GPU Workers                                       │
│  └── FFmpeg + NVENC + CUDA filters                     │
└─────────────────────────────────────────────────────────┘
```

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Configure AIDP credentials
export AIDP_API_KEY="your-api-key"
export AIDP_WALLET="your-solana-wallet"

# Process a video on AIDP GPU
python src/forge.py process --input video.mp4 --preset cinematic --output processed.mp4

# Batch process folder
python src/forge.py batch --input ./videos --lut Cinematic_Teal_Orange.cube
```

## Features

### Processing Presets
- **Cinematic**: Teal-orange grade + film grain + letterbox
- **Broadcast**: Rec709 safe + loudness normalization
- **Social**: Vertical crop + captions + thumbnail generation
- **HDR**: SDR to HDR10 conversion with GPU tone mapping

### Supported Formats
- Input: MP4, MOV, MKV, AVI, ProRes, DNxHD
- Output: H.264, HEVC, ProRes (GPU-accelerated)

## Project Structure

```
aidp-video-forge/
├── src/
│   ├── forge.py          # Main CLI entry point
│   ├── aidp_client.py    # AIDP GPU integration
│   ├── gpu_pipeline.py   # CUDA-accelerated FFmpeg
│   ├── job_queue.py      # Job orchestration
│   └── presets.py        # Processing presets
├── scripts/
│   ├── gpu-encode.sh     # NVENC encoding script
│   └── gpu-effects.sh    # CUDA effects pipeline
├── docker/
│   └── Dockerfile.gpu    # NVIDIA Docker image
├── tests/
│   └── test_pipeline.py  # Unit tests
└── docs/
    └── GPU_INTEGRATION.md
```

## AIDP Integration

### How We Use AIDP GPUs

1. **Job Submission**: Videos are uploaded and queued for processing
2. **Node Selection**: AIDP routes jobs to available GPU nodes (A100, A10G, RTX 4090)
3. **GPU Processing**: FFmpeg with NVENC/CUDA executes on AIDP infrastructure
4. **Verification**: AIDP's proof system verifies computation integrity
5. **Delivery**: Processed videos returned via decentralized storage

### Cost Efficiency

AIDP's decentralized model provides:
- 40-60% cost reduction vs. centralized cloud GPU
- No cold start delays (always-available GPU pool)
- Pay-per-second billing

## Demo Video

[Watch the 2-minute demo](./docs/demo.mp4) showing:
1. Upload and preset selection
2. Real-time GPU utilization on AIDP node
3. Before/after comparison
4. Processing speed benchmark

## Links

- [AIDP Marketplace Listing](https://aidp.store/marketplace/video-forge)
- [Twitter/X](https://x.com/purplesquirrelnetworks)
- [Live Demo](https://video-forge.aidp.store)

## License

MIT License - Built for AIDP GPU Build & Recruit Campaign
