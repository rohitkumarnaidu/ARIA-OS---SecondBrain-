"""Test configuration — adds project paths to sys.path for imports."""

import sys
from pathlib import Path

# Add packages/ so tests can import ai.*, config.*, database.*, shared.*
packages_path = str(Path(__file__).resolve().parent.parent / "packages")
if packages_path not in sys.path:
    sys.path.insert(0, packages_path)

# Add apps/api/ so tests can import app.api.*
api_path = str(Path(__file__).resolve().parent.parent / "apps" / "api")
if api_path not in sys.path:
    sys.path.insert(0, api_path)

# Add services/scheduler/ so tests can import crons.*
scheduler_path = str(Path(__file__).resolve().parent.parent / "services" / "scheduler")
if scheduler_path not in sys.path:
    sys.path.insert(0, scheduler_path)
