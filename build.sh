#!/usr/bin/env bash
set -o errexit

# Install backend dependencies
cd backend
pip install -e .

# Run database migrations
alembic upgrade head
cd ..

# Install frontend dependencies and build
cd frontend
npm ci
npm run build
cd ..
