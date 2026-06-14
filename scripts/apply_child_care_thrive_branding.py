#!/usr/bin/env python3
from __future__ import annotations

import os
import re
import shutil
from pathlib import Path
from xml.sax.saxutils import escape as xml_escape

APP_NAME = "Child-Care Thrive"
PACKAGE_ID = "za.co.childcarethrive.collect"
BRAND_LINE = "Child-Care Thrive powered by HIV Survivors & Partners Network"
APK_BASENAME = "Child-Care-Thrive-Collect"
REQUIRE_BRANDING_ASSETS = os.getenv("REQUIRE_BRANDING_ASSETS", "true").lower() not in {"0", "false", "no"}

PLACEHOLDER_LOGO = """<?xml version="1.0" encoding="utf-8"?>
<vector xmlns:android="http://schemas.android.com/apk/res/android"
    android:width="108dp" android:height="108dp" android:viewportWidth="108" android:viewportHeight="108">
    <path android:fillColor="#FFFFFF" android:pathData="M0,0h108v108h-108z" />
    <path android:fillColor="#D71920" android:pathData="M10,38h88v32h-88z" />
    <path android:fillColor="#111111" android:pathData="M22,50h64v8h-64z" />
</vector>
"""

DEFAULT_SPLASH_BACKGROUND = """<?xml version="1.0" encoding="utf-8"?>
<layer-list xmlns:android="http://schemas.android.com/apk/res/android">
    <item android:drawable="@android:color/white" />
    <item android:gravity="center" android:width="216dp" android:height="216dp" android:drawable="@drawable/child_care_thrive_logo" />
</layer-list>
"""


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def replace_file(path: Path, replacements: list[tuple[str, str]]) -> None:
    if not path.exists():
        print(f"skip missing {path}")
        return
    text = read_text(path)
    original = text
    for old, new in replacements:
        text = text.replace(old, new)
    if text != original:
        write_text(path, text)
        print(f"patched {path}")


def regex_file(path: Path, replacements: list[tuple[str, str]]) -> None:
    if not path.exists():
        print(f"skip missing {path}")
        return
    text = read_text(path)
    original = text
    for pattern, repl in replacements:
        text = re.sub(pattern, repl, text, flags=re.DOTALL)
    if text != original:
        write_text(path, text)
        print(f"patched {path}")


def ensure_secrets(root: Path) -> None:
    if not (root / "secrets.gradle").exists():
        write_text(root / "secrets.gradle", """import java.util.Properties

ext.getSecrets = { ->
    def props = new Properties()
    def secretsFile = rootProject.file('secrets.properties')
    if (secretsFile.exists()) {
        secretsFile.withInputStream { props.load(it) }
    }
    return props
}
""")
    if not (root / "secrets.properties").exists():
        write_text(root / "secrets.properties", """GOOGLE_MAPS_API_KEY=
MAPBOX_ACCESS_TOKEN=
MAPBOX_DOWNLOADS_TOKEN=
ENTITIES_FILTER_PROJECT_URL=
ENTITIES_FILTER_SEARCH_PROJECT_URL=
THOUSAND_MEDIA_FILE_PROJECT_URL=
THOUSAND_MEDIA_FILE_ENTITY_LIST_PROJECT_URL=
""")


def patch_build_gradle(root: Path) -> None:
    path = root / "collect_app" / "build.gradle"
    if not path.exists():
        raise FileNotFoundError("collect_app/build.gradle not found")
    text = read_text(path)
    text = re.sub(r"applicationId\(['\"][^'\"]+['\"]\)", f"applicationId('{PACKAGE_ID}')", text)
    text = text.replace("archivesBaseName = 'ODK-Collect'", f"archivesBaseName = '{APK_BASENAME}'")
    text = text.replace("apply plugin: 'com.google.gms.google-services'", "// Disabled for Child-Care Thrive fork build")
    text = text.replace("apply plugin: 'com.google.firebase.crashlytics'", "// Disabled for Child-Care Thrive fork build")
    write_text(path, text)
    print("patched collect_app/build.gradle")


def patch_manifest(root: Path) -> None:
    path = root / "collect_app" / "src" / "main" / "AndroidManifest.xml"
    replace_file(path, [
        ("org.koboc.collect.android.provider.odk.forms", f"{PACKAGE_ID}.provider.odk.forms"),
        ("org.koboc.collect.android.provider.odk.instances", f"{PACKAGE_ID}.provider.odk.instances"),
        ("android:label=\"ODK Form\"", f"android:label=\"{APP_NAME} Form\""),
    ])
    regex_file(path, [
        (r"android:icon=\"@mipmap/ic_launcher\"", "android:icon=\"@drawable/child_care_thrive_logo\""),
        (r"android:roundIcon=\"@mipmap/ic_launcher_round\"", "android:roundIcon=\"@drawable/child_care_thrive_logo\""),
    ])


def patch_string_xml(path: Path) -> bool:
    text = read_text(path)
    original = text
    if 'name="collect_app_name"' in text:
        text = re.sub(r"<string\s+name=\"collect_app_name\"[^>]*>.*?</string>", f"<string name=\"collect_app_name\">{xml_escape(APP_NAME)}</string>", text, flags=re.DOTALL)
    text = text.replace("KoboCollect", APP_NAME)
    text = text.replace("Kobo Collect", APP_NAME)
    text = text.replace("ODK Collect", APP_NAME)
    if text != original:
        write_text(path, text)
        print(f"patched strings in {path}")
        return True
    return False


def patch_strings(root: Path) -> None:
    patched = 0
    for path in root.rglob("src/main/res/values*/*.xml"):
        try:
            if patch_string_xml(path):
                patched += 1
        except UnicodeDecodeError:
            continue
    write_text(root / "collect_app" / "src" / "main" / "res" / "values" / "child_care_thrive_strings.xml", f"""<?xml version="1.0" encoding="utf-8"?>
<resources>
    <string name="child_care_thrive_brand_line">{xml_escape(BRAND_LINE)}</string>
</resources>
""")
    print(f"patched {patched} string resource files")


def find_asset(root: Path, names: list[str]) -> Path | None:
    for folder in [root / "branding", root.parent / "branding", Path.cwd() / "branding"]:
        for name in names:
            p = folder / name
            if p.exists():
                return p
    return None


def remove_launcher_xml_collisions(root: Path) -> None:
    res = root / "collect_app" / "src" / "main" / "res"
    for folder in res.glob("mipmap-*"):
        if folder.is_dir():
            for name in ["ic_launcher.xml", "ic_launcher_round.xml"]:
                p = folder / name
                if p.exists():
                    p.unlink()
                    print(f"removed duplicate launcher XML {p}")


def copy_drawable(src: Path, drawable_dir: Path, stem: str) -> str:
    suffix = ".jpg" if src.suffix.lower() == ".jpeg" else src.suffix.lower()
    if suffix not in {".png", ".jpg", ".xml"}:
        raise SystemExit(f"Unsupported branding asset type: {src}")
    target = drawable_dir / f"{stem}{suffix}"
    shutil.copyfile(src, target)
    print(f"copied {src} to {target}")
    return f"@drawable/{stem}"


def write_splash_background(drawable_dir: Path, splash_ref: str) -> None:
    body = f"""<?xml version="1.0" encoding="utf-8"?>
<layer-list xmlns:android="http://schemas.android.com/apk/res/android">
    <item android:drawable="@android:color/white" />
    <item>
        <bitmap android:src="{splash_ref}" android:gravity="fill" />
    </item>
</layer-list>
"""
    write_text(drawable_dir / "child_care_thrive_splash_background.xml", body)


def write_assets(root: Path) -> None:
    drawable = root / "collect_app" / "src" / "main" / "res" / "drawable"
    drawable.mkdir(parents=True, exist_ok=True)
    icon = find_asset(root, ["child_care_icon.png", "child_care_icon.xml", "child_care_logo.png", "child_care_logo.xml", "logo.png", "logo.xml", "icon.png", "icon.xml", "launcher.png"])
    splash = find_asset(root, ["child_care_splash.png", "child_care_splash.jpg", "child_care_splash.xml", "child_care_banner.png", "splash.png", "splash.jpg", "banner.png"])

    if REQUIRE_BRANDING_ASSETS and not icon:
        raise SystemExit("Missing branding icon. Add branding/child_care_icon.png before building.")
    if REQUIRE_BRANDING_ASSETS and not splash:
        raise SystemExit("Missing branding splash. Add branding/child_care_splash.png before building.")

    if icon:
        copy_drawable(icon, drawable, "child_care_thrive_logo")
    else:
        write_text(drawable / "child_care_thrive_logo.xml", PLACEHOLDER_LOGO)

    if splash:
        splash_ref = copy_drawable(splash, drawable, "child_care_thrive_splash")
        write_splash_background(drawable, splash_ref)
    else:
        write_text(drawable / "child_care_thrive_splash_background.xml", DEFAULT_SPLASH_BACKGROUND)

    remove_launcher_xml_collisions(root)


def add_window_background_to_style(text: str, style_name: str) -> str:
    pattern = rf"(<style name=\"{style_name}\"[^>]*>)(.*?)(</style>)"
    def repl(match: re.Match[str]) -> str:
        body = match.group(2)
        if "android:windowBackground" not in body:
            body += "\n        <item name=\"android:windowBackground\">@drawable/child_care_thrive_splash_background</item>"
        return match.group(1) + body + match.group(3)
    return re.sub(pattern, repl, text, flags=re.DOTALL)


def patch_splash_and_background(root: Path) -> None:
    res = root / "collect_app" / "src" / "main" / "res"
    for path in res.rglob("*.xml"):
        try:
            text = read_text(path)
        except UnicodeDecodeError:
            continue
        original = text
        if "windowSplashScreen" in text:
            text = re.sub(r"<item name=\"windowSplashScreenAnimatedIcon\">.*?</item>", "<item name=\"windowSplashScreenAnimatedIcon\">@drawable/child_care_thrive_logo</item>", text, flags=re.DOTALL)
            text = re.sub(r"<item name=\"windowSplashScreenBackground\">.*?</item>", "<item name=\"windowSplashScreenBackground\">@android:color/white</item>", text, flags=re.DOTALL)
            text = add_window_background_to_style(text, "Theme.Collect.SplashScreen")
        if "<style name=\"Theme.Collect\"" in text:
            text = add_window_background_to_style(text, "Theme.Collect")
        if text != original:
            write_text(path, text)
            print(f"patched splash/background theme {path}")


def verify(root: Path) -> None:
    summary = root / "CHILD_CARE_THRIVE_BRANDING_APPLIED.md"
    write_text(summary, f"""# Child-Care Thrive branding patch applied

- App name: {APP_NAME}
- Package ID: `{PACKAGE_ID}`
- Brand line: {BRAND_LINE}
- APK base name: `{APK_BASENAME}`
- Startup/app window background: `@drawable/child_care_thrive_splash_background`
""")
    drawable = root / "collect_app" / "src" / "main" / "res" / "drawable"
    if not any((drawable / f"child_care_thrive_logo{ext}").exists() for ext in [".png", ".jpg", ".xml"]):
        raise SystemExit("Expected branded launcher resource was not created")
    if not (drawable / "child_care_thrive_splash_background.xml").exists():
        raise SystemExit("Expected branded splash background was not created")


def main() -> None:
    root = Path.cwd().resolve()
    if not (root / "settings.gradle").exists():
        raise SystemExit("Run this script from the root of a KoboCollect source checkout")
    ensure_secrets(root)
    patch_build_gradle(root)
    write_assets(root)
    patch_manifest(root)
    patch_strings(root)
    patch_splash_and_background(root)
    verify(root)
    print("Child-Care Thrive branding patch complete")


if __name__ == "__main__":
    main()
