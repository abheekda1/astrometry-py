# jobs.py
import asyncio
from .client import AstrometryAPIClient
from ..exceptions import AstrometryError
from .notifier import send_slack_notification

class JobManager:
    def __init__(self, client: AstrometryAPIClient):
        self.client = client
        self._killed = False

    async def process_job(self, image_path: str) -> int:
        # 1) Submit
        submit_resp = await self.client.submit_job(image_path)
        subid = submit_resp.get("subid")
        print(subid)
        if not subid:
            raise AstrometryError("Failed to submit job.")

        # 2) Poll until solved
        while not self._killed:
            status = await self.client.check_job_status(subid)
            # once Astrometry returns at least one calibration,
            # we know your image is solved
            if len(status.get("job_calibrations")) > 0:
                send_slack_notification(
                    f"Submission {subid} completed!",
                    webhook_url="YOUR_WEBHOOK"
                )
                return subid
            await asyncio.sleep(5)

        raise AstrometryError(f"Job {subid} was killed.")

    def kill(self) -> None:
        self._killed = True
