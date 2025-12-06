#!/bin/bash

# stop the app running on 8020 port
pkill -f "uvicorn app.main:app --host 0.0.0.0 --port 8020"

echo "Blog on port 8020 has been stopped."