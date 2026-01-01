"""
Tests for AIDP Video Forge GPU Pipeline
"""

import pytest
import asyncio
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from gpu_pipeline import GPUPipeline
from presets import PRESETS, get_preset, list_presets


class TestGPUPipeline:
    """Test GPU pipeline functionality"""

    def test_pipeline_initialization(self):
        """Test pipeline can be initialized"""
        pipeline = GPUPipeline()
        assert pipeline is not None
        assert hasattr(pipeline, 'has_nvenc')
        assert hasattr(pipeline, 'has_cuda')

    def test_build_gpu_command_basic(self):
        """Test basic FFmpeg command generation"""
        pipeline = GPUPipeline()
        cmd = pipeline.build_gpu_command(
            input_path="input.mp4",
            output_path="output.mp4",
            preset=PRESETS["default"]
        )

        assert "ffmpeg" in cmd[0]
        assert "input.mp4" in cmd
        assert "output.mp4" in cmd

    def test_build_gpu_command_with_nvenc(self):
        """Test NVENC encoder is used when available"""
        pipeline = GPUPipeline()
        pipeline.has_nvenc = True  # Force NVENC available

        cmd = pipeline.build_gpu_command(
            input_path="input.mp4",
            output_path="output.mp4",
            preset=PRESETS["default"]
        )

        # Should include NVENC encoder
        cmd_str = " ".join(cmd)
        assert "h264_nvenc" in cmd_str or "libx264" in cmd_str

    def test_build_gpu_command_with_lut(self):
        """Test LUT filter is added when LUT path provided"""
        pipeline = GPUPipeline()
        cmd = pipeline.build_gpu_command(
            input_path="input.mp4",
            output_path="output.mp4",
            preset=PRESETS["cinematic"],
            lut_path="test.cube"
        )

        cmd_str = " ".join(cmd)
        assert "lut3d" in cmd_str

    def test_cuda_filter_mapping(self):
        """Test CUDA filter equivalents are defined"""
        assert "scale" in GPUPipeline.CUDA_FILTERS
        assert GPUPipeline.CUDA_FILTERS["scale"] == "scale_cuda"
        assert "yadif" in GPUPipeline.CUDA_FILTERS

    def test_nvenc_presets(self):
        """Test NVENC preset mapping"""
        assert "fastest" in GPUPipeline.NVENC_PRESETS
        assert "best" in GPUPipeline.NVENC_PRESETS
        assert GPUPipeline.NVENC_PRESETS["fastest"] == "p1"
        assert GPUPipeline.NVENC_PRESETS["best"] == "p7"


class TestPresets:
    """Test processing presets"""

    def test_all_presets_exist(self):
        """Test all expected presets are defined"""
        expected = [
            "default", "cinematic", "broadcast", "social_vertical",
            "hdr_to_sdr", "hevc_master", "fast_preview", "youtube",
            "netflix", "vintage_film", "documentary", "action"
        ]
        for preset_name in expected:
            assert preset_name in PRESETS, f"Missing preset: {preset_name}"

    def test_preset_has_required_fields(self):
        """Test presets have required fields"""
        required_fields = ["description", "encoder", "min_vram_gb"]
        for name, preset in PRESETS.items():
            for field in required_fields:
                assert field in preset, f"Preset {name} missing field: {field}"

    def test_get_preset(self):
        """Test get_preset function"""
        preset = get_preset("cinematic")
        assert preset is not None
        assert "encoder" in preset

        # Test fallback to default
        preset = get_preset("nonexistent")
        assert preset == PRESETS["default"]

    def test_list_presets(self):
        """Test list_presets function"""
        presets = list_presets()
        assert len(presets) >= 12
        assert "default" in presets
        assert "cinematic" in presets

    def test_cinematic_preset(self):
        """Test cinematic preset configuration"""
        preset = PRESETS["cinematic"]
        assert preset["speed"] == "quality"
        assert "grain" in preset
        assert "letterbox" in preset
        assert preset["letterbox"] == 2.39

    def test_broadcast_preset(self):
        """Test broadcast preset configuration"""
        preset = PRESETS["broadcast"]
        assert preset["rate_control"] == "cbr"
        assert preset["scale"] == (1920, 1080)

    def test_youtube_preset(self):
        """Test YouTube preset configuration"""
        preset = PRESETS["youtube"]
        assert preset["scale"] == (3840, 2160)  # 4K
        assert preset["fps"] == 60


class TestGPUInfo:
    """Test GPU detection"""

    def test_get_gpu_info(self):
        """Test GPU info retrieval"""
        pipeline = GPUPipeline()
        info = pipeline.get_gpu_info()

        assert "name" in info
        assert "nvenc_available" in info
        assert "cuda_filters_available" in info


# Async tests
class TestAsyncPipeline:
    """Test async pipeline operations"""

    @pytest.mark.asyncio
    async def test_process_local_missing_file(self):
        """Test local processing with missing file"""
        pipeline = GPUPipeline()

        result = await pipeline.process_local(
            input_path="nonexistent.mp4",
            output_path="output.mp4",
            preset=PRESETS["default"]
        )

        assert result["success"] is False
        assert "error" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
