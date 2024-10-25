from pathlib import Path
from setuptools import setup, find_packages

reqs = Path("requirements.txt").read_text().splitlines()

with open("README.md", encoding="utf-8") as fo:
    long_description = fo.read()

setup(
    name="my_api",
    version="0.1.0",
    url="https://github.com/purarue/HPI_API",
    author="purarue",
    description=("""An automatic JSON API for HPI"""),
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="MIT",
    packages=find_packages(include=["my_api"]),
    install_requires=reqs,
    keywords="data server",
    entry_points={"console_scripts": ["hpi_api = my_api.__main__:main"]},
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
)
