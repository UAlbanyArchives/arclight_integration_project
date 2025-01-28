# /usr/bin/env python3
import setuptools

# Read dependencies from requirements.txt
with open("requirements.txt", "r") as req_file:
    requirements = req_file.read().splitlines()

setuptools.setup(
    name="iiiflow",
    version="0.1",
    author="Gregory Wiedeman",
    author_email="gwiedeman@albany.edu",
    description="An IIIF pipeline tool using the Digital Object Discovery Storage Specification.",
    long_description_content_type="text/markdown",
    url="https://github.com/UAlbanyArchives/arclight_integration_project",
    packages=setuptools.find_namespace_packages(exclude=("tests")),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=requirements,
    python_requires=">=3.8",
)
