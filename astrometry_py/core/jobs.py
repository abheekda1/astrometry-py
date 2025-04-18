import asyncio
from .client import AstrometryAPIClient
# from .exceptions import AstrometryError
from ..exceptions import AstrometryError
from .notifier import send_slack_notification

class JobManager:
    def __init__(self, client: AstrometryAPIClient, killed=False):
        self.client = client
        self.killed = killed

    async def process_job(self, image_path: str):
        """
        Submits an image for plate solving, monitors the job, and retrieves the result.
        Sends a notification on job completion or failure.
        """
        job_info = await self.client.submit_job(image_path)
        print(job_info.json()["jobs"])
        job_id = job_info.json()["jobs"][0]
        print(job_id)
        if not job_id:
            raise AstrometryError("Failed to submit job.")

        while True:
            if self.killed:
                raise AstrometryError(f"Job {job_id} killed.")
                
            status = await self.client.check_job_status(job_id)
            # if status.get("status") == "success":
            print(status)
            if status["status"] == "success":
                result = await self.client.retrieve_result(job_id)
                # todo: add an option to pick which notification gets sent and add url as some param
                send_slack_notification(f"Job {job_id} completed successfully.", webhook_url="YOUR_SLACK_WEBHOOK")
                return result
            elif status.get("status") == "failure":
                send_slack_notification(f"Job {job_id} failed.", webhook_url="YOUR_SLACK_WEBHOOK")
                raise AstrometryError(f"Job {job_id} failed.")
            # fixme: should there be an else block here?
            await asyncio.sleep(5)  # Poll every 5 seconds

    async def kill(self):
        self.killed = True