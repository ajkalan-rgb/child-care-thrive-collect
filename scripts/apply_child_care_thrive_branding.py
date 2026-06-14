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
REQUIRE_ASSETS = os.getenv("REQUIRE_BRANDING_ASSETS", "true").lower() not in {"0", "false", "no"}

LOGO_XML = """<?xml version="1.0" encoding="utf-8"?>
<vector xmlns:android="http://schemas.android.com/apk/res/android" android:width="108dp" android:height="108dp" android:viewportWidth="108" android:viewportHeight="108">
    <path android:fillColor="#FFFFFF" android:pathData="M0,0h108v108h-108z" />
    <path android:fillColor="#D71920" android:pathData="M10,38h88v32h-88z" />
    <path android:fillColor="#111111" android:pathData="M22,50h64v8h-64z" />
</vector>
"""

DEFAULT_BG_XML = """<?xml version="1.0" encoding="utf-8"?>
<layer-list xmlns:android="http://schemas.android.com/apk/res/android">
    <item android:drawable="@android:color/white" />
    <item android:gravity="center" android:width="216dp" android:height="216dp" android:drawable="@drawable/child_care_thrive_logo" />
</layer-list>
"""


def txt(p: Path) -> str:
    return p.read_text(encoding="utf-8")


def put(p: Path, s: str) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(s, encoding="utf-8")


def patch_file(p: Path, old_new: list[tuple[str, str]]) -> None:
    if not p.exists():
        return
    s = txt(p)
    o = s
    for old, new in old_new:
        s = s.replace(old, new)
    if s != o:
        put(p, s)
        print(f"patched {p}")


def find_asset(root: Path, names: list[str]) -> Path | None:
    for base in [root / "branding", root.parent / "branding", Path.cwd() / "branding"]:
        for name in names:
            p = base / name
            if p.exists():
                return p
    return None


def copy_asset(src: Path, dst_dir: Path, stem: str) -> str:
    ext = ".jpg" if src.suffix.lower() == ".jpeg" else src.suffix.lower()
    if ext not in {".png", ".jpg", ".xml"}:
        raise SystemExit(f"Unsupported asset: {src}")
    dst = dst_dir / f"{stem}{ext}"
    shutil.copyfile(src, dst)
    print(f"copied {src} to {dst}")
    return f"@drawable/{stem}"


def bg_xml(drawable_ref: str) -> str:
    return f"""<?xml version="1.0" encoding="utf-8"?>
<layer-list xmlns:android="http://schemas.android.com/apk/res/android">
    <item android:drawable="@android:color/white" />
    <item><bitmap android:src="{drawable_ref}" android:gravity="fill" /></item>
</layer-list>
"""


def ensure_secrets(root: Path) -> None:
    if not (root / "secrets.gradle").exists():
        put(root / "secrets.gradle", """import java.util.Properties
ext.getSecrets = { ->
    def props = new Properties()
    def secretsFile = rootProject.file('secrets.properties')
    if (secretsFile.exists()) { secretsFile.withInputStream { props.load(it) } }
    return props
}
""")
    if not (root / "secrets.properties").exists():
        put(root / "secrets.properties", """GOOGLE_MAPS_API_KEY=
MAPBOX_ACCESS_TOKEN=
MAPBOX_DOWNLOADS_TOKEN=
ENTITIES_FILTER_PROJECT_URL=
ENTITIES_FILTER_SEARCH_PROJECT_URL=
THOUSAND_MEDIA_FILE_PROJECT_URL=
THOUSAND_MEDIA_FILE_ENTITY_LIST_PROJECT_URL=
""")


def patch_build(root: Path) -> None:
    p = root / "collect_app" / "build.gradle"
    s = txt(p)
    s = re.sub(r"applicationId\(['\"][^'\"]+['\"]\)", f"applicationId('{PACKAGE_ID}')", s)
    s = s.replace("archivesBaseName = 'ODK-Collect'", f"archivesBaseName = '{APK_BASENAME}'")
    s = s.replace("apply plugin: 'com.google.gms.google-services'", "// Disabled for Child-Care Thrive fork build")
    s = s.replace("apply plugin: 'com.google.firebase.crashlytics'", "// Disabled for Child-Care Thrive fork build")
    put(p, s)


def patch_manifest(root: Path) -> None:
    p = root / "collect_app/src/main/AndroidManifest.xml"
    patch_file(p, [
        ("org.koboc.collect.android.provider.odk.forms", f"{PACKAGE_ID}.provider.odk.forms"),
        ("org.koboc.collect.android.provider.odk.instances", f"{PACKAGE_ID}.provider.odk.instances"),
        ("android:label=\"ODK Form\"", f"android:label=\"{APP_NAME} Form\""),
        ('android:icon="@mipmap/ic_launcher"', 'android:icon="@drawable/child_care_thrive_logo"'),
        ('android:roundIcon="@mipmap/ic_launcher_round"', 'android:roundIcon="@drawable/child_care_thrive_logo"'),
    ])


def patch_strings(root: Path) -> None:
    for p in root.rglob("src/main/res/values*/*.xml"):
        try:
            s = txt(p)
        except UnicodeDecodeError:
            continue
        o = s
        s = re.sub(r"<string\s+name=\"collect_app_name\"[^>]*>.*?</string>", f"<string name=\"collect_app_name\">{xml_escape(APP_NAME)}</string>", s, flags=re.DOTALL)
        s = s.replace("KoboCollect", APP_NAME).replace("Kobo Collect", APP_NAME).replace("ODK Collect", APP_NAME)
        if s != o:
            put(p, s)
    put(root / "collect_app/src/main/res/values/child_care_thrive_strings.xml", f"""<?xml version="1.0" encoding="utf-8"?>
<resources><string name="child_care_thrive_brand_line">{xml_escape(BRAND_LINE)}</string></resources>
""")


def patch_assets(root: Path) -> None:
    d = root / "collect_app/src/main/res/drawable"
    d.mkdir(parents=True, exist_ok=True)
    icon = find_asset(root, ["child_care_icon.png", "child_care_icon.xml", "child_care_logo.png", "logo.png", "icon.png"])
    app_bg = find_asset(root, ["child_care_splash.png", "child_care_splash.jpg", "child_care_splash.xml", "child_care_banner.png", "splash.png", "splash.jpg", "banner.png"])
    startup = find_asset(root, ["chil_thrie_startup.png", "child_thrie_startup.png", "child_thrive_startup.png", "child_care_startup.png", "startup.png", "startup_screen.png"])
    if REQUIRE_ASSETS and not icon:
        raise SystemExit("Missing branding/child_care_icon.png")
    if REQUIRE_ASSETS and not startup:
        raise SystemExit("Missing branding/chil_thrie_startup.png")
    logo_ref = copy_asset(icon, d, "child_care_thrive_logo") if icon else None
    if not logo_ref:
        put(d / "child_care_thrive_logo.xml", LOGO_XML)
    startup_ref = copy_asset(startup, d, "child_care_thrive_startup") if startup else "@drawable/child_care_thrive_logo"
    app_ref = copy_asset(app_bg, d, "child_care_thrive_app_background_image") if app_bg else startup_ref
    put(d / "child_care_thrive_startup_background.xml", bg_xml(startup_ref))
    put(d / "child_care_thrive_app_background.xml", bg_xml(app_ref))
    for folder in (root / "collect_app/src/main/res").glob("mipmap-*"):
        for name in ["ic_launcher.xml", "ic_launcher_round.xml"]:
            p = folder / name
            if p.exists():
                p.unlink()


def set_style_item(body: str, item: str, value: str) -> str:
    pattern = rf"<item name=\"{re.escape(item)}\">.*?</item>"
    repl = f"<item name=\"{item}\">{value}</item>"
    return re.sub(pattern, repl, body, flags=re.DOTALL) if re.search(pattern, body, flags=re.DOTALL) else body + f"\n        {repl}"


def patch_style(text: str, style: str, updates: dict[str, str]) -> str:
    pattern = rf"(<style name=\"{re.escape(style)}\"[^>]*>)(.*?)(</style>)"
    def repl(m: re.Match[str]) -> str:
        body = m.group(2)
        for k, v in updates.items():
            body = set_style_item(body, k, v)
        return m.group(1) + body + m.group(3)
    return re.sub(pattern, repl, text, flags=re.DOTALL)


def patch_themes(root: Path) -> None:
    for p in (root / "collect_app/src/main/res").rglob("*.xml"):
        try:
            s = txt(p)
        except UnicodeDecodeError:
            continue
        o = s
        s = patch_style(s, "Theme.Collect.SplashScreen", {
            "windowSplashScreenAnimatedIcon": "@drawable/child_care_thrive_logo",
            "windowSplashScreenBackground": "@android:color/white",
            "android:windowBackground": "@drawable/child_care_thrive_startup_background",
        })
        s = patch_style(s, "Theme.Collect", {
            "android:windowBackground": "@drawable/child_care_thrive_app_background",
        })
        if s != o:
            put(p, s)


def main() -> None:
    root = Path.cwd().resolve()
    if not (root / "settings.gradle").exists():
        raise SystemExit("Run from KoboCollect source root")
    ensure_secrets(root)
    patch_build(root)
    patch_assets(root)
    patch_manifest(root)
    patch_strings(root)
    patch_themes(root)
    put(root / "CHILD_CARE_THRIVE_BRANDING_APPLIED.md", "Startup uses chil_thrie_startup.png. App background uses child_care_splash.png.\n")
    print("Child-Care Thrive branding patch complete")


if __name__ == "__main__":
    main()
