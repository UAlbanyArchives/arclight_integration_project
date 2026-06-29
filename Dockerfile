FROM python:3.11-slim-bookworm

ENV TZ=Etc/UTC

# Set the working directory
WORKDIR /code

# Update and install dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        poppler-utils \
        libvips-tools \
        tesseract-ocr \
        tzdata \
        rsync \
        imagemagick \
        ffmpeg \
        libreoffice \
        xfonts-75dpi \
        xfonts-base \
        wkhtmltopdf && \
    rm -f /etc/ImageMagick-6/policy.xml && \
    ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy the policy file (if needed)
COPY policy.xml /etc/ImageMagick-6/policy.xml

# Copy the requirements file and install Python dependencies
COPY setup.py .
COPY .iiiflow.yml /root

# Install the iiiflow
RUN pip install --no-cache-dir .

# Run  tests
CMD ["pytest", "tests", "-vv"]
