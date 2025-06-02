# Use official Python image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy and install dependencies
COPY coach/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the coach service code
COPY coach/ .

# Expose the port the coach service will use
EXPOSE 5002

# Start the Flask app
CMD ["python", "main.py"]
