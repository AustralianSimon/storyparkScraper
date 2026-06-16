FROM python:3.12.7-slim-bullseye
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    libglib2.0-0 \
    libnss3 \
    libnspr4 \
    libdbus-1-3 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libexpat1 \
    libxcb1 \
    libxkbcommon0 \
    libatspi2.0-0 \
    libx11-6 \
    libxcomposite1 \
    libxdamage1 \
    libxext6 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libpango-1.0-0 \
    libcairo2 \
    libasound2 \
    fonts-liberation \
    libappindicator3-1 \
    xdg-utils \
    wget \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user with a home directory so Playwright can store browser binaries
RUN groupadd -r appuser && useradd -r -g appuser -m -d /home/appuser appuser

RUN pip install --upgrade pip

WORKDIR /app

COPY --chown=appuser:appuser entrypoint.sh /entrypoint.sh
COPY --chown=appuser:appuser . /app

RUN pip install --no-cache-dir -r /app/requirements.txt

RUN pwd && ls -la

RUN pip install --no-cache-dir -r /app/requirements.txt

RUN pwd && ls -la && echo "Files in /:"
RUN bash -c 'if [ -f "entrypoint.sh" ]; then echo "entrypoint.sh exists"; else echo "entrypoint.sh not found"; fi'

RUN chmod +x /entrypoint.sh

# Install Playwright browsers as appuser so they land in /home/appuser/.cache
USER appuser
RUN python -m playwright install chromium

#EXPOSE 8000
EXPOSE 8000
CMD ["/bin/bash", "/entrypoint.sh"]
