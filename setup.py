"""This file is used to install your project as a package.
It is used by pip to install your project."""

from setuptools import setup, find_packages

setup(
    name="GitMetrics-TeamBuilder",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "requests",  # Add other dependencies here
    ],
)
