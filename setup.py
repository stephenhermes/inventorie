from setuptools import setup, find_packages  # type: ignore

import inventorie

DISTNAME = "inventorie"
MAINTAINER = "Stephen Hermes"
SHORT_DESCRIPTION = "A simple inventory management system for DIY electronics."
with open("README.md") as f:
    LONG_DESCRIPTION = f.read()
LICENSE = "MIT"
VERSION = inventorie.__version__
with open("requirements.txt") as f:
    REQUIREMENTS = f.read().splitlines()


setup(
    name=DISTNAME,
    version=VERSION,
    maintainer=MAINTAINER,
    description=SHORT_DESCRIPTION,
    license=LICENSE,
    long_description=LONG_DESCRIPTION,
    python_requires=">=3.7",
    install_requires=REQUIREMENTS,
    packages=find_packages(),
    entry_points={"console_scripts": ["inventorie=inventorie.main:run_script"]},
)
