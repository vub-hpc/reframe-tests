#!/bin/bash
set -euo pipefail

cd $(dirname "$0")
source ./sourceme.sh
exec ./run.py "$@"
