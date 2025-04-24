import aiohttp
import asyncio
import json
import os
from typing import Any, Dict
import logging
from .logging import Logger, Notifier

class AstrometryAPIClient:
    """
    Astrometry.net API client with integrated logging and notifications.

    :param api_key:           Your Astrometry API key
    :param base_url:          Base URL for the API
    :param notifier_channels: Optional Notifier bit-flags (e.g. Notifier.SLACK|Notifier.DISCORD)
    :param notifier_level:    Logging level at or above which notifications fire
    """
    def __init__(
        self,
        api_key: str,
        base_url: str = "https://nova.astrometry.net/api/",
        notifier_channels: int | None = None,
        notifier_level: int = logging.ERROR
    ):
        # Initialize logger (and notifier if channels provided)
        self.logger = Logger(
            name="astrometry_client",
            level=logging.INFO,
            notifier_channels=notifier_channels,
            notifier_level=notifier_level
        )
        self.notifier = self.logger.notifier

        self.api_key = api_key
        self.base_url = base_url.rstrip("/") + "/"
        self.session_id: str = ""
        timeout = aiohttp.ClientTimeout(total=60)
        self._session: aiohttp.ClientSession | None = None

    async def _get_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            self.logger.debug("Creating new aiohttp session")
            self._session = aiohttp.ClientSession()
        return self._session

    async def login(self) -> Dict[str, Any]:
        url = self.base_url + "login"
        payload = {"request-json": json.dumps({"apikey": self.api_key})}
        try:
            self.logger.debug("Logging in via %s", url)
            sess = await self._get_session()
            async with sess.post(url, data=payload) as resp:
                resp.raise_for_status()
                text = await resp.text()
                data = json.loads(text)
                self.session_id = data.get("session", "")
                self.logger.info("Logged in, session_id=%s", self.session_id)
                return data
        except Exception as e:
            self.logger.error("Login failed: %s", e)
            if self.notifier:
                self.notifier.error(f"Login failed: {e}")
            raise

    async def submit_job(self, image_path: str) -> Dict[str, Any]:
        url = self.base_url + "upload"
        self.logger.info("Submitting job for image %s", image_path)
        try:
            sess = await self._get_session()
            form = aiohttp.FormData()
            form.add_field("request-json", json.dumps({"session": self.session_id}), content_type="text/plain")
            form.add_field(
                "file", open(image_path, "rb"),
                filename=os.path.basename(image_path),
                content_type="application/octet-stream"
            )
            async with sess.post(url, data=form) as resp:
                resp.raise_for_status()
                text = await resp.text()
                data = json.loads(text)
                self.logger.info("Submit response: %s", data)
                return data
        except Exception as e:
            self.logger.error("Failed to submit job: %s", e)
            if self.notifier:
                self.notifier.error(f"Submit job failed: {e}")
            raise

    async def check_submission_status(self, subid: int) -> Dict[str, Any]:
        url = f"{self.base_url}submissions/{subid}"
        params = {"session": self.session_id}
        self.logger.debug("Checking status for submission %d", subid)
        try:
            sess = await self._get_session()
            async with sess.get(url, params=params) as resp:
                resp.raise_for_status()
                text = await resp.text()
                data = json.loads(text)
                self.logger.debug("Status response: %s", data)
                return data
        except Exception as e:
            self.logger.error("Status check failed for %d: %s", subid, e)
            if self.notifier:
                self.notifier.error(f"Status check failed for {subid}: {e}")
            raise

    async def get_job_info(self, jobid: int) -> Dict[str, Any]:
        url = f"{self.base_url}jobs/{jobid}/info/"
        params = {"session": self.session_id}
        self.logger.debug("Fetching job info for job %d", jobid)
        try:
            sess = await self._get_session()
            async with sess.get(url, params=params) as resp:
                resp.raise_for_status()
                text = await resp.text()
                data = json.loads(text)
                self.logger.info("Job info retrieved for %d", jobid)
                return data
        except Exception as e:
            self.logger.error("Failed to get job info %d: %s", jobid, e)
            if self.notifier:
                self.notifier.error(f"Get job info failed for {jobid}: {e}")
            raise

    async def retrieve_result(self, jobid: int, file_type: str) -> bytes:
        url = f"https://nova.astrometry.net/{file_type}/{jobid}"
        params = {"session": self.session_id}
        self.logger.debug("Retrieving result %s for job %d", file_type, jobid)
        try:
            sess = await self._get_session()
            async with sess.get(url, params=params) as resp:
                resp.raise_for_status()
                data = await resp.read()
                self.logger.info("Result %s retrieved for job %d", file_type, jobid)
                return data
        except Exception as e:
            self.logger.error("Result retrieval failed %s for %d: %s", file_type, jobid, e)
            if self.notifier:
                self.notifier.error(f"Retrieve result {file_type} failed for {jobid}: {e}")
            raise

    async def close(self) -> None:
        self.logger.debug("Closing HTTP session")
        if self._session:
            await self._session.close()
            self.logger.info("Session closed")
