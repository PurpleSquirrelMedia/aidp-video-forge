"""
Video Processing Presets for AIDP Video Forge
Each preset defines GPU-optimized encoding and filter settings
"""

PRESETS = {
    "default": {
        "description": "Standard web-optimized output with GPU encoding",
        "encoder": "h264_nvenc",
        "speed": "medium",
        "cq": 23,
        "rate_control": "vbr",
        "audio_codec": "aac",
        "audio_bitrate": "128k",
        "faststart": True,
        "min_vram_gb": 4,
    },

    "cinematic": {
        "description": "Film-like output with teal-orange grade, grain, and letterbox",
        "encoder": "h264_nvenc",
        "speed": "quality",
        "cq": 20,
        "rate_control": "vbr",
        "bframes": 4,
        "eq": {
            "brightness": 0.02,
            "contrast": 1.1,
            "saturation": 1.15,
        },
        "grain": 8,  # Subtle film grain
        "letterbox": 2.39,  # Cinema aspect ratio
        "unsharp": "5:5:0.5:5:5:0.5",
        "audio_codec": "aac",
        "audio_bitrate": "192k",
        "faststart": True,
        "min_vram_gb": 6,
        "preferred_lut": "Cinematic_Teal_Orange.cube",
    },

    "broadcast": {
        "description": "Broadcast-safe output for TV/streaming platforms",
        "encoder": "h264_nvenc",
        "speed": "quality",
        "cq": 18,
        "rate_control": "cbr",
        "bitrate": "15M",
        "maxrate": "20M",
        "bufsize": "30M",
        "scale": (1920, 1080),
        "fps": 29.97,
        "audio_codec": "aac",
        "audio_bitrate": "256k",
        "audio_sample_rate": 48000,
        "faststart": True,
        "min_vram_gb": 6,
        "preferred_lut": "Broadcast_Safe.cube",
    },

    "social_vertical": {
        "description": "Vertical 9:16 output optimized for TikTok/Reels/Shorts",
        "encoder": "h264_nvenc",
        "speed": "fast",
        "cq": 22,
        "rate_control": "vbr",
        "scale": (1080, 1920),
        "fps": 30,
        "eq": {
            "brightness": 0.03,
            "contrast": 1.08,
            "saturation": 1.2,
        },
        "unsharp": "3:3:0.8",
        "audio_codec": "aac",
        "audio_bitrate": "128k",
        "faststart": True,
        "min_vram_gb": 4,
    },

    "hdr_to_sdr": {
        "description": "Convert HDR content to SDR with GPU tone mapping",
        "encoder": "h264_nvenc",
        "speed": "medium",
        "cq": 20,
        "rate_control": "vbr",
        "hwaccel": True,
        "tonemap": True,  # Enable CUDA tone mapping
        "audio_codec": "copy",
        "faststart": True,
        "min_vram_gb": 8,
        "cuda_compute": "7.5",  # Requires newer GPU for tone mapping
    },

    "hevc_master": {
        "description": "High-quality HEVC output for archival/master",
        "encoder": "hevc_nvenc",
        "speed": "quality",
        "cq": 18,
        "rate_control": "vbr",
        "bframes": 4,
        "audio_codec": "aac",
        "audio_bitrate": "320k",
        "audio_sample_rate": 48000,
        "faststart": True,
        "min_vram_gb": 8,
    },

    "fast_preview": {
        "description": "Fast preview encode for quick review",
        "encoder": "h264_nvenc",
        "speed": "fastest",
        "cq": 28,
        "rate_control": "vbr",
        "scale": (1280, 720),
        "fps": 30,
        "audio_codec": "aac",
        "audio_bitrate": "96k",
        "faststart": True,
        "min_vram_gb": 2,
    },

    "youtube": {
        "description": "YouTube recommended settings with GPU encoding",
        "encoder": "h264_nvenc",
        "speed": "medium",
        "cq": 18,
        "rate_control": "vbr",
        "bitrate": "0",
        "maxrate": "40M",
        "bufsize": "80M",
        "bframes": 2,
        "scale": (3840, 2160),  # 4K
        "fps": 60,
        "audio_codec": "aac",
        "audio_bitrate": "384k",
        "audio_sample_rate": 48000,
        "faststart": True,
        "min_vram_gb": 8,
    },

    "netflix": {
        "description": "Netflix delivery specification",
        "encoder": "hevc_nvenc",
        "speed": "quality",
        "cq": 16,
        "rate_control": "vbr",
        "bitrate": "0",
        "maxrate": "25M",
        "bufsize": "50M",
        "bframes": 4,
        "scale": (3840, 2160),
        "fps": 23.976,
        "audio_codec": "aac",
        "audio_bitrate": "448k",
        "audio_sample_rate": 48000,
        "faststart": True,
        "min_vram_gb": 10,
    },

    "vintage_film": {
        "description": "Vintage film look with faded colors and heavy grain",
        "encoder": "h264_nvenc",
        "speed": "quality",
        "cq": 20,
        "rate_control": "vbr",
        "eq": {
            "brightness": -0.02,
            "contrast": 0.95,
            "saturation": 0.7,
            "gamma": 1.1,
        },
        "grain": 25,  # Heavy grain
        "vignette": 0.4,
        "letterbox": 1.66,  # Old film aspect
        "audio_codec": "aac",
        "audio_bitrate": "128k",
        "faststart": True,
        "min_vram_gb": 6,
        "preferred_lut": "Vintage_Fade.cube",
    },

    "documentary": {
        "description": "Clean, natural look for documentary content",
        "encoder": "h264_nvenc",
        "speed": "quality",
        "cq": 19,
        "rate_control": "vbr",
        "eq": {
            "brightness": 0.01,
            "contrast": 1.02,
            "saturation": 0.95,
        },
        "unsharp": "3:3:0.3",
        "audio_codec": "aac",
        "audio_bitrate": "192k",
        "faststart": True,
        "min_vram_gb": 6,
        "preferred_lut": "Documentary_Natural.cube",
    },

    "action": {
        "description": "High contrast, punchy colors for action content",
        "encoder": "h264_nvenc",
        "speed": "medium",
        "cq": 19,
        "rate_control": "vbr",
        "bframes": 2,
        "eq": {
            "brightness": 0.0,
            "contrast": 1.25,
            "saturation": 1.3,
        },
        "unsharp": "5:5:1.0:5:5:0.5",
        "audio_codec": "aac",
        "audio_bitrate": "256k",
        "faststart": True,
        "min_vram_gb": 6,
        "preferred_lut": "Blockbuster_Action.cube",
    },
}


def get_preset(name: str) -> dict:
    """Get a preset by name, with fallback to default"""
    return PRESETS.get(name, PRESETS["default"])


def list_presets() -> list[str]:
    """List all available preset names"""
    return list(PRESETS.keys())


def get_preset_description(name: str) -> str:
    """Get the description of a preset"""
    preset = PRESETS.get(name, {})
    return preset.get("description", "No description available")
