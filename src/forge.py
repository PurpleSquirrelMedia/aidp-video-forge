#!/usr/bin/env python3
"""
AIDP Video Forge - GPU-Accelerated Video Processing CLI
Main entry point for submitting video processing jobs to AIDP network
"""

import argparse
import asyncio
import json
import sys
from pathlib import Path
from typing import Optional

from aidp_client import AIDPClient
from gpu_pipeline import GPUPipeline
from presets import PRESETS


def parse_args():
    parser = argparse.ArgumentParser(
        description="GPU-accelerated video processing on AIDP network",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Process single video with cinematic preset
  forge process --input video.mp4 --preset cinematic --output result.mp4

  # Batch process folder with custom LUT
  forge batch --input ./videos --lut Teal_Orange.cube --output ./processed

  # Check job status
  forge status --job-id abc123
        """
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Process command
    process_parser = subparsers.add_parser("process", help="Process a single video")
    process_parser.add_argument("--input", "-i", required=True, help="Input video file")
    process_parser.add_argument("--output", "-o", help="Output file path")
    process_parser.add_argument("--preset", "-p", choices=list(PRESETS.keys()),
                                default="default", help="Processing preset")
    process_parser.add_argument("--lut", help="Custom LUT file (.cube)")
    process_parser.add_argument("--gpu-node", help="Specific AIDP GPU node to use")
    process_parser.add_argument("--local", action="store_true",
                                help="Process locally (no AIDP)")

    # Batch command
    batch_parser = subparsers.add_parser("batch", help="Batch process videos")
    batch_parser.add_argument("--input", "-i", required=True, help="Input directory")
    batch_parser.add_argument("--output", "-o", help="Output directory")
    batch_parser.add_argument("--preset", "-p", choices=list(PRESETS.keys()),
                              default="default", help="Processing preset")
    batch_parser.add_argument("--lut", help="Custom LUT file (.cube)")
    batch_parser.add_argument("--parallel", type=int, default=4,
                              help="Number of parallel jobs on AIDP")

    # Status command
    status_parser = subparsers.add_parser("status", help="Check job status")
    status_parser.add_argument("--job-id", "-j", required=True, help="Job ID")

    # List command
    list_parser = subparsers.add_parser("list", help="List available resources")
    list_parser.add_argument("--type", choices=["presets", "luts", "nodes", "jobs"],
                             default="presets", help="What to list")

    return parser.parse_args()


async def process_video(args):
    """Process a single video file"""
    input_path = Path(args.input)

    if not input_path.exists():
        print(f"Error: Input file not found: {input_path}")
        return 1

    output_path = args.output or str(input_path.stem) + "_processed.mp4"
    preset = PRESETS.get(args.preset, PRESETS["default"])

    print(f"AIDP Video Forge")
    print("=" * 50)
    print(f"Input:  {input_path}")
    print(f"Output: {output_path}")
    print(f"Preset: {args.preset}")
    if args.lut:
        print(f"LUT:    {args.lut}")
    print("=" * 50)

    if args.local:
        # Local processing (for testing)
        pipeline = GPUPipeline()
        result = await pipeline.process_local(
            input_path=str(input_path),
            output_path=output_path,
            preset=preset,
            lut_path=args.lut
        )
    else:
        # AIDP processing
        client = AIDPClient()

        print("\n[1/4] Uploading to AIDP network...")
        upload_result = await client.upload_file(str(input_path))

        print("[2/4] Submitting GPU job...")
        job = await client.submit_job(
            input_file_id=upload_result["file_id"],
            preset=preset,
            lut_path=args.lut,
            gpu_node=args.gpu_node
        )

        print(f"[3/4] Processing on AIDP GPU node: {job['node_id']}")
        print(f"      Job ID: {job['job_id']}")

        # Wait for completion
        result = await client.wait_for_job(job["job_id"], progress_callback=print_progress)

        print("[4/4] Downloading result...")
        await client.download_file(result["output_file_id"], output_path)

    print("\n" + "=" * 50)
    print("Processing complete!")
    print(f"Output: {output_path}")

    if "metrics" in result:
        metrics = result["metrics"]
        print(f"\nPerformance Metrics:")
        print(f"  GPU Time:     {metrics.get('gpu_time_ms', 'N/A')}ms")
        print(f"  Speedup:      {metrics.get('speedup', 'N/A')}x vs CPU")
        print(f"  AIDP Node:    {metrics.get('node_id', 'N/A')}")
        print(f"  Cost:         ${metrics.get('cost_usd', 'N/A')}")

    return 0


async def batch_process(args):
    """Batch process multiple videos"""
    input_dir = Path(args.input)

    if not input_dir.is_dir():
        print(f"Error: Input directory not found: {input_dir}")
        return 1

    output_dir = Path(args.output or str(input_dir) + "_processed")
    output_dir.mkdir(parents=True, exist_ok=True)

    # Find video files
    video_extensions = {".mp4", ".mov", ".mkv", ".avi", ".m4v", ".webm"}
    videos = [f for f in input_dir.iterdir()
              if f.suffix.lower() in video_extensions]

    if not videos:
        print(f"No video files found in {input_dir}")
        return 1

    print(f"AIDP Video Forge - Batch Processing")
    print("=" * 50)
    print(f"Input:    {input_dir}")
    print(f"Output:   {output_dir}")
    print(f"Videos:   {len(videos)}")
    print(f"Preset:   {args.preset}")
    print(f"Parallel: {args.parallel} jobs")
    print("=" * 50)

    client = AIDPClient()
    preset = PRESETS.get(args.preset, PRESETS["default"])

    # Submit all jobs
    jobs = []
    for i, video in enumerate(videos):
        print(f"\n[{i+1}/{len(videos)}] Submitting: {video.name}")

        upload_result = await client.upload_file(str(video))
        job = await client.submit_job(
            input_file_id=upload_result["file_id"],
            preset=preset,
            lut_path=args.lut
        )
        jobs.append({
            "job_id": job["job_id"],
            "input": video.name,
            "output": str(output_dir / f"{video.stem}_processed.mp4")
        })

    print(f"\nSubmitted {len(jobs)} jobs to AIDP network")
    print("Waiting for completion...")

    # Wait for all jobs
    completed = 0
    for job in jobs:
        result = await client.wait_for_job(job["job_id"])
        await client.download_file(result["output_file_id"], job["output"])
        completed += 1
        print(f"Completed: {completed}/{len(jobs)} - {job['input']}")

    print("\n" + "=" * 50)
    print(f"Batch processing complete!")
    print(f"Output directory: {output_dir}")

    return 0


async def check_status(args):
    """Check job status"""
    client = AIDPClient()
    status = await client.get_job_status(args.job_id)

    print(f"Job Status: {args.job_id}")
    print("=" * 50)
    print(json.dumps(status, indent=2))

    return 0


def list_resources(args):
    """List available resources"""
    if args.type == "presets":
        print("Available Presets:")
        print("=" * 50)
        for name, preset in PRESETS.items():
            print(f"\n{name}:")
            print(f"  {preset.get('description', 'No description')}")

    elif args.type == "luts":
        lut_dir = Path(__file__).parent.parent.parent / "ColorGrading" / "LUTs"
        if lut_dir.exists():
            print("Available LUTs:")
            print("=" * 50)
            for lut in lut_dir.rglob("*.cube"):
                print(f"  {lut.relative_to(lut_dir)}")
        else:
            print("LUT directory not found")

    elif args.type == "nodes":
        print("AIDP GPU Nodes:")
        print("=" * 50)
        print("  (Connect to AIDP to list available nodes)")

    elif args.type == "jobs":
        print("Recent Jobs:")
        print("=" * 50)
        print("  (Connect to AIDP to list recent jobs)")

    return 0


def print_progress(status):
    """Print progress update"""
    progress = status.get("progress", 0)
    stage = status.get("stage", "processing")
    print(f"      Progress: {progress}% - {stage}", end="\r")


async def main():
    args = parse_args()

    if args.command == "process":
        return await process_video(args)
    elif args.command == "batch":
        return await batch_process(args)
    elif args.command == "status":
        return await check_status(args)
    elif args.command == "list":
        return list_resources(args)
    else:
        print("Use --help for usage information")
        return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
