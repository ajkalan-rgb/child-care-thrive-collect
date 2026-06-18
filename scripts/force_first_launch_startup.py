#!/usr/bin/env python3
"""Force Child-Care Thrive clean-install/login behaviour in the cloned Collect source.

This is run inside the GitHub Actions build after the normal branding patch.
It keeps the first-launch/login screen visibly branded with the startup artwork
and prevents Android backup/restore from bringing back a previously configured
project after uninstall/reinstall on the same device.
"""
from __future__ import annotations

import re
from pathlib import Path

STARTUP_BACKGROUND = "@drawable/child_care_thrive_startup_background"
APP_BACKGROUND = "@drawable/child_care_thrive_app_background"


def txt(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def put(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8")
    print(f"patched {path}")


def set_application_attr(text: str, attr: str, value: str) -> str:
    """Set or add an attribute on the manifest <application> element."""
    attr_pattern = rf'({re.escape(attr)}=)"[^"]*"'
    if re.search(attr_pattern, text):
        return re.sub(attr_pattern, rf'\1"{value}"', text, count=1)

    return re.sub(
        r'(<application\b)([^>]*>)',
        lambda match: f'{match.group(1)}\n        {attr}="{value}"{match.group(2)}',
        text,
        count=1,
        flags=re.DOTALL,
    )


def patch_manifest(root: Path) -> None:
    manifest = root / "collect_app/src/main/AndroidManifest.xml"
    if not manifest.exists():
        raise SystemExit(f"Missing expected manifest: {manifest}")

    text = txt(manifest)
    original = text
    text = set_application_attr(text, "android:allowBackup", "false")
    text = set_application_attr(text, "android:fullBackupContent", "false")
    text = set_application_attr(text, "android:restoreAnyVersion", "false")

    if text != original:
        put(manifest, text)
    else:
        print(f"manifest backup/restore attributes already patched: {manifest}")


def patch_first_launch_layout(root: Path) -> None:
    first_launch = root / "collect_app/src/main/res/layout/first_launch_layout.xml"
    if not first_launch.exists():
        raise SystemExit(f"Missing expected first-launch layout: {first_launch}")

    text = txt(first_launch)
    original = text

    # The normal app background is used after login. First launch must keep the
    # startup artwork visible so users understand they are at initial setup/login.
    text = text.replace(APP_BACKGROUND, STARTUP_BACKGROUND)

    # If upstream changed the layout and no Child-Care background is present,
    # add the startup background to the first element that fills the viewport.
    if STARTUP_BACKGROUND not in text:
        def add_background(match: re.Match[str]) -> str:
            tag = match.group(0)
            if "android:background=" in tag:
                return re.sub(r'android:background="[^"]*"', f'android:background="{STARTUP_BACKGROUND}"', tag, count=1)
            return tag[:-1] + f'\n    android:background="{STARTUP_BACKGROUND}">'

        text = re.sub(
            r'<[\w.]+\b(?=[^>]*android:fillViewport="true")[^>]*>',
            add_background,
            text,
            count=1,
            flags=re.DOTALL,
        )

    if text != original:
        put(first_launch, text)
    else:
        print(f"first-launch startup background already patched: {first_launch}")


def main() -> None:
    root = Path.cwd()
    patch_manifest(root)
    patch_first_launch_layout(root)


if __name__ == "__main__":
    main()
