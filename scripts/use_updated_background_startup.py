#!/usr/bin/env python3
"""Apply the approved Child-Care Thrive startup and main-menu compositions."""
from pathlib import Path
import runpy

scripts = Path(__file__).parent
for script in (
    "apply_new_only_startup_screen.py",
    "apply_new_background_main_menu.py",
):
    runpy.run_path(str(scripts / script), run_name="__main__")
