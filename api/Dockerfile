FROM python:3.9-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ /app/

# Set environment variables
ENV PYTHONPATH=/app
ENV FLASK_APP=app.py

# Expose the port
EXPOSE 5000

# Command to run the application
CMD ["python", "run.py"]
