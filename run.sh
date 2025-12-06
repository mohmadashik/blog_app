#!/bin/bash

# Load the app on 8020 port 

echo "Starting the blog App on port 8020..."
uvicorn app.main:app --host 0.0.0.0 --port 8020

echo "Blog is running on port 8020."
