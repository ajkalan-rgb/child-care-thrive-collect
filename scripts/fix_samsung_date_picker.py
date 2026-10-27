#!/usr/bin/env python3
"""Align native KoboCollect date-picker dialogs to the Child-Care Thrive light theme.

Run *after* apply_child_care_thrive_branding.py. Upstream changes fail closed.
"""
from pathlib import Path
import re

theme = Path("collect_app/src/main/java/org/odk/collect/android/utilities/ThemeUtils.java")
styles = Path("collect_app/src/main/res/values/date_time_pickers.xml")
palette = Path("collect_app/src/main/res/values/child_care_thrive_palette.xml")
for path in (theme, styles, palette):
    if not path.is_file():
        raise SystemExit(f"FAIL: required branded upstream source is missing: {path}")

source = theme.read_text(encoding="utf-8")
for method, mode, kind in (
    ("getCalendarDatePickerDialogTheme", "Calendar", "DatePicker"),
    ("getSpinnerDatePickerDialogTheme", "Spinner", "DatePicker"),
    ("getSpinnerTimePickerDialogTheme", "Spinner", "TimePicker"),
):
    light = f"R.style.Theme_Collect_Light_{mode}_{kind}_Dialog"
    pat = re.compile(r"(@StyleRes\s+public int " + method + r"\(\)\s*\{)(.*?)(\n    \})", re.DOTALL)
    matches = list(pat.finditer(source))
    if len(matches) != 1 or light not in matches[0].group(2):
        raise SystemExit(f"FAIL: upstream picker selector changed: {method}")
    body = (
        "\n        // Child-Care Thrive app theme is Light even in Samsung dark mode.\n"
        "        // Keep native platform pickers consistent with the app theme.\n"
        f"        return {light};"
    )
    source = pat.sub(lambda m: m.group(1) + body + m.group(3), source, count=1)
theme.write_text(source, encoding="utf-8")

xml = styles.read_text(encoding="utf-8")
for style in ("Theme.Collect.Light.Calendar.DatePicker.Dialog", "Theme.Collect.Light.Dialog.Alert"):
    pat = re.compile(r'(<style name="' + re.escape(style) + r'"[^>]*>)(.*?)(\n    </style>)', re.DOTALL)
    match = pat.search(xml)
    if not match:
        raise SystemExit(f"FAIL: upstream date picker theme changed: {style}")
    body = match.group(2)
    for name, value in (
        ("android:colorBackground", "@android:color/white"),
        ("android:background", "@android:color/white"),
        ("android:textColorPrimary", "@color/child_care_text_primary"),
        ("android:textColorSecondary", "@color/child_care_text_secondary"),
        ("colorOnSurface", "@color/child_care_text_primary"),
        ("colorAccent", "@color/child_care_app_bar"),
    ):
        line = f'<item name="{name}">{value}</item>'
        key = re.compile(r'<item name="' + re.escape(name) + r'">.*?</item>')
        body = key.sub(line, body) if key.search(body) else body + "\n        " + line
    xml = xml[:match.start()] + match.group(1) + body + match.group(3) + xml[match.end():]
styles.write_text(xml, encoding="utf-8")
print("Applied explicit light date-picker styles for Samsung calendar and spinner controls.")
