# Use the official Playwright Python image with system dependencies pre-installed
FROM mcr.microsoft.com/playwright/python:v1.49.0-jammy

# Set working directory inside the container
WORKDIR /app

# Copy and install python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install the browser binary 
RUN playwright install chromium

# Copy your script over
COPY . .

# Run your script
CMD ["python", "run.py"]
