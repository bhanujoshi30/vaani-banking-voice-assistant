# Use an ARM64-compatible Python base image
FROM python:3.11-slim-bookworm

# Set the working directory
WORKDIR /app

# Install build dependencies required for compiling C extensions
RUN apt-get update && \
        apt-get install -y --no-install-recommends \
        build-essential \
        python3-dev \
        libz-dev && \
        rm -rf /var/lib/apt/lists/*

# Copy application code into the image
COPY . .

# Move the current build context contents into a `backend` package folder so
# the application can be imported as `backend.app` (preserves existing
# package-relative imports).
# Move files into a `backend` package directory under /app (so import `backend` works)
RUN mkdir -p /app/backend && \
        for p in /app/* /app/.*; do \
            bn=$(basename "$p"); \
            if [ "$bn" != "." ] && [ "$bn" != ".." ] && [ "$bn" != "backend" ] && [ "$bn" != "Dockerfile" ] && [ "$bn" != ".dockerignore" ]; then \
                mv "$p" /app/backend/ || true; \
            fi; \
        done

# Keep the working directory at `/app` so Python can import the `backend` package
WORKDIR /app
# Install requirements from the moved `backend` folder
RUN pip install --no-cache-dir -r backend/requirements.txt

# Expose the port Dokku expects (5000 is the default)
ENV PORT=5000
EXPOSE 5000

# Run the app as a package module
CMD ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:5000", "backend.app:app"]