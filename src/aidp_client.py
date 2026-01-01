"""
AIDP Client - Interface to AIDP Decentralized GPU Network
Handles authentication, job submission, and result retrieval
"""

import asyncio
import hashlib
import os
import time
from typing import Any, Callable, Optional
import json

# AIDP Configuration
AIDP_API_URL = os.getenv("AIDP_API_URL", "https://api.aidp.store")
AIDP_API_KEY = os.getenv("AIDP_API_KEY", "")
AIDP_WALLET = os.getenv("AIDP_WALLET", "")


class AIDPClient:
    """Client for interacting with AIDP decentralized GPU network"""

    def __init__(
        self,
        api_url: str = AIDP_API_URL,
        api_key: str = AIDP_API_KEY,
        wallet: str = AIDP_WALLET
    ):
        self.api_url = api_url
        self.api_key = api_key
        self.wallet = wallet
        self._session = None

    async def _get_session(self):
        """Get or create aiohttp session"""
        if self._session is None:
            import aiohttp
            self._session = aiohttp.ClientSession(
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "X-AIDP-Wallet": self.wallet,
                    "Content-Type": "application/json"
                }
            )
        return self._session

    async def close(self):
        """Close the session"""
        if self._session:
            await self._session.close()
            self._session = None

    async def upload_file(self, file_path: str) -> dict:
        """
        Upload a file to AIDP decentralized storage

        Returns:
            dict with file_id and storage_url
        """
        session = await self._get_session()

        # Calculate file hash for integrity
        file_hash = await self._hash_file(file_path)
        file_size = os.path.getsize(file_path)
        file_name = os.path.basename(file_path)

        # Request upload URL
        async with session.post(
            f"{self.api_url}/v1/storage/upload",
            json={
                "filename": file_name,
                "size": file_size,
                "hash": file_hash,
                "type": "video"
            }
        ) as resp:
            if resp.status != 200:
                raise AIDPError(f"Upload request failed: {await resp.text()}")
            upload_info = await resp.json()

        # Upload to presigned URL
        with open(file_path, "rb") as f:
            async with session.put(
                upload_info["upload_url"],
                data=f,
                headers={"Content-Type": "video/mp4"}
            ) as resp:
                if resp.status not in (200, 201):
                    raise AIDPError(f"File upload failed: {resp.status}")

        return {
            "file_id": upload_info["file_id"],
            "storage_url": upload_info["storage_url"],
            "hash": file_hash
        }

    async def submit_job(
        self,
        input_file_id: str,
        preset: dict,
        lut_path: Optional[str] = None,
        gpu_node: Optional[str] = None,
        priority: str = "normal"
    ) -> dict:
        """
        Submit a GPU processing job to AIDP network

        Args:
            input_file_id: ID of uploaded input file
            preset: Processing preset configuration
            lut_path: Optional path to LUT file
            gpu_node: Optional specific GPU node to use
            priority: Job priority (low, normal, high)

        Returns:
            dict with job_id and node_id
        """
        session = await self._get_session()

        # Upload LUT if provided
        lut_file_id = None
        if lut_path:
            lut_upload = await self.upload_file(lut_path)
            lut_file_id = lut_upload["file_id"]

        # Build job configuration
        job_config = {
            "type": "video_processing",
            "input_file_id": input_file_id,
            "preset": preset,
            "lut_file_id": lut_file_id,
            "priority": priority,
            "gpu_requirements": {
                "min_vram_gb": preset.get("min_vram_gb", 8),
                "preferred_gpu": preset.get("preferred_gpu", "any"),
                "cuda_compute": preset.get("cuda_compute", "7.0")
            }
        }

        if gpu_node:
            job_config["target_node"] = gpu_node

        # Submit job
        async with session.post(
            f"{self.api_url}/v1/jobs/submit",
            json=job_config
        ) as resp:
            if resp.status != 200:
                raise AIDPError(f"Job submission failed: {await resp.text()}")
            result = await resp.json()

        return {
            "job_id": result["job_id"],
            "node_id": result["assigned_node"],
            "estimated_time": result.get("estimated_time_seconds"),
            "cost_estimate": result.get("cost_estimate_usd")
        }

    async def get_job_status(self, job_id: str) -> dict:
        """Get current status of a job"""
        session = await self._get_session()

        async with session.get(f"{self.api_url}/v1/jobs/{job_id}") as resp:
            if resp.status != 200:
                raise AIDPError(f"Status check failed: {await resp.text()}")
            return await resp.json()

    async def wait_for_job(
        self,
        job_id: str,
        timeout: int = 3600,
        poll_interval: int = 2,
        progress_callback: Optional[Callable] = None
    ) -> dict:
        """
        Wait for a job to complete

        Args:
            job_id: Job ID to wait for
            timeout: Maximum wait time in seconds
            poll_interval: Seconds between status checks
            progress_callback: Optional callback for progress updates

        Returns:
            Final job status with output_file_id
        """
        start_time = time.time()

        while True:
            status = await self.get_job_status(job_id)

            if progress_callback:
                progress_callback(status)

            if status["status"] == "completed":
                return status

            if status["status"] == "failed":
                raise AIDPError(f"Job failed: {status.get('error', 'Unknown error')}")

            if time.time() - start_time > timeout:
                raise AIDPError(f"Job timed out after {timeout} seconds")

            await asyncio.sleep(poll_interval)

    async def download_file(self, file_id: str, output_path: str) -> str:
        """Download a file from AIDP storage"""
        session = await self._get_session()

        # Get download URL
        async with session.get(
            f"{self.api_url}/v1/storage/download/{file_id}"
        ) as resp:
            if resp.status != 200:
                raise AIDPError(f"Download request failed: {await resp.text()}")
            download_info = await resp.json()

        # Download file
        async with session.get(download_info["download_url"]) as resp:
            if resp.status != 200:
                raise AIDPError(f"File download failed: {resp.status}")

            with open(output_path, "wb") as f:
                async for chunk in resp.content.iter_chunked(8192):
                    f.write(chunk)

        return output_path

    async def list_gpu_nodes(self, available_only: bool = True) -> list:
        """List available GPU nodes on AIDP network"""
        session = await self._get_session()

        params = {"available_only": str(available_only).lower()}

        async with session.get(
            f"{self.api_url}/v1/nodes",
            params=params
        ) as resp:
            if resp.status != 200:
                raise AIDPError(f"Node list failed: {await resp.text()}")
            return await resp.json()

    async def get_pricing(self, gpu_type: str = "any") -> dict:
        """Get current pricing for GPU compute"""
        session = await self._get_session()

        async with session.get(
            f"{self.api_url}/v1/pricing",
            params={"gpu_type": gpu_type}
        ) as resp:
            if resp.status != 200:
                raise AIDPError(f"Pricing request failed: {await resp.text()}")
            return await resp.json()

    @staticmethod
    async def _hash_file(file_path: str, chunk_size: int = 65536) -> str:
        """Calculate SHA256 hash of file"""
        sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            while chunk := f.read(chunk_size):
                sha256.update(chunk)
        return sha256.hexdigest()


class AIDPError(Exception):
    """AIDP-specific error"""
    pass


# Convenience functions for direct usage
async def process_video_on_aidp(
    input_path: str,
    output_path: str,
    preset: dict,
    lut_path: Optional[str] = None
) -> dict:
    """
    High-level function to process a video on AIDP

    Example:
        result = await process_video_on_aidp(
            input_path="video.mp4",
            output_path="processed.mp4",
            preset={"encoder": "h264_nvenc", "crf": 23}
        )
    """
    client = AIDPClient()

    try:
        # Upload
        upload_result = await client.upload_file(input_path)

        # Submit job
        job = await client.submit_job(
            input_file_id=upload_result["file_id"],
            preset=preset,
            lut_path=lut_path
        )

        # Wait for completion
        result = await client.wait_for_job(job["job_id"])

        # Download result
        await client.download_file(result["output_file_id"], output_path)

        return {
            "success": True,
            "output_path": output_path,
            "job_id": job["job_id"],
            "metrics": result.get("metrics", {})
        }

    finally:
        await client.close()
