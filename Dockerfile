FROM python:3.11-slim

# Install system deps + Caddy
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    && curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/deb/debian.deb.txt' | tee /etc/apt/sources.list.d/caddy-stable.list \
    && apt-get update \
    && apt-get install -y caddy \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Python deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# App code + data
COPY . .

EXPOSE 8080

# Simple start script (runs all three in background)
COPY start.sh /start.sh
RUN chmod +x /start.sh

CMD ["/start.sh"]
