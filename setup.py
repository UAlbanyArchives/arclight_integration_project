# /usr/bin/env python3
import setuptools

requirements = [
    "PyYAML==6.0.2",
    "pypdf==3.14.0",
    "requests==2.32.3",
    "pycryptodome==3.15.0",
    "iiif-prezi3==1.2.1",
    "PyMuPDF==1.24.11",
    "openai-whisper==20240930",
    "mutagen==1.47.0",
    "ffmpeg-python==0.2.0",
    "pyvips==2.2.3",
    "pandas==2.2.3",
    "pytest",
]

setuptools.setup(
    name="iiiflow",
    version="0.1.1",
    author="Gregory Wiedeman",
    author_email="gwiedeman@albany.edu",
    description="An IIIF pipeline tool using the Digital Object Discovery Storage Specification.",
    long_description_content_type="text/markdown",
    url="https://github.com/UAlbanyArchives/arclight_integration_project",
    packages=setuptools.find_packages(exclude=("tests")),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=requirements,
    python_requires=">=3.8",
)
