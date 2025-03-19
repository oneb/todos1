FROM python:3.9-slim

WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all files
COPY . .

# Expose the port that will be used by FastAPI
EXPOSE 8000

# Copy and make the startup script executable
COPY start.sh .
RUN chmod +x start.sh

# Run the application with migrations
CMD ["./start.sh"]