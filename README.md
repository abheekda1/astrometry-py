example.py:  
```py
import asyncio
from astrometry_py import AstrometryAPIClient, JobManager

async def main():
    client = AstrometryAPIClient("mmetbwhnrbmtyvgb")
    try:
        await client.login()
        mgr = JobManager(client)
        subid = await mgr.process_job("m42.jpg")
        print("Plate solved, sub id:", subid)

        resp = await client.retrieve_result(subid, "new_fits_file")
        with open("new_fits_file.fits", "wb") as f:
            f.write(resp)
        
    finally:
        await client.close()

if __name__ == "__main__":
    asyncio.run(main())
```