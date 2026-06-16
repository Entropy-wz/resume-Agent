#!/bin/bash
cd "$(dirname "$0")"
./venv/Scripts/python.exe test_my_resume.py "$@"
