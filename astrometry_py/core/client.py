import aiohttp
import asyncio

import requests
import json

class AstrometryAPIClient:
    # todo: need to actually use base_url
    def __init__(self, api_key: str, base_url: str = "https://nova.astrometry.net/api/"):
        self.api_key = api_key
        self.base_url = base_url
        self.session = None

    async def login(self):
        R = requests.post('http://nova.astrometry.net/api/login', data={'request-json': json.dumps({"apikey": self.api_key}), 'session': self.session })
        print(R.json())
        # fixme: check if it has session first (i.e. check status)
        self.session = R.json()['session']
        return R

    async def submit_job(self, image_path: str) -> dict:
        """
        Submits a plate-solving job to astrometry.net.
        Returns a dictionary with job details including a job_id.
        """
        # must be submitted as multipart/form-data
        # todo: handle errors/exceptions/etc.
        # + logging
        # todo: diff file name? based on image_path?
        R = requests.post("http://nova.astrometry.net/api/upload", files={'file': ('img.fits', open(image_path, 'rb'))}, data={'session': self.session})
        print(R)
        return R


    async def check_job_status(self, job_id: int) -> dict:
        """
        Checks the status of a submitted job.
        Returns a dictionary indicating job status.
        """
        # TODO: Implement job status polling
        # todo: check if job id is valid (maybe backend does this)
        R = requests.get(f"http://nova.astrometry.net/api/submissions/{job_id}", data={'session': self.session})
        print(R)
        return R

    async def get_result(self, job_id: int) -> dict:
        """
        Gets the results of a job with things like
        tagged objects and objects in field
        """
        R = requests.get(f"http://nova.astrometry.net/api/jobs/{job_id}/info/", data={'session': self.session})
        print(R)
        return R

    async def retrieve_result(self, job_id: int, file_type: str) -> dict:
        """
        Retrieves the result of a completed job.
        Returns a dictionary containing the astrometric solution.
        """
        # TODO: Implement result retrieval logic
        """
        URLs:
        http://nova.astrometry.net/wcs_file/JOBID
        http://nova.astrometry.net/new_fits_file/JOBID
        http://nova.astrometry.net/rdls_file/JOBID
        http://nova.astrometry.net/axy_file/JOBID
        http://nova.astrometry.net/corr_file/JOBID
        http://nova.astrometry.net/annotated_display/JOBID
        http://nova.astrometry.net/red_green_image_display/JOBID
        http://nova.astrometry.net/extraction_image_display/JOBID
        """
        # todo: check to make sure file_type is valid
        R = requests.get(f"http://nova.astrometry.net/{file_type}/{job_id}", data={'session': self.session})
        print(R)
        return R
