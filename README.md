# astrometry-py
## How to install
```bash
git clone https://github.com/abheekda1/astrometry-py
cd astrometry-py
pip install .
```

## Example code
example.py:  
```py
import asyncio
from astrometry_py import AstrometryAPIClient, JobManager

async def main():
    client = AstrometryAPIClient("YOUR_API_KEY_HERE")
    try:
        await client.login()
        mgr = JobManager(client)
        subid = await mgr.process_job("file.fits")
        print("Plate solved, sub id:", subid)

        resp = await client.retrieve_result(subid, "new_fits_file")
        with open("new_fits_file.fits", "wb") as f:
            f.write(resp)
        
    finally:
        await client.close()

if __name__ == "__main__":
    asyncio.run(main())
```