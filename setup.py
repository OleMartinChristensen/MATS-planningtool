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
        "ephem==3.7.6.0",
        "matplotlib>=3.1.1",
        "scipy>=1.2.1",
        "lxml>=4.3.3",
        "astropy>=4.0",
        "h5py>=2.9.0",
        "skyfield>=1.13",
        "Sphinx>=2.3.1",
        "astroquery",
    ],
)

