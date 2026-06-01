#!/usr/bin/env python3
"""
Apply Child-Care Thrive branding to a KoboCollect source checkout.

Run from the root of a freshly cloned KoboCollect repository:

    python3 /path/to/apply_child_care_thrive_branding.py

What this patches:
- Android applicationId/package identity
- APK base name
- launcher/app labels
- exposed provider authorities
- external shortcut label
- splash/launcher placeholder assets
- optional real branding assets from ../branding or ./branding

This deliberately does not change KoboCollect's core data-collection engine.
"""

from __future__ import annotations

import re
import shutil
from pathlib import Path

APP_NAME = "Child-Care Thrive"
PACKAGE_ID = "za.co.childcarethrive.collect"
BRAND_LINE = "Child-Care Thrive powered by HIV Survivors & Partners Network"
APK_BASENAME = "Child-Care-Thrive-Collect"


VECTOR_LOGO = """<?xml version="1.0" encoding="utf-8"?>
<vector xmlns:android="http://schemas.android.com/apk/res/android"
    android:width="108dp"
    android:height="108dp"
    android:viewportWidth="108"
    android:viewportHeight="108">
    <path android:fillColor="#FFFFFF" android:pathData="M0,0h108v108h-108z" />
    <path android:fillColor="#D71920" android:pathData="M10,38h88v32h-88z" />
    <path android:fillColor="#FFFFFF" android:pathData="M18,44h72v20h-72z" />
    <path android:fillColor="#111111" android:pathData="M30,49h48v4h-48zM26,57h56v4h-56z" />
</vector>
"""

SPLASH_LAYER_LIST = """<?xml version="1.0" encoding="utf-8"?>
<layer-list xmlns:android="http://schemas.android.com/apk/res/android">
    <item android:drawable="@android:color/white" />
    <item
        android:gravity="center"
        android:width="216dp"
        android:height="216dp"
        android:drawable="@drawable/child_care_thrive_logo" />
</layer-list>
"""

ADAPTIVE_ICON = """<?xml version="1.0" encoding="utf-8"?>
<adaptive-icon xmlns:android="http://schemas.android.com/apk/res/android">
    <background android:drawable="@android:color/white" />
    <foreground android:drawable="@drawable/child_care_thrive_logo" />
</adaptive-icon>
"""

ROUND_ICON = ADAPTIVE_ICON


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def patch_text_file(path: Path, transforms: list[tuple[str, str]]) -> None:
    if not path.exists():
        print(f"skip missing {path}")
        return

    text = read_text(path)
    original = text
    for old, new in transforms:
        text = text.replace(old, new)

    if text != original:
        write_text(path, text)
        print(f"patched {path}")
    else:
        print(f"no changes needed {path}")


def regex_replace_file(path: Path, patterns: list[tuple[str, str]]) -> None:
    if not path.exists():
        print(f"skip missing {path}")
        return

    text = read_text(path)
    original = text
    for pattern, replacement in patterns:
        text = re.sub(pattern, replacement, text, flags=re.DOTALL)

    if text != original:
        write_text(path, text)
        print(f"patched {path}")
    else:
        print(f"no regex changes needed {path}")


def ensure_secrets(root: Path) -> None:
    secrets_gradle = root / "secrets.gradle"
    if not secrets_gradle.exists():
        write_text(
            secrets_gradle,
            """import java.util.Properties

ext.getSecrets = { ->
    def props = new Properties()
    def secretsFile = rootProject.file('secrets.properties')
    if (secretsFile.exists()) {
        secretsFile.withInputStream { props.load(it) }
    }
    return props
}
""",
        )
        print("created secrets.gradle")

    secrets_properties = root / "secrets.properties"
    if not secrets_properties.exists():
        write_text(
            secrets_properties,
            """GOOGLE_MAPS_API_KEY=
MAPBOX_ACCESS_TOKEN=
MAPBOX_DOWNLOADS_TOKEN=
ENTITIES_FILTER_PROJECT_URL=
ENTITIES_FILTER_SEARCH_PROJECT_URL=
THOUSAND_MEDIA_FILE_PROJECT_URL=
THOUSAND_MEDIA_FILE_ENTITY_LIST_PROJECT_URL=
""",
        )
        print("created secrets.properties")


def patch_build_gradle(root: Path) -> None:
    build_gradle = root / "collect_app" / "build.gradle"
    if not build_gradle.exists():
        raise FileNotFoundError("collect_app/build.gradle not found. Are you in the KoboCollect repo root?")

    text = read_text(build_gradle)
    text = re.sub(r"applicationId\(['\"][^'\"]+['\"]\)", f"applicationId('{PACKAGE_ID}')", text)
    text = text.replace("archivesBaseName = 'ODK-Collect'", f"archivesBaseName = '{APK_BASENAME}'")

    # The upstream build applies Google services / Crashlytics at the bottom. A fork build without
    # official google-services.json should not fail because of missing Google/Firebase config.
    text = text.replace(
        "apply plugin: 'com.google.gms.google-services'",
        "// Child-Care Thrive fork: google-services disabled for unsigned/test fork build",
    )
    text = text.replace(
        "apply plugin: 'com.google.firebase.crashlytics'",
        "// Child-Care Thrive fork: crashlytics disabled for unsigned/test fork build",
    )

    write_text(build_gradle, text)
    print("patched collect_app/build.gradle")


def patch_manifest(root: Path) -> None:
    manifest = root / "collect_app" / "src" / "main" / "AndroidManifest.xml"
    patch_text_file(
        manifest,
        [
            ("org.koboc.collect.android.provider.odk.forms", f"{PACKAGE_ID}.provider.odk.forms"),
            ("org.koboc.collect.android.provider.odk.instances", f"{PACKAGE_ID}.provider.odk.instances"),
            ("android:label=\"ODK Form\"", f"android:label=\"{APP_NAME} Form\""),
        ],
    )


def patch_strings(root: Path) -> None:
    strings_file = root / "strings" / "src" / "main" / "res" / "values" / "strings.xml"
    if strings_file.exists():
        text = read_text(strings_file)
        original = text

        if 'name="collect_app_name"' in text:
            text = re.sub(
                r"<string name=\"collect_app_name\">.*?</string>",
                f"<string name=\"collect_app_name\">{APP_NAME}</string>",
                text,
            )
        else:
            text = text.replace("</resources>", f"    <string name=\"collect_app_name\">{APP_NAME}</string>\n</resources>")

        text = text.replace("KoboCollect", APP_NAME)
        text = text.replace("Kobo Collect", APP_NAME)
        text = text.replace("ODK Collect", APP_NAME)

        if text != original:
            write_text(strings_file, text)
            print("patched strings module labels")
        else:
            print("strings module labels already patched")

    override_dir = root / "collect_app" / "src" / "main" / "res" / "values"
    write_text(
        override_dir / "child_care_thrive_strings.xml",
        f"""<?xml version="1.0" encoding="utf-8"?>
<resources>
    <string name="child_care_thrive_brand_line">{BRAND_LINE}</string>
</resources>
""",
    )
    print("created collect_app brand-line string")


def find_branding_asset(root: Path, file_names: list[str]) -> Path | None:
    candidate_dirs = [
        root / "branding",
        root.parent / "branding",
        Path.cwd() / "branding",
    ]

    for folder in candidate_dirs:
        for name in file_names:
            path = folder / name
            if path.exists():
                return path
    return None


def write_launcher_and_splash_assets(root: Path) -> None:
    res = root / "collect_app" / "src" / "main" / "res"
    drawable = res / "drawable"
    drawable.mkdir(parents=True, exist_ok=True)

    icon_asset = find_branding_asset(root, ["child_care_icon.png", "icon.png", "launcher.png"])
    splash_asset = find_branding_asset(root, ["child_care_splash.png", "splash.png", "child_care_splash.jpg", "splash.jpg"])

    if icon_asset:
        shutil.copyfile(icon_asset, drawable / "child_care_thrive_logo.png")
        print(f"copied real icon asset from {icon_asset}")
    else:
        write_text(drawable / "child_care_thrive_logo.xml", VECTOR_LOGO)
        print("created vector placeholder icon asset")

    if splash_asset:
        suffix = splash_asset.suffix.lower()
        target = drawable / f"child_care_thrive_splash{suffix}"
        shutil.copyfile(splash_asset, target)
        print(f"copied real splash asset from {splash_asset}")
    else:
        write_text(drawable / "child_care_thrive_splash.xml", SPLASH_LAYER_LIST)
        print("created layer-list placeholder splash asset")

    for folder in res.glob("mipmap-*"):
        if folder.is_dir():
            write_text(folder / "ic_launcher.xml", ADAPTIVE_ICON)
            write_text(folder / "ic_launcher_round.xml", ROUND_ICON)

    print("wrote launcher adaptive icon XML files")


def patch_splash_themes(root: Path) -> None:
    res = root / "collect_app" / "src" / "main" / "res"
    for xml in res.rglob("*.xml"):
        try:
            text = read_text(xml)
        except UnicodeDecodeError:
            continue

        if "windowSplashScreen" not in text:
            continue

        original = text
        text = re.sub(
            r"<item name=\"windowSplashScreenAnimatedIcon\">.*?</item>",
            "<item name=\"windowSplashScreenAnimatedIcon\">@drawable/child_care_thrive_logo</item>",
            text,
            flags=re.DOTALL,
        )
        text = re.sub(
            r"<item name=\"windowSplashScreenBackground\">.*?</item>",
            "<item name=\"windowSplashScreenBackground\">@android:color/white</item>",
            text,
            flags=re.DOTALL,
        )

        if text != original:
            write_text(xml, text)
            print(f"patched splash theme {xml}")


def write_branding_summary(root: Path) -> None:
    write_text(
        root / "CHILD_CARE_THRIVE_BRANDING_APPLIED.md",
        f"""# Child-Care Thrive branding patch applied

- App name: {APP_NAME}
- Package ID: `{PACKAGE_ID}`
- Brand line: {BRAND_LINE}
- APK base name: `{APK_BASENAME}`

Notes:

- KoboCollect/ODK Collect core collection logic has not been rewritten.
- This is a source-level Android build patch, not a compiled APK binary patch.
- If real assets are supplied under `branding/`, the script copies them into Android resources.
- Without real assets, the script creates simple placeholder launcher/splash assets so the build can proceed.
""",
    )


def main() -> None:
    root = Path.cwd().resolve()
    if not (root / "settings.gradle").exists():
        raise SystemExit("Run this script from the root of a KoboCollect source checkout")

    ensure_secrets(root)
    patch_build_gradle(root)
    patch_manifest(root)
    patch_strings(root)
    write_launcher_and_splash_assets(root)
    patch_splash_themes(root)
    write_branding_summary(root)

    print("Child-Care Thrive branding patch complete")


if __name__ == "__main__":
    main()
