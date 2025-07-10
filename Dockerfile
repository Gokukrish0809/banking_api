# Use an official lightweight Python image
FROM python:3.10-slim

# Prevent Python from writing .pyc files and buffering stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# Copy and install dependencies first (leveraging Docker cache)
COPY requirements.txt .
RUN apt-get update && apt-get install -y libpq-dev gcc
RUN pip install --no-cache-dir -r requirements.txt

# Copy your application code
COPY . .

# run pytest and start uvicorn server

COPY startup.sh /startup.sh
RUN chmod +x /startup.sh

CMD["/startup.sh"]
