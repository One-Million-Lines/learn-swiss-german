#!/usr/bin/env bash
# One-shot local bootstrap: database schema + indexes, legacy migration,
# baseline seed, and the introductory curriculum. Idempotent — safe to re-run.
#
# Prerequisites: a MongoDB replica set reachable via MONGODB_URI (see backend/.env),
# and the backend virtualenv activated (or run through it).
set -euo pipefail
cd "$(dirname "$0")/.."

echo "==> 1/4 Database schema, validators and indexes"
python -m scripts.setup_database --apply

echo "==> 2/4 Legacy JSON migration"
python -m scripts.import_legacy --apply

echo "==> 3/4 Baseline seed (dialects + versioned config)"
python -m scripts.seed

echo "==> 4/4 Introductory curriculum (gsw-zh preview)"
python -m scripts.build_curriculum

echo ""
echo "Done. Verify with: python -m scripts.setup_database --check"
echo "Create an admin with: python -m scripts.bootstrap_admin --email you@example.com"
