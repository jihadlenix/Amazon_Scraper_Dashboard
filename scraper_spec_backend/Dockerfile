FROM python:3.12-slim

# System deps for Selenium
RUN apt-get update && apt-get install -y --no-install-recommends \
    chromium chromium-driver fonts-liberation \
 && rm -rf /var/lib/apt/lists/*

# Env for Selenium + Python
ENV CHROME_BIN=/usr/bin/chromium \
    CHROMEDRIVER_PATH=/usr/bin/chromedriver \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Python deps (paths are relative to scraper_spec_backend/)
COPY requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# App code
COPY app ./app

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
