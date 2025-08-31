#!/bin/bash

# Navigate to the app directory
cd "/Users/natantzvi.roth/Documents/natan-transcribe-main/app"

# Activate virtual environment
source "/Users/natantzvi.roth/Documents/natan-transcribe-main/venv/bin/activate"

# Start streamlit
exec streamlit run main.py --server.port=8501 --server.address=localhost --server.headless=true --server.maxUploadSize=10000
