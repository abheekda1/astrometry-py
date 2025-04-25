from setuptools import setup, find_packages

setup(
    name="astrometry_py",
    version="0.0.1",
    author="Abheek Dhawan",
    description="Python API Wrapper for Astrometry.net",
    # packages=find_packages(include=["astrometry_py", "astrometry_py.*"]),
    packages=find_packages(),
    install_requires=[
        # e.g. "requests>=2.0",
    ],
    entry_points={
        # if you want console scripts:
        # 'console_scripts': ['proj-cli = projname.scripts:main'],
    },
)
