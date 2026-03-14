# Use Python 3.9 as base image (matches your local version)
FROM python:3.9-slim

# Set the working directory inside the container
WORKDIR /app

# Copy requirements first (Docker caches this layer if requirements don't change)
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy all project files into the container
COPY . .

# Tell Docker which port the app uses
EXPOSE 8000

# Command to run the app when container starts
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]