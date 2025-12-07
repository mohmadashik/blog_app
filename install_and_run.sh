#!/usr/bin/env bash
set -e

# 1. Create venv if not exists
if [ ! -d "venv" ]; then
  python -m venv venv
fi

# 2. Activate venv
source venv/bin/activate

# 3. Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# 4. Run app
uvicorn app.main:app --host 0.0.0.0 --port 8020 --reload
