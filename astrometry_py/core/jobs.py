# jobs.py
import asyncio
from .client import AstrometryAPIClient
from ..exceptions import AstrometryError
# from .notifier import send_slack_notification
from .logging import Notifier, Logger
from ..storage import hash_cache

class JobManager:
    """Submits jobs asynchronously to astrometry.net and monitors them
    """
    def __init__(self, client: AstrometryAPIClient):
        """Initializes a JobManager object

        :param client: the client that manages requests to the API
        :type client: AstrometryAPIClient
        """
        self.client = client
        self._killed = False
        self.notifier = Notifier(Notifier.SLACK | Notifier.DISCORD)
        self.logger = Logger(name="astrometry_py")

    @hash_cache
    async def process_job(self, image_path: str) -> int:
        """Submits a job a monitors it till completion

        :param image_path: Path to the image to submit
        :type image_path: str
        :raises AstrometryError: 
        :return: Job ID
        :rtype: int
        """
        submit_resp = await self.client.submit_job(image_path)
        subid = submit_resp.get("subid")
        # print(subid)
        if not subid:
            raise AstrometryError("Failed to submit job.")

        while not self._killed:
            status = await self.client.check_submission_status(subid)

            # once Astrometry returns at least one calibration,
            # we know your image is solved
            if len(status.get("job_calibrations")) > 0:
                # send_slack_notification(
                #     f"Submission {subid} completed!",
                #     webhook_url="YOUR_WEBHOOK"
                # )
                self.logger.info(f"Submission {subid} completed!")
                self.notifier.info(f"Submission {subid} completed!")

                # todo: figure out which job id is the "real" one (is it in job calibrations or jobs, is it first or last?)
                jobid = status.get("jobs")[0]
                job_results = await self.client.get_job_info(jobid)

                # send_slack_notification(
                #     f"Job {jobid} in submission {subid} detected the following:\n\t{job_results.get("machine_tags")}",
                #     webhook_url="YOUR_WEBHOOK"
                # )
                
                return jobid
            await asyncio.sleep(2)

        raise AstrometryError(f"Job {subid} was killed.")

    def kill(self) -> None:
        """Kills the job
        """
        self._killed = True
