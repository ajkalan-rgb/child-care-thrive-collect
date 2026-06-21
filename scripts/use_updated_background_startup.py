#!/usr/bin/env python3
"""Compatibility entry point for the new-only first-launch screen patch."""
from pathlib import Path
import runpy

runpy.run_path(
    str(Path(__file__).with_name("apply_new_only_startup_screen.py")),
    run_name="__main__",
)
