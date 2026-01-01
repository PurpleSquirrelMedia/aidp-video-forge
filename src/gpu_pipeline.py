"""
GPU Pipeline - CUDA-accelerated FFmpeg video processing
Builds FFmpeg command chains optimized for NVIDIA GPUs
"""

import asyncio
import json
import os
import subprocess
from pathlib import Path
from typing import Any, Optional


class GPUPipeline:
    """
    GPU-accelerated video processing pipeline using FFmpeg with NVIDIA NVENC/CUDA

    Supports:
    - Hardware encoding (h264_nvenc, hevc_nvenc)
    - CUDA-accelerated filters (scale_cuda, yadif_cuda, etc.)
    - GPU-based color processing
    """

    # CUDA filter equivalents for common operations
    CUDA_FILTERS = {
        "scale": "scale_cuda",
        "yadif": "yadif_cuda",  # Deinterlacing
        "overlay": "overlay_cuda",
        "transpose": "transpose_npp",
        "chromakey": "chromakey_cuda",
    }

    # NVENC presets (quality/speed tradeoff)
    NVENC_PRESETS = {
        "fastest": "p1",
        "fast": "p2",
        "medium": "p4",
        "slow": "p5",
        "quality": "p6",
        "best": "p7",
    }

    def __init__(self, ffmpeg_path: str = "ffmpeg"):
        self.ffmpeg_path = ffmpeg_path
        self._check_gpu_support()

    def _check_gpu_support(self):
        """Check if NVIDIA GPU encoding is available"""
        try:
            result = subprocess.run(
                [self.ffmpeg_path, "-hide_banner", "-encoders"],
                capture_output=True,
                text=True
            )
            self.has_nvenc = "h264_nvenc" in result.stdout
            self.has_cuda = "scale_cuda" in subprocess.run(
                [self.ffmpeg_path, "-hide_banner", "-filters"],
                capture_output=True,
                text=True
            ).stdout
        except Exception:
            self.has_nvenc = False
            self.has_cuda = False

    def build_gpu_command(
        self,
        input_path: str,
        output_path: str,
        preset: dict,
        lut_path: Optional[str] = None
    ) -> list[str]:
        """
        Build FFmpeg command with GPU acceleration

        Args:
            input_path: Input video file
            output_path: Output video file
            preset: Processing preset configuration
            lut_path: Optional LUT file for color grading

        Returns:
            List of FFmpeg command arguments
        """
        cmd = [self.ffmpeg_path, "-hide_banner", "-y"]

        # GPU hardware acceleration for decoding
        if preset.get("hwaccel", True) and self.has_nvenc:
            cmd.extend([
                "-hwaccel", "cuda",
                "-hwaccel_output_format", "cuda"
            ])

        cmd.extend(["-i", input_path])

        # Build filter chain
        filters = self._build_filter_chain(preset, lut_path)
        if filters:
            cmd.extend(["-vf", filters])

        # Video encoding
        encoder = preset.get("encoder", "h264_nvenc" if self.has_nvenc else "libx264")
        cmd.extend(["-c:v", encoder])

        if "nvenc" in encoder:
            # NVENC-specific options
            nvenc_preset = self.NVENC_PRESETS.get(
                preset.get("speed", "medium"), "p4"
            )
            cmd.extend([
                "-preset", nvenc_preset,
                "-rc", preset.get("rate_control", "vbr"),
                "-cq", str(preset.get("cq", 23)),
                "-b:v", preset.get("bitrate", "0"),
                "-maxrate", preset.get("maxrate", "50M"),
                "-bufsize", preset.get("bufsize", "100M"),
            ])

            # GPU-specific tuning
            if preset.get("tune"):
                cmd.extend(["-tune", preset["tune"]])

            # B-frames for better compression
            cmd.extend(["-bf", str(preset.get("bframes", 3))])

        else:
            # CPU fallback (libx264/libx265)
            cmd.extend([
                "-preset", preset.get("cpu_preset", "medium"),
                "-crf", str(preset.get("crf", 23)),
            ])

        # Audio encoding
        audio_codec = preset.get("audio_codec", "aac")
        if audio_codec == "copy":
            cmd.extend(["-c:a", "copy"])
        else:
            cmd.extend([
                "-c:a", audio_codec,
                "-b:a", preset.get("audio_bitrate", "128k"),
                "-ar", str(preset.get("audio_sample_rate", 48000)),
            ])

        # Output options
        if preset.get("faststart", True):
            cmd.extend(["-movflags", "+faststart"])

        cmd.append(output_path)

        return cmd

    def _build_filter_chain(
        self,
        preset: dict,
        lut_path: Optional[str] = None
    ) -> str:
        """Build FFmpeg filter chain with CUDA acceleration where possible"""
        filters = []
        use_cuda = self.has_cuda and preset.get("use_cuda", True)

        # Hardware upload if not already on GPU
        if use_cuda and not preset.get("hwaccel", True):
            filters.append("hwupload_cuda")

        # Scaling
        if "scale" in preset:
            w, h = preset["scale"]
            if use_cuda:
                filters.append(f"scale_cuda={w}:{h}")
            else:
                filters.append(f"scale={w}:{h}")

        # Deinterlacing
        if preset.get("deinterlace"):
            if use_cuda:
                filters.append("yadif_cuda=0:-1:0")
            else:
                filters.append("yadif=0:-1:0")

        # HDR to SDR tone mapping
        if preset.get("tonemap"):
            if use_cuda:
                filters.append("tonemap_cuda=tonemap=hable:peak=100")
            else:
                filters.append("zscale=t=linear:npl=100,tonemap=hable,zscale=t=bt709")

        # Frame rate conversion
        if "fps" in preset:
            filters.append(f"fps={preset['fps']}")

        # Download from GPU for CPU-based filters
        needs_cpu_filters = lut_path or preset.get("eq") or preset.get("unsharp")
        if use_cuda and needs_cpu_filters:
            filters.append("hwdownload,format=nv12")

        # Color grading with LUT
        if lut_path:
            # LUT application (CPU-based, but fast)
            filters.append(f"lut3d='{lut_path}'")

        # Color correction (eq filter)
        if preset.get("eq"):
            eq = preset["eq"]
            eq_str = ",".join(f"{k}={v}" for k, v in eq.items())
            filters.append(f"eq={eq_str}")

        # Sharpening
        if preset.get("unsharp"):
            filters.append(f"unsharp={preset['unsharp']}")

        # Film grain (for cinematic look)
        if preset.get("grain"):
            grain = preset["grain"]
            filters.append(f"noise=c0s={grain}:c0f=t+u")

        # Letterbox
        if preset.get("letterbox"):
            aspect = preset["letterbox"]
            filters.append(f"pad=iw:iw/{aspect}:(ow-iw)/2:(oh-ih)/2:black")

        # Vignette
        if preset.get("vignette"):
            filters.append(f"vignette=angle={preset['vignette']}")

        return ",".join(filters) if filters else ""

    async def process_local(
        self,
        input_path: str,
        output_path: str,
        preset: dict,
        lut_path: Optional[str] = None
    ) -> dict:
        """
        Process video locally (for testing without AIDP)

        Returns:
            dict with processing results and metrics
        """
        import time

        cmd = self.build_gpu_command(input_path, output_path, preset, lut_path)

        print(f"FFmpeg command: {' '.join(cmd)}")

        start_time = time.time()

        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        stdout, stderr = await process.communicate()

        elapsed = time.time() - start_time

        if process.returncode != 0:
            return {
                "success": False,
                "error": stderr.decode(),
                "command": " ".join(cmd)
            }

        # Get input duration for speedup calculation
        probe_cmd = [
            "ffprobe", "-v", "quiet",
            "-print_format", "json",
            "-show_format",
            input_path
        ]
        probe_result = subprocess.run(probe_cmd, capture_output=True, text=True)
        probe_data = json.loads(probe_result.stdout) if probe_result.stdout else {}
        duration = float(probe_data.get("format", {}).get("duration", elapsed))

        return {
            "success": True,
            "output_path": output_path,
            "metrics": {
                "processing_time_seconds": elapsed,
                "input_duration_seconds": duration,
                "speedup": round(duration / elapsed, 2) if elapsed > 0 else 0,
                "encoder": preset.get("encoder", "h264_nvenc"),
                "used_cuda": self.has_cuda and preset.get("use_cuda", True)
            }
        }

    def get_gpu_info(self) -> dict:
        """Get information about available GPU"""
        try:
            result = subprocess.run(
                ["nvidia-smi", "--query-gpu=name,memory.total,driver_version",
                 "--format=csv,noheader"],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                parts = result.stdout.strip().split(", ")
                return {
                    "name": parts[0] if len(parts) > 0 else "Unknown",
                    "memory": parts[1] if len(parts) > 1 else "Unknown",
                    "driver": parts[2] if len(parts) > 2 else "Unknown",
                    "nvenc_available": self.has_nvenc,
                    "cuda_filters_available": self.has_cuda
                }
        except Exception:
            pass

        return {
            "name": "No NVIDIA GPU detected",
            "nvenc_available": False,
            "cuda_filters_available": False
        }


# Export for easy importing
__all__ = ["GPUPipeline"]
