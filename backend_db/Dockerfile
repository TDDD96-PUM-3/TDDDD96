FROM python:3.12-slim

# Install Chromium browser + matching driver. Debian's chromium
# package ships native binaries for both amd64 and arm64, so the
# same Dockerfile works on Intel/Linux/CI and on Apple Silicon
# without conditional FROMs or platform emulation.
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        chromium \
        chromium-driver && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV FLASK_ENV=development
# Tell Selenium where the system's Chromium and chromedriver live.
ENV CHROME_BIN=/usr/bin/chromium
ENV CHROMEDRIVER_PATH=/usr/bin/chromedriver

CMD ["flask", "--app", "app:create_app", "run", "--debug", \
    "--host=0.0.0.0", "--port=8000"]
