#!/usr/bin/env python3
"""ARIA OS — Database Migration Helper

Runs Alembic migrations with proper environment setup.
Reads DATABASE_URL from .env file or environment variable.

Usage:
    python scripts/run_migration.py upgrade     # Run all pending migrations
    python scripts/run_migration.py downgrade   # Rollback one step
    python scripts/run_migration.py history     # View migration history
    python scripts/run_migration.py current     # Check current version
    python scripts/run_migration.py revision -m "message"  # Create new migration
"""

import os
import sys
import subprocess
from pathlib import Path


def load_env():
    env_path = Path(__file__).resolve().parent.parent / ".env"
    if env_path.exists():
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    os.environ.setdefault(key.strip(), value.strip().strip("'\""))


def main():
    load_env()

    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        print("ERROR: DATABASE_URL not set. Set it in .env or as environment variable.")
        print("Example: DATABASE_URL=postgresql://user:pass@host:5432/aria_os")
        sys.exit(1)

    migrations_dir = str(Path(__file__).resolve().parent / "migrations")
    os.chdir(migrations_dir)

    args = ["alembic"] + sys.argv[1:] if len(sys.argv) > 1 else ["alembic", "upgrade", "head"]

    print(f"Running: {' '.join(args)}")
    print(f"Database: {database_url[:database_url.rfind('@')+1]}****@{database_url.split('@')[-1]}")
    print()

    result = subprocess.run(args, env={**os.environ, "DATABASE_URL": database_url})
    sys.exit(result.returncode)


if __name__ == "__main__":
    main()
