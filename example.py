import asyncio
from astrometry_py import AstrometryAPIClient, JobManager
from astropy.io import fits
import numpy as np
import matplotlib.pyplot as plt
from io import BytesIO

async def main():
    client = AstrometryAPIClient("mmetbwhnrbmtyvgb")
    try:
        # login and create job manager
        await client.login()
        mgr = JobManager(client)

        # process a job with file "m104.jpg"
        jobid = await mgr.process_job("m104.jpg")

        # get the solved fits and write to disk
        resp = await client.retrieve_result(jobid, "new_fits_file")
        with open("new_fits_file.fits", "wb") as f:
            f.write(resp)

        data = fits.getdata(BytesIO(resp))

        img_rgb = np.moveaxis(data, 0, -1)  # now (568, 960, 3)
        plt.figure(figsize=(8, 6))
        plt.imshow(img_rgb, origin='lower')
        plt.axis('off')
        plt.title("RGB Composite from astrometry.net")
        plt.show()
        
    finally:
        await client.close()                   # always runs

if __name__ == "__main__":
    asyncio.run(main())