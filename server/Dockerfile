# Use an existing Python runtime as a parent image
#FROM python:3.9-slim-buster
FROM python:latest

# Set the work directory to /app
WORKDIR /app

# Copy the requirements.txt file into the image
COPY requirements.txt .

# Install the required libraries
RUN pip install --no-cache-dir -r requirements.txt

# Copy the app.py file into the image
COPY main.py .
COPY job.yaml .

# Expose port 5000 for the Flask app
EXPOSE 5000

# Set environment variable for the Flask app
ENV FLASK_APP=main.py

# Start the Flask app
CMD ["flask", "run", "--host", "0.0.0.0"]