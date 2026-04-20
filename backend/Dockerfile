# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
# We use /app as the root to mirror the project structure
WORKDIR /app

# Install system dependencies needed for sentence-transformers
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file from the root into the container
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire backend directory into the container
COPY backend/ ./backend/

# Set environment variables
ENV PYTHONPATH=/app
ENV PORT=8000
ENV PYTHONUNBUFFERED=1

# Expose the port the app runs on
EXPOSE 8000

# Start the application using uvicorn
# Points to Phase 9: API and Multi-thread Chat Layer
CMD ["sh", "-c", "uvicorn backend.phase-9-api-multi-thread-chat.src.app:app --host 0.0.0.0 --port ${PORT}"]
