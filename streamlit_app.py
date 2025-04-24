import json
import streamlit as st
import tempfile
from astropy.io import fits
from astropy.wcs import WCS
from astropy.visualization import ImageNormalize, PercentileInterval, AsinhStretch
import matplotlib.pyplot as plt
from io import BytesIO
import asyncio
import nest_asyncio
from pathlib import Path
import numpy as np

from astrometry_py import AstrometryAPIClient, JobManager

# Patch event loop for Streamlit
nest_asyncio.apply()
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
run = lambda coro: loop.run_until_complete(coro)

st.set_page_config(layout="wide")
st.title("Astrometry.net: DIY Annotation with WCS Axes")

# Sidebar inputs
api_key = st.sidebar.text_input("Astrometry.net API Key", type="password")
uploaded = st.sidebar.file_uploader(
    "Upload an image (FITS, JPEG, PNG…)", 
    type=["fits", "fit", "jpg", "jpeg", "png"]
)
if not api_key or not uploaded:
    st.sidebar.info("🔑 Enter your API key and upload a file to get started.")
    st.stop()

# Determine if original is FITS
orig_name = uploaded.name if hasattr(uploaded, 'name') else ''
is_fits = orig_name.lower().endswith(('.fits', '.fit'))

# Save upload to temp file (for caching)
suffix = Path(orig_name).suffix or '.fits'
with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
    raw_bytes = uploaded.read()
    tmp.write(raw_bytes)
    tmp_path = tmp.name

# Instantiate client and job manager
client = AstrometryAPIClient(api_key=api_key)
jobs = JobManager(client)

# Helper to fetch annotations
def fetch_annotations(jobid: int) -> list:
    async def _inner():
        url = f"{client.base_url}jobs/{jobid}/annotations/"
        sess = await client._get_session()
        async with sess.get(url, params={"session": client.session_id}) as resp:
            resp.raise_for_status()
            text = await resp.text()
            data = json.loads(text)
            return data.get("annotations", [])
    return run(_inner())

# 1) Login
try:
    run(client.login())
except Exception as e:
    st.error(f"🚫 Login failed: {e}")
    st.stop()

# 2) Solve button
if st.sidebar.button("▶️ Solve this image"):
    with st.spinner("Solving… this may take a moment"):
        try:
            jobid = run(jobs.process_job(tmp_path))
        except Exception as e:
            st.error(f"🚫 Solve failed: {e}")
            st.stop()

    st.success(f"✅ Solved! Job ID: {jobid}")

    # 3) Retrieve raw solved FITS with WCS headers
    try:
        raw_solved = run(client.retrieve_result(jobid, "new_fits_file"))
    except Exception as e:
        st.error(f"🚫 Could not fetch solved FITS: {e}")
        st.stop()

    # 4) Fetch annotations
    annotations = fetch_annotations(jobid)

    # 5) Render side-by-side
    col1, col2 = st.columns(2)

    # Original
    col1.header("Original")
    if is_fits:
        try:
            hdul0 = fits.open(BytesIO(raw_bytes), ignore_missing_simple=True)
            data0 = hdul0[0].data.astype(float)
            wcs0 = WCS(hdul0[0].header, naxis=2)
            norm0 = ImageNormalize(data0,
                                   interval=PercentileInterval(99.5),
                                   stretch=AsinhStretch(0.1))
            fig0 = plt.figure(figsize=(5,5))
            ax0 = fig0.add_subplot(1,1,1, projection=wcs0)
            ax0.imshow(data0, norm=norm0, cmap='gray', origin='lower')
            ax0.coords.grid(color='white', ls='dotted')
            ax0.set_xlabel('RA')
            ax0.set_ylabel('Dec')
            col1.pyplot(fig0)
        except Exception:
            col1.write("Could not render FITS; showing uploaded bytes.")
            col1.image(raw_bytes)
    else:
        col1.image(raw_bytes)

    # Annotated with DIY annotations
    col2.header("Annotated with WCS axes & Annotations")
    try:
        hdul1 = fits.open(BytesIO(raw_solved), ignore_missing_simple=True)
        data1 = hdul1[0].data
        # # Handle 3D data (e.g., RGB planes)
        # if data1.ndim == 3 and data1.shape[0] in (3,4):
        #     # convert shape (C,H,W) -> (H,W,C)
        #     rgb = np.moveaxis(data1, 0, -1)
        #     show_data = rgb.astype(float)
        # else:
        #     show_data = data1.astype(float)
        show_data = np.moveaxis(data1, 0, -1)  # now (568, 960, 3)

        wcs1 = WCS(hdul1[0].header, naxis=2)
        norm1 = ImageNormalize(show_data,
                               interval=PercentileInterval(99.5),
                               stretch=AsinhStretch(0.1))
        fig1 = plt.figure(figsize=(5,5))
        ax1 = fig1.add_subplot(1,1,1, projection=wcs1)
        # For RGB, omit cmap
        if show_data.ndim == 3:
            ax1.imshow(show_data, origin='lower')
        else:
            ax1.imshow(show_data, norm=norm1, cmap='gray', origin='lower')
        ax1.coords.grid(color='white', ls='dotted')
        ax1.set_xlabel('RA')
        ax1.set_ylabel('Dec')

        # Draw annotation circles and labels
        for ann in annotations:
            xpix = ann.get('pixelx')
            ypix = ann.get('pixely')
            radius = ann.get('radius')
            names = ann.get('names', [])
            label = names[0] if names else ''
            circ = plt.Circle((xpix, ypix), radius=radius + 8,
                              edgecolor='lime', facecolor='none', lw=1.2,
                              transform=ax1.get_transform('pixel'))
            ax1.add_patch(circ)
            if label:
                ax1.text(xpix+10, ypix+10, label,
                         color='lime', fontsize=7, weight='bold',
                         transform=ax1.get_transform('pixel'))

        col2.pyplot(fig1)
    except Exception as e:
        st.error(f"🚫 Could not render annotated FITS: {e}")
        col2.image(raw_solved)

    # 6) Close session
    try:
        run(client.close())
    except:
        pass