# Dockerfile
FROM python:3.12-alpine

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Install dependencies
RUN apk add --no-cache streamlink && \
    pip install --no-cache-dir flask


# Set work directory
WORKDIR /app

# Copy application code
COPY streamlink_server.py /app/streamlink_server.py

# Expose the application port
EXPOSE 6090

# Run the application
CMD ["python", "streamlink_server.py"]