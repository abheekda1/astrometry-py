import aiohttp
import asyncio
import json
import os
from typing import Any, Dict

class AstrometryAPIClient:
    def __init__(
        self,
        api_key: str,
        base_url: str = "https://nova.astrometry.net/api/"
    ):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/") + "/"
        self.session_id: str = ""
        timeout = aiohttp.ClientTimeout(total=60)
        self._session: aiohttp.ClientSession(timeout=timeout) | None = None

    async def _get_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
        return self._session

    async def login(self) -> dict:
        sess = await self._get_session()
        url  = self.base_url + "login"
        payload = {"request-json": json.dumps({"apikey": self.api_key})}

        async with sess.post(url, data=payload) as resp:
            resp.raise_for_status()
            text = await resp.text()
            data = json.loads(text)

            self.session_id = data["session"]
            return data

    async def submit_job(self, image_path: str) -> Dict[str, Any]:
        """
        Upload an image file as multipart/form-data.
        """
        sess = await self._get_session()
        url = self.base_url + "upload"

        # Build the multipart form
        form = aiohttp.FormData()
        form.add_field(
            "request-json",
            json.dumps({"session": self.session_id}),
            content_type="text/plain"
        )
        form.add_field(
            "file",
            open(image_path, "rb"),
            filename=os.path.basename(image_path),
            content_type="application/octet-stream"
        )

        async with sess.post(url, data=form) as resp:
            resp.raise_for_status()
            text = await resp.text()
            data = json.loads(text)
            return data


    async def check_job_status(self, subid: int) -> Dict[str, Any]:
        """
        Check your submission status.
        """
        sess = await self._get_session()
        url = f"{self.base_url}submissions/{subid}"
        params = {"session": self.session_id}

        async with sess.get(url, params=params) as resp:
            resp.raise_for_status()
            text = await resp.text()
            data = json.loads(text)
            return data

    async def get_job_info(self, jobid: int) -> Dict[str, Any]:
        """
        Fetch the job-level metadata/details.
        """
        sess = await self._get_session()
        url = f"{self.base_url}jobs/{jobid}/info/"
        params = {"session": self.session_id}

        async with sess.get(url, params=params) as resp:
            resp.raise_for_status()
            return await resp.json()

    async def retrieve_result(self, jobid: int, file_type: str) -> bytes:
        """
        Download one of the result files (WCS, annotated image, etc.)
        Returns raw bytes of the file.
        """
        sess = await self._get_session()
        url = f"https://nova.astrometry.net/{file_type}/{jobid}"
        params = {"session": self.session_id}

        async with sess.get(url, params=params) as resp:
            resp.raise_for_status()
            return await resp.read()

    async def close(self) -> None:
        if self._session:
            await self._session.close()
