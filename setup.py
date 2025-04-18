from setuptools import setup, find_packages

setup(
    name="astrometry_py",
    version="0.1.0",
    author="Abheek Dhawan",
    description="…short description…",
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
