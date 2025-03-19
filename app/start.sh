#!/bin/bash
set -e

# Check if certificates exist, generate them if they don't
if [ ! -f "/certs/cert.pem" ] || [ ! -f "/certs/key.pem" ]; then
  echo "Certificates not found, generating them..."
  mkdir -p /certs
  /app/generate_certs.sh
  echo "Certificates generated."
fi

echo "Running migrations..."
alembic upgrade head

echo "Starting app..."
exec python main.py
