#!/usr/bin/env python3
"""Use branding/Updated_background.png as the launch and first-login background."""
from pathlib import Path

STARTUP_BACKGROUND = "@drawable/child_care_thrive_startup_background"
APP_BACKGROUND = "@drawable/child_care_thrive_app_background"
REPLACEMENT_IMAGE = "@drawable/child_care_thrive_app_background_image"


def put(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    print(f"patched {path}")


def bitmap_background(drawable_ref: str) -> str:
    return f'''<?xml version="1.0" encoding="utf-8"?>
<layer-list xmlns:android="http://schemas.android.com/apk/res/android">
    <item android:drawable="@android:color/white" />
    <item>
        <bitmap android:src="{drawable_ref}" android:gravity="fill" />
    </item>
</layer-list>
'''


def main() -> None:
    root = Path.cwd()

    # The workflow copies branding/Updated_background.png into this drawable name.
    put(
        root / "collect_app/src/main/res/drawable/child_care_thrive_startup_background.xml",
        bitmap_background(REPLACEMENT_IMAGE),
    )

    first_launch = root / "collect_app/src/main/res/layout/first_launch_layout.xml"
    text = first_launch.read_text(encoding="utf-8")
    text = text.replace(APP_BACKGROUND, STARTUP_BACKGROUND)
    first_launch.write_text(text, encoding="utf-8")
    print(f"patched {first_launch}")


if __name__ == "__main__":
    main()
