# Use the python:3.9-slim-buster base image
FROM python:3.9-slim-buster

# Set the working directory
WORKDIR /code

# Update and install dependencies
RUN apt update && \
    apt install -y apt-transport-https gnupg wget aptitude poppler-utils libvips-tools && \
    echo 'deb [trusted=yes] https://notesalexp.org/tesseract-ocr5/buster/ buster main' >> /etc/apt/sources.list && \
    apt update -oAcquire::AllowInsecureRepositories=true && \
    apt install -y notesalexp-keyring -oAcquire::AllowInsecureRepositories=true && \
    wget -O - https://notesalexp.org/debian/alexp_key.asc | apt-key add - && \
    apt update && \
    aptitude install -y tesseract-ocr tzdata rsync imagemagick && \
    rm /etc/ImageMagick-6/policy.xml && \
    ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone && \
    apt clean && rm -rf /var/lib/apt/lists/*

# Install ffmpeg
RUN apt update && apt install -y ffmpeg

# Copy the policy file (if needed)
COPY policy.xml /etc/ImageMagick-6/policy.xml

# Copy the requirements file and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Set default command (optional)
CMD ["bash"]
