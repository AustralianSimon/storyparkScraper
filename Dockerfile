FROM python:3.12.7-slim-bullseye
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
RUN apt-get update && apt-get upgrade -y #&& apt-get install -y libpq-dev build-essential

# Create non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser

RUN pip install --upgrade pip
WORKDIR /app



# Add these debug lines
RUN pwd && ls -la

COPY --chown=appuser:appuser entrypoint.sh /entrypoint.sh
COPY --chown=appuser:appuser /app /app

RUN pwd && ls -la && echo "Files in /:"
RUN chmod +x /entrypoint.sh
RUN bash -c 'if [ -f "entrypoint.sh" ]; then echo "entrypoint.sh exists"; else echo "entrypoint.sh not found"; fi'

EXPOSE 8000
CMD ["/bin/bash", "/entrypoint.sh"]