#!/usr/bin/env bash
# exit on error
set -o errexit

# Frontend'i build et
cd frontend
npm install
npm run build
cd ..

# Backend bağımlılıklarını kur
pip install -r requirements.txt
