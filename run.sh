#!/bin/bash

cd $(dirname "$0")
source ./sourceme.sh
exec ./run.py "$@"
