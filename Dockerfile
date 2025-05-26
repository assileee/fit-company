# Use official Python image
FROM python:3.11-slim

# Set working directory in the container
WORKDIR /app

# Copy only requirements first to leverage Docker caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the app
COPY . .

# Expose port Flask runs on
EXPOSE 5000

# Set environment variables
ENV FLASK_APP=src/fit/app.py
ENV FLASK_RUN_HOST=0.0.0.0

# Start the Flask app
CMD ["flask", "run"]