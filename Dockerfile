FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    iputils-ping \
    procps \
    net-tools \
    openssh-client \
    curl \
    && curl -L https://github.com/aguacero7/rkik/releases/download/v1.2.1/rkik-linux-x86_64 -o /usr/local/bin/rkik \
    && chmod +x /usr/local/bin/rkik \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
