from distutils.core import setup

from setuptools import setup

setup(
    name="Operational_Planning_Tool",
    version="1.0",
    description="Mission planning tool for the MATS satellite",
    author="David Skånberg & Ole Martin Christensen",
    author_email="ole.martin.christensen@gmail.com",
    url="https://github.com/OleMartinChristensen/MATS-planningtool/",
    packages=["OPT"],
    install_requires=[
        "ephem",
        "matplotlib",
        "scipy",
        "lxml",
        "astropy",
        "h5py",
        "skyfield",
        "Sphinx",
        "astroquery",
    ],
)

