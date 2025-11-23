#!/bin/bash
# Backend build script for Vercel
# Installs only backend dependencies to reduce deployment size

set -e

echo "🔧 Installing backend dependencies only..."
pip install -r requirements-backend.txt

echo "✅ Backend dependencies installed successfully"

