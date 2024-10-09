"""This file is used to install your project as a package.
It is used by pip to install your project."""

from setuptools import setup, find_packages


# Function to read the requirements.txt file
def read_requirements():
    with open("requirements.txt", encoding="utf-8") as req_file:
        return req_file.read().splitlines()


setup(
    name="GitMetrics-TeamBuilder",
    version="0.1.0",
    packages=find_packages(),
    install_requires=read_requirements(),
    entry_points={
        "console_scripts": [
            "team=app.driver:main",
        ],
    },
    author="Jialin Cui",
    author_email="jcui9@ncsu.edu",
    description="A command-line tool for mining user metrics and forming teams.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/JialinC/GitMetrics-TeamBuilder",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
