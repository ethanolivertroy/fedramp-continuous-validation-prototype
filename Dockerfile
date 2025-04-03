FROM python:3.10-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create output directory
RUN mkdir -p /app/reports

# Set environment variable for output directory
ENV OUTPUT_DIR=/app/reports

# Run the validation tool when container starts
ENTRYPOINT ["python", "check_encryption.py"]

# Default command with help information
CMD ["--help"]