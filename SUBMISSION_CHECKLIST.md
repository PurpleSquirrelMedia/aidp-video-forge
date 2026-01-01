# AIDP Hackathon Submission Checklist

## Project: AIDP Video Forge
**Category**: Best Performing Project for Compute Usage

---

## Required Submissions

### 1. AIDP Marketplace Project Page
- [ ] Create account on https://aidp.store
- [ ] Navigate to marketplace submission
- [ ] Fill in project details:
  - **Name**: AIDP Video Forge
  - **Description**: GPU-accelerated video processing on decentralized compute
  - **Category**: Video Processing / AI
  - **GPU Usage**: NVENC encoding, CUDA filters, HDR tone mapping

### 2. Public GitHub Repository
- [x] Repository created: https://github.com/PurpleSquirrelMedia/aidp-video-forge
- [x] Code is public
- [x] README with clear documentation
- [x] GPU integration documentation
- [x] Working code examples

### 3. Social Media Link (Twitter/X)
- [ ] Post announcement using template from `docs/SOCIAL_POST.md`
- [ ] Include:
  - Project name and description
  - @aidpstore mention
  - GitHub link
  - Demo video link (if available)
  - Relevant hashtags (#AIDP #GPU #DePIN)

### 4. Demo Video (1-2 minutes)
- [ ] Record using script from `docs/SOCIAL_POST.md`
- [ ] Show:
  - GPU encoding in action
  - Speed comparison (CPU vs GPU)
  - Before/after color grading
  - Cost savings
- [ ] Upload to YouTube/Loom/etc.
- [ ] Include link in marketplace submission

### 5. GPU Usage Explanation
- [x] Documented in `docs/GPU_INTEGRATION.md`
- [x] Covers:
  - NVENC hardware encoding
  - CUDA filter acceleration
  - HDR tone mapping
  - Performance benchmarks
  - Cost comparison

---

## Judging Criteria Alignment

| Criteria | How We Address It |
|----------|-------------------|
| Technical execution | Production-ready FFmpeg GPU pipeline |
| GPU integration depth | NVENC + CUDA filters + HDR processing |
| Product quality | 12 professional presets, LUT support |
| Creativity & originality | Decentralized video processing platform |
| User experience & design | Simple CLI + planned web dashboard |
| Vision & scalability | Distributed batch processing |
| Social proof | Open source, Twitter announcement |
| Depth of AIDP compute usage | Full GPU pipeline on AIDP nodes |
| Value added to ecosystem | Enables video creators to use AIDP |

---

## Quick Links

- **GitHub**: https://github.com/PurpleSquirrelMedia/aidp-video-forge
- **AIDP**: https://aidp.store
- **Demo Script**: `./scripts/demo-processing.sh`

---

## Submission Commands

```bash
# Test locally before submission
cd ~/Projects/aidp-video-forge
./scripts/demo-processing.sh

# Run with AIDP (after getting API key)
export AIDP_API_KEY="your-key"
export AIDP_WALLET="your-wallet"
python src/forge.py process --input video.mp4 --preset cinematic
```

---

## After Submission

- [ ] Monitor for questions/feedback
- [ ] Engage with AIDP community on Telegram
- [ ] Share progress updates on Twitter
- [ ] Prepare for demo day (if applicable)
