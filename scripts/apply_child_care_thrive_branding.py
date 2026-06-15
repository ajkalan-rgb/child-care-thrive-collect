#!/usr/bin/env python3
from __future__ import annotations

import os
import re
import shutil
import xml.etree.ElementTree as ET
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


def txt(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def put(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def patch_file(path: Path, replacements: list[tuple[str, str]]) -> None:
    if not path.exists():
        return
    text = txt(path)
    original = text
    for old, new in replacements:
        text = text.replace(old, new)
    if text != original:
        put(path, text)
        print(f"patched {path}")


def find_asset(root: Path, names: list[str]) -> Path | None:
    for base in [root / "branding", root.parent / "branding", Path.cwd() / "branding"]:
        for name in names:
            path = base / name
            if path.exists():
                return path
    return None


def copy_asset(src: Path, dst_dir: Path, stem: str) -> str:
    ext = ".jpg" if src.suffix.lower() == ".jpeg" else src.suffix.lower()
    if ext not in {".png", ".jpg", ".xml"}:
        raise SystemExit(f"Unsupported branding asset type: {src}")
    dst = dst_dir / f"{stem}{ext}"
    shutil.copyfile(src, dst)
    print(f"copied {src} to {dst}")
    return f"@drawable/{stem}"


def bitmap_background(drawable_ref: str) -> str:
    return f"""<?xml version="1.0" encoding="utf-8"?>
<layer-list xmlns:android="http://schemas.android.com/apk/res/android">
    <item android:drawable="@android:color/white" />
    <item>
        <bitmap android:src="{drawable_ref}" android:gravity="fill" />
    </item>
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
    path = root / "collect_app" / "build.gradle"
    text = txt(path)
    text = re.sub(r"applicationId\(['\"][^'\"]+['\"]\)", f"applicationId('{PACKAGE_ID}')", text)
    text = text.replace("archivesBaseName = 'ODK-Collect'", f"archivesBaseName = '{APK_BASENAME}'")
    text = text.replace("apply plugin: 'com.google.gms.google-services'", "// Disabled for Child-Care Thrive fork build")
    text = text.replace("apply plugin: 'com.google.firebase.crashlytics'", "// Disabled for Child-Care Thrive fork build")
    put(path, text)


def patch_manifest(root: Path) -> None:
    patch_file(root / "collect_app/src/main/AndroidManifest.xml", [
        ("org.koboc.collect.android.provider.odk.forms", f"{PACKAGE_ID}.provider.odk.forms"),
        ("org.koboc.collect.android.provider.odk.instances", f"{PACKAGE_ID}.provider.odk.instances"),
        ("android:label=\"ODK Form\"", f"android:label=\"{APP_NAME} Form\""),
        ('android:icon="@mipmap/ic_launcher"', 'android:icon="@drawable/child_care_thrive_logo"'),
        ('android:roundIcon="@mipmap/ic_launcher_round"', 'android:roundIcon="@drawable/child_care_thrive_logo"'),
    ])


def patch_strings(root: Path) -> None:
    for path in root.rglob("src/main/res/values*/*.xml"):
        try:
            text = txt(path)
        except UnicodeDecodeError:
            continue
        original = text
        text = re.sub(r"<string\s+name=\"collect_app_name\"[^>]*>.*?</string>", f"<string name=\"collect_app_name\">{xml_escape(APP_NAME)}</string>", text, flags=re.DOTALL)
        text = text.replace("KoboCollect", APP_NAME).replace("Kobo Collect", APP_NAME).replace("ODK Collect", APP_NAME)
        if text != original:
            put(path, text)
    put(root / "collect_app/src/main/res/values/child_care_thrive_strings.xml", f"""<?xml version="1.0" encoding="utf-8"?>
<resources>
    <string name="child_care_thrive_brand_line">{xml_escape(BRAND_LINE)}</string>
</resources>
""")


def patch_brand_colours(root: Path) -> None:
    values = root / "collect_app/src/main/res/values"
    put(values / "child_care_thrive_palette.xml", """<?xml version="1.0" encoding="utf-8"?>
<resources>
    <color name="child_care_text_primary">#061B2A</color>
    <color name="child_care_text_secondary">#0B2A3C</color>
    <color name="child_care_app_bar">#001117</color>
    <color name="child_care_primary_button">#0B6F8A</color>
    <color name="child_care_dark_button">#263134</color>
</resources>
""")

    colors = values / "colors.xml"
    if colors.exists():
        text = txt(colors)
        for name, value in {
            "colorPrimaryLight": "#001117",
            "colorOnPrimaryLight": "#FFFFFF",
            "colorPrimaryContainerLight": "#D8F0FF",
            "colorOnPrimaryContainerLight": "#061B2A",
            "colorSurfaceLight": "#FFFFFF",
            "colorPrimaryDark": "#001117",
            "colorOnPrimaryDark": "#FFFFFF",
            "colorPrimaryContainerDark": "#263134",
            "colorOnPrimaryContainerDark": "#FFFFFF",
            "colorSurfaceDark": "#FFFFFF",
        }.items():
            text = re.sub(rf"<color name=\"{name}\">.*?</color>", f"<color name=\"{name}\">{value}</color>", text)
        put(colors, text)


def patch_assets(root: Path) -> None:
    drawable = root / "collect_app/src/main/res/drawable"
    drawable.mkdir(parents=True, exist_ok=True)

    icon = find_asset(root, ["child_care_icon.png", "child_care_icon.xml", "child_care_logo.png", "logo.png", "icon.png"])
    splash = find_asset(root, ["child_care_splash.png", "child_care_splash.jpg", "child_care_splash.xml", "child_care_banner.png", "splash.png", "splash.jpg", "banner.png"])
    startup = find_asset(root, ["child_care_startup.png", "startup.png", "startup_screen.png", "child_thrive_startup.png", "child_thrie_startup.png", "chil_thrive_startup.png", "chil_thrie_startup.png"])

    if REQUIRE_ASSETS and not icon:
        raise SystemExit("Missing branding/child_care_icon.png")
    if REQUIRE_ASSETS and not startup:
        raise SystemExit("Missing branding/child_care_startup.png")

    if icon:
        copy_asset(icon, drawable, "child_care_thrive_logo")
    else:
        put(drawable / "child_care_thrive_logo.xml", LOGO_XML)

    startup_ref = copy_asset(startup, drawable, "child_care_thrive_startup") if startup else "@drawable/child_care_thrive_logo"
    splash_ref = copy_asset(splash, drawable, "child_care_thrive_app_background_image") if splash else startup_ref
    put(drawable / "child_care_thrive_startup_background.xml", bitmap_background(startup_ref))
    put(drawable / "child_care_thrive_app_background.xml", bitmap_background(splash_ref))

    for folder in (root / "collect_app/src/main/res").glob("mipmap-*"):
        for name in ["ic_launcher.xml", "ic_launcher_round.xml"]:
            path = folder / name
            if path.exists():
                path.unlink()


def set_style_item(body: str, item: str, value: str) -> str:
    pattern = rf"<item name=\"{re.escape(item)}\">.*?</item>"
    replacement = f"<item name=\"{item}\">{value}</item>"
    if re.search(pattern, body, flags=re.DOTALL):
        return re.sub(pattern, replacement, body, flags=re.DOTALL)
    return body + f"\n        {replacement}"


def patch_style(text: str, style: str, updates: dict[str, str]) -> str:
    pattern = rf"(<style name=\"{re.escape(style)}\"[^>]*>)(.*?)(</style>)"

    def replace(match: re.Match[str]) -> str:
        body = match.group(2)
        for key, value in updates.items():
            body = set_style_item(body, key, value)
        return match.group(1) + body + match.group(3)

    return re.sub(pattern, replace, text, flags=re.DOTALL)


def patch_themes(root: Path) -> None:
    updates = {
        "android:textColorPrimary": "@color/child_care_text_primary",
        "android:textColorSecondary": "@color/child_care_text_secondary",
        "colorOnSurface": "@color/child_care_text_primary",
        "colorOnSurfaceVariant": "@color/child_care_text_secondary",
        "colorOnBackground": "@color/child_care_text_primary",
        "colorPrimary": "@color/child_care_app_bar",
        "colorOnPrimary": "@android:color/white",
    }
    for path in (root / "collect_app/src/main/res").rglob("*.xml"):
        try:
            text = txt(path)
        except UnicodeDecodeError:
            continue
        original = text
        text = patch_style(text, "Theme.Collect.SplashScreen", {
            "windowSplashScreenAnimatedIcon": "@drawable/child_care_thrive_logo",
            "windowSplashScreenBackground": "@android:color/white",
            "android:windowBackground": "@drawable/child_care_thrive_startup_background",
            **updates,
        })
        text = patch_style(text, "Theme.Collect", {
            "android:windowBackground": "@drawable/child_care_thrive_app_background",
            **updates,
        })
        if text != original:
            put(path, text)


def hide_textview_by_id(xml: str, view_id: str) -> str:
    pattern = rf"(<TextView\b(?=[^>]*android:id=\"@\+id/{re.escape(view_id)}\")[^>]*)(/>)"

    def replace(match: re.Match[str]) -> str:
        block = match.group(1)
        if "android:visibility=" not in block:
            block += '\n                android:visibility="gone"'
        if "android:layout_height=" in block:
            block = re.sub(r'android:layout_height="[^"]+"', 'android:layout_height="0dp"', block)
        return block + match.group(2)

    return re.sub(pattern, replace, xml, flags=re.DOTALL)


def patch_known_text_colours(xml: str) -> str:
    for old, new in [
        ('android:textColor="#888"', 'android:textColor="@color/child_care_text_secondary"'),
        ('android:textColor="#888888"', 'android:textColor="@color/child_care_text_secondary"'),
        ('android:textColor="@color/color_on_surface_medium_emphasis"', 'android:textColor="@color/child_care_text_primary"'),
        ('android:textColor="@color/color_on_surface_low_emphasis"', 'android:textColor="@color/child_care_text_secondary"'),
        ('android:textColor="?colorOnSurface"', 'android:textColor="@color/child_care_text_primary"'),
        ('android:textColor="?attr/colorOnSurface"', 'android:textColor="@color/child_care_text_primary"'),
    ]:
        xml = xml.replace(old, new)
    return xml


def patch_button_backgrounds(root: Path) -> None:
    drawable = root / "collect_app/src/main/res/drawable"
    patch_file(drawable / "main_menu_button_background.xml", [
        ('<solid android:color="?colorSurfaceContainerLow" />', '<solid android:color="@color/child_care_dark_button" />'),
    ])
    patch_file(drawable / "start_new_form_button_background.xml", [
        ('<solid android:color="?colorPrimary" />', '<solid android:color="@color/child_care_primary_button" />'),
    ])


def patch_layouts(root: Path) -> None:
    layout_dir = root / "collect_app/src/main/res/layout"

    for path in layout_dir.glob("*.xml"):
        try:
            text = txt(path)
        except UnicodeDecodeError:
            continue
        original = text
        text = patch_known_text_colours(text)
        if text != original:
            put(path, text)

    main_menu = layout_dir / "main_menu.xml"
    if main_menu.exists():
        text = txt(main_menu)
        text = hide_textview_by_id(text, "app_name")
        text = hide_textview_by_id(text, "version_sha")
        text = text.replace('android:paddingBottom="@dimen/margin_standard"', 'android:paddingBottom="0dp"')
        put(main_menu, text)

    compact = [
        ('android:layout_marginVertical="@dimen/margin_extra_small"', 'android:layout_marginVertical="2dp"'),
        ('android:layout_marginHorizontal="@dimen/margin_standard"', 'android:layout_marginHorizontal="32dp"'),
        ('android:layout_marginVertical="@dimen/margin_standard"', 'android:layout_marginVertical="6dp"'),
        ('android:layout_marginStart="@dimen/margin_extra_large"', 'android:layout_marginStart="24dp"'),
        ('android:layout_marginEnd="@dimen/margin_extra_large"', 'android:layout_marginEnd="24dp"'),
        ('android:textAppearance="?textAppearanceLabelExtraLarge"', 'android:textAppearance="?textAppearanceTitleMedium"'),
        ('android:layout_width="wrap_content"\n        android:layout_height="wrap_content"\n        android:layout_marginStart="24dp"', 'android:layout_width="24dp"\n        android:layout_height="24dp"\n        android:layout_marginStart="24dp"'),
        ('android:layout_width="wrap_content"\n        android:layout_height="wrap_content"\n        android:layout_marginVertical="6dp"', 'android:layout_width="24dp"\n        android:layout_height="24dp"\n        android:layout_marginVertical="6dp"'),
    ]
    for name in ["main_menu_button.xml", "start_new_from_button.xml"]:
        patch_file(layout_dir / name, compact)


def validate_xml_resources(root: Path) -> None:
    errors: list[str] = []
    for path in (root / "collect_app/src/main/res").rglob("*.xml"):
        try:
            ET.parse(path)
        except ET.ParseError as error:
            errors.append(f"{path}: {error}")
    if errors:
        raise SystemExit("Invalid XML after Child-Care Thrive branding patch:\n" + "\n".join(errors[:20]))
    print("validated XML resources")


def main() -> None:
    root = Path.cwd().resolve()
    if not (root / "settings.gradle").exists():
        raise SystemExit("Run from KoboCollect source root")
    ensure_secrets(root)
    patch_build(root)
    patch_brand_colours(root)
    patch_assets(root)
    patch_manifest(root)
    patch_strings(root)
    patch_themes(root)
    patch_button_backgrounds(root)
    patch_layouts(root)
    validate_xml_resources(root)
    put(root / "CHILD_CARE_THRIVE_BRANDING_APPLIED.md", "Startup uses child_care_startup.png. App splash/background uses child_care_splash.png. Main-menu app/version text is hidden. Buttons are compact. Risky bulk layout background insertion is disabled and XML is validated before Gradle runs.\n")
    print("Child-Care Thrive branding patch complete")


if __name__ == "__main__":
    main()
