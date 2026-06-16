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
SERVER_URL = "https://kc.kobotoolbox.org/"
FORMS_AUTHORITY = f"{PACKAGE_ID}.provider.odk.forms"
INSTANCES_AUTHORITY = f"{PACKAGE_ID}.provider.odk.instances"
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


def replace(path: Path, pairs: list[tuple[str, str]]) -> None:
    if not path.exists():
        return
    text = txt(path)
    original = text
    for old, new in pairs:
        text = text.replace(old, new)
    if text != original:
        put(path, text)
        print(f"patched {path}")


def regex_replace(path: Path, pairs: list[tuple[str, str]]) -> None:
    if not path.exists():
        return
    text = txt(path)
    original = text
    for pattern, replacement in pairs:
        text = re.sub(pattern, replacement, text, flags=re.DOTALL)
    if text != original:
        put(path, text)
        print(f"patched {path}")


def find_asset(root: Path, names: list[str]) -> Path | None:
    for base in [root / "branding", root.parent / "branding", Path.cwd() / "branding"]:
        for name in names:
            candidate = base / name
            if candidate.exists():
                return candidate
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
    path = root / "collect_app/build.gradle"
    if not path.exists():
        return
    text = txt(path)
    text = re.sub(r"applicationId\(['\"][^'\"]+['\"]\)", f"applicationId('{PACKAGE_ID}')", text)
    text = text.replace("archivesBaseName = 'ODK-Collect'", f"archivesBaseName = '{APK_BASENAME}'")
    text = text.replace("apply plugin: 'com.google.gms.google-services'", "// Disabled for Child-Care Thrive fork build")
    text = text.replace("apply plugin: 'com.google.firebase.crashlytics'", "// Disabled for Child-Care Thrive fork build")
    put(path, text)


def patch_manifest_and_contracts(root: Path) -> None:
    replace(root / "collect_app/src/main/AndroidManifest.xml", [
        ("org.koboc.collect.android.provider.odk.forms", FORMS_AUTHORITY),
        ("org.koboc.collect.android.provider.odk.instances", INSTANCES_AUTHORITY),
        ("android:label=\"ODK Form\"", f"android:label=\"{APP_NAME} Form\""),
        ('android:icon="@mipmap/ic_launcher"', 'android:icon="@drawable/child_care_thrive_logo"'),
        ('android:roundIcon="@mipmap/ic_launcher_round"', 'android:roundIcon="@drawable/child_care_thrive_logo"'),
    ])
    replace(root / "collect_app/src/main/java/org/odk/collect/android/external/FormsContract.java", [
        ('static final String AUTHORITY = "org.koboc.collect.android.provider.odk.forms";', f'static final String AUTHORITY = "{FORMS_AUTHORITY}";'),
    ])
    replace(root / "collect_app/src/main/java/org/odk/collect/android/external/InstancesContract.java", [
        ('public static final String AUTHORITY = "org.koboc.collect.android.provider.odk.instances";', f'public static final String AUTHORITY = "{INSTANCES_AUTHORITY}";'),
    ])


def patch_strings(root: Path) -> None:
    for path in root.rglob("src/main/res/values*/*.xml"):
        try:
            text = txt(path)
        except UnicodeDecodeError:
            continue
        original = text
        text = re.sub(r"<string\s+name=\"collect_app_name\"[^>]*>.*?</string>", f"<string name=\"collect_app_name\">{xml_escape(APP_NAME)}</string>", text, flags=re.DOTALL)
        text = re.sub(r"<string\s+name=\"tagline\"[^>]*>.*?</string>", "<string name=\"tagline\">Configure project</string>", text, flags=re.DOTALL)
        text = text.replace("KoboCollect", APP_NAME).replace("Kobo Collect", APP_NAME).replace("ODK Collect", APP_NAME)
        if text != original:
            put(path, text)
    put(root / "collect_app/src/main/res/values/child_care_thrive_strings.xml", f"""<?xml version="1.0" encoding="utf-8"?>
<resources>
    <string name="child_care_thrive_brand_line">{xml_escape(BRAND_LINE)}</string>
</resources>
""")


def patch_colours(root: Path) -> None:
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
    logo_ref = copy_asset(icon, drawable, "child_care_thrive_logo") if icon else "@drawable/child_care_thrive_logo"
    if not icon:
        put(drawable / "child_care_thrive_logo.xml", LOGO_XML)
    startup_ref = copy_asset(startup, drawable, "child_care_thrive_startup") if startup else logo_ref
    splash_ref = copy_asset(splash, drawable, "child_care_thrive_app_background_image") if splash else startup_ref
    put(drawable / "child_care_thrive_startup_background.xml", bitmap_background(startup_ref))
    put(drawable / "child_care_thrive_app_background.xml", bitmap_background(splash_ref))
    for folder in (root / "collect_app/src/main/res").glob("mipmap-*"):
        for name in ["ic_launcher.xml", "ic_launcher_round.xml"]:
            if (folder / name).exists():
                (folder / name).unlink()


def set_style_item(body: str, item: str, value: str) -> str:
    pattern = rf"<item name=\"{re.escape(item)}\">.*?</item>"
    replacement = f"<item name=\"{item}\">{value}</item>"
    if re.search(pattern, body, flags=re.DOTALL):
        return re.sub(pattern, replacement, body, flags=re.DOTALL)
    return body + f"\n        {replacement}"


def patch_style(text: str, style: str, updates: dict[str, str]) -> str:
    pattern = rf"(<style name=\"{re.escape(style)}\"[^>]*>)(.*?)(</style>)"
    def repl(match: re.Match[str]) -> str:
        body = match.group(2)
        for key, value in updates.items():
            body = set_style_item(body, key, value)
        return match.group(1) + body + match.group(3)
    return re.sub(pattern, repl, text, flags=re.DOTALL)


def patch_themes(root: Path) -> None:
    app_updates = {
        "android:textColorPrimary": "@color/child_care_text_primary",
        "android:textColorSecondary": "@color/child_care_text_secondary",
        "colorOnSurface": "@color/child_care_text_primary",
        "colorOnSurfaceVariant": "@color/child_care_text_secondary",
        "colorOnBackground": "@color/child_care_text_primary",
        "colorPrimary": "@color/child_care_app_bar",
        "colorOnPrimary": "@android:color/white",
        "android:colorBackground": "@android:color/white",
        "colorSurface": "@android:color/white",
        "colorSurfaceContainerLowest": "@android:color/white",
        "colorSurfaceContainerLow": "@android:color/white",
        "colorSurfaceContainer": "@android:color/white",
        "colorSurfaceContainerHigh": "@android:color/white",
        "colorSurfaceContainerHighest": "@android:color/white",
        "android:forceDarkAllowed": "false",
        "elevationOverlayEnabled": "false",
    }
    dialog_updates = {
        "android:colorBackground": "@android:color/white",
        "colorSurface": "@android:color/white",
        "colorOnSurface": "@color/child_care_text_primary",
        "colorOnBackground": "@color/child_care_text_primary",
        "colorPrimary": "@color/child_care_app_bar",
        "colorOnPrimary": "@android:color/white",
        "android:forceDarkAllowed": "false",
        "buttonBarPositiveButtonStyle": "@style/Widget.Collect.Dialog.PositiveButton",
    }
    for path in (root / "collect_app/src/main/res").rglob("*.xml"):
        try:
            text = txt(path)
        except UnicodeDecodeError:
            continue
        original = text
        text = text.replace('parent="Theme.Material3.DayNight.NoActionBar"', 'parent="Theme.Material3.Light.NoActionBar"')
        text = patch_style(text, "Theme.Collect.SplashScreen", {"windowSplashScreenAnimatedIcon": "@drawable/child_care_thrive_logo", "windowSplashScreenBackground": "@android:color/white", "android:windowBackground": "@drawable/child_care_thrive_startup_background", **app_updates})
        text = patch_style(text, "Theme.Collect", {"android:windowBackground": "@android:color/white", **app_updates})
        text = patch_style(text, "Theme.Collect.Dialog.Alert", dialog_updates)
        text = patch_style(text, "Theme.Collect.BottomSheet", dialog_updates)
        if text != original:
            put(path, text)


def hide_view_by_id(xml: str, view_id: str) -> str:
    pattern = rf"(<[\w.]+\b(?=[^>]*android:id=\"@\+id/{re.escape(view_id)}\")[^>]*?)(\s*/?>)"
    def repl(match: re.Match[str]) -> str:
        block, close = match.group(1), match.group(2)
        if "android:visibility=" not in block:
            block += '\n                android:visibility="gone"'
        if "android:layout_height=" in block:
            block = re.sub(r'android:layout_height="[^"]+"', 'android:layout_height="0dp"', block)
        return block + close
    return re.sub(pattern, repl, xml, flags=re.DOTALL)


def patch_button_backgrounds(root: Path) -> None:
    drawable = root / "collect_app/src/main/res/drawable"
    replace(drawable / "main_menu_button_background.xml", [('<solid android:color="?colorSurfaceContainerLow" />', '<solid android:color="@color/child_care_dark_button" />')])
    replace(drawable / "start_new_form_button_background.xml", [('<solid android:color="?colorPrimary" />', '<solid android:color="@color/child_care_primary_button" />')])


def patch_layouts(root: Path) -> None:
    layout = root / "collect_app/src/main/res/layout"
    main_menu = layout / "main_menu.xml"
    if main_menu.exists():
        text = txt(main_menu)
        text = text.replace('android:layout_height="match_parent">', 'android:layout_height="match_parent"\n    android:background="@drawable/child_care_thrive_app_background">', 1)
        text = text.replace('android:layout_marginTop="@dimen/margin_extra_small"', 'android:layout_marginTop="132dp"', 1)
        text = hide_view_by_id(text, "app_name")
        text = hide_view_by_id(text, "version_sha")
        put(main_menu, text)
    first = layout / "first_launch_layout.xml"
    if first.exists():
        text = txt(first)
        text = text.replace('android:fillViewport="true">', 'android:fillViewport="true"\n    android:background="@drawable/child_care_thrive_app_background">')
        for view_id in ["logo", "configure_via_qr_button", "app_name", "dont_have_server"]:
            text = hide_view_by_id(text, view_id)
        text = text.replace('android:text="@string/tagline"', 'android:text="Configure project"')
        put(first, text)
    manual = layout / "manual_project_creator_dialog_layout.xml"
    if manual.exists():
        text = hide_view_by_id(txt(manual), "config_tip")
        put(manual, text)
    compact = [
        ('android:layout_marginVertical="@dimen/margin_extra_small"', 'android:layout_marginVertical="2dp"'),
        ('android:layout_marginHorizontal="@dimen/margin_standard"', 'android:layout_marginHorizontal="42dp"'),
        ('android:layout_marginVertical="@dimen/margin_standard"', 'android:layout_marginVertical="6dp"'),
        ('android:layout_marginStart="@dimen/margin_extra_large"', 'android:layout_marginStart="24dp"'),
        ('android:layout_marginEnd="@dimen/margin_extra_large"', 'android:layout_marginEnd="24dp"'),
        ('android:textAppearance="?textAppearanceLabelExtraLarge"', 'android:textAppearance="?textAppearanceTitleMedium"'),
        ('android:layout_width="wrap_content"\n        android:layout_height="wrap_content"\n        android:layout_marginStart="24dp"', 'android:layout_width="24dp"\n        android:layout_height="24dp"\n        android:layout_marginStart="24dp"'),
        ('android:layout_width="wrap_content"\n        android:layout_height="wrap_content"\n        android:layout_marginVertical="6dp"', 'android:layout_width="24dp"\n        android:layout_height="24dp"\n        android:layout_marginVertical="6dp"'),
    ]
    for name in ["main_menu_button.xml", "start_new_from_button.xml"]:
        replace(layout / name, compact)


def patch_preferences_xml(root: Path) -> None:
    xml_dir = root / "collect_app/src/main/res/xml"
    project = xml_dir / "project_preferences.xml"
    if project.exists():
        text = txt(project)
        if 'android:key="protected_category"' not in text:
            text = text.replace('<PreferenceCategory\n        android:title="@string/protected_settings"', '<PreferenceCategory\n        android:key="protected_category"\n        android:title="@string/protected_settings"')
        put(project, text)
    identity = xml_dir / "identity_preferences.xml"
    if identity.exists():
        put(identity, """<?xml version="1.0" encoding="utf-8"?>
<PreferenceScreen xmlns:android="http://schemas.android.com/apk/res/android" xmlns:app="http://schemas.android.com/apk/res-auto" android:title="@string/user_and_device_identity_title">
    <Preference android:key="form_metadata" android:summary="@string/form_metadata_summary" android:title="@string/form_metadata" app:iconSpaceReserved="false" app:allowDividerAbove="false" app:allowDividerBelow="false" />
</PreferenceScreen>
""")


def patch_kotlin_code(root: Path) -> None:
    menu_button = root / "collect_app/src/main/java/org/odk/collect/android/mainmenu/MainMenuButton.kt"
    if menu_button.exists():
        text = txt(menu_button)
        if "import android.graphics.Color" not in text:
            text = text.replace("import android.content.Context\n", "import android.content.Context\nimport android.graphics.Color\n")
        marker = "            binding.name.text = buttonName\n"
        injected = "            binding.name.text = buttonName\n            binding.name.setTextColor(Color.WHITE)\n            binding.number.setTextColor(Color.WHITE)\n            binding.icon.setColorFilter(Color.WHITE)\n"
        if marker in text and injected not in text:
            text = text.replace(marker, injected)
        put(menu_button, text)

    view_model = root / "collect_app/src/main/java/org/odk/collect/android/mainmenu/MainMenuViewModel.kt"
    if view_model.exists():
        replace(view_model, [("""    fun refreshInstances() {
        scheduler.immediate<Any?>({
            InstanceDiskSynchronizer(settingsProvider).doInBackground()
            instancesDataService.update(projectsDataService.requireCurrentProject().uuid)
            null
        }) { }
    }
""", """    fun refreshInstances() {
        scheduler.immediate<Any?>({
            try {
                InstanceDiskSynchronizer(settingsProvider).doInBackground()
            } catch (_: Exception) {
            } catch (_: Error) {
            }
            instancesDataService.update(projectsDataService.requireCurrentProject().uuid)
            null
        }) { }
    }
""")])

    fragment = root / "collect_app/src/main/java/org/odk/collect/android/mainmenu/MainMenuFragment.kt"
    if fragment.exists():
        text = txt(fragment)
        text = text.replace("requireActivity().title = project.name", "requireActivity().title = \"\"")
        text = re.sub(r"    override fun onPrepareOptionsMenu\(menu: Menu\) \{.*?\n    \}\n\n    override fun onCreateOptionsMenu", "    override fun onPrepareOptionsMenu(menu: Menu) {\n        menu.findItem(org.odk.collect.android.R.id.projects).isVisible = false\n    }\n\n    override fun onCreateOptionsMenu", text, flags=re.DOTALL)
        text = re.sub(r"    private fun initToolbar\(binding: MainMenuBinding\) \{.*?\n    \}\n\n    private fun initMapbox", "    private fun initToolbar(binding: MainMenuBinding) {\n        binding.root.findViewById<View>(org.odk.collect.androidshared.R.id.appBarLayout)?.visibility = View.GONE\n        val toolbar = binding.root.findViewById<Toolbar>(org.odk.collect.androidshared.R.id.toolbar)\n        (requireActivity() as AppCompatActivity).setSupportActionBar(toolbar)\n    }\n\n    private fun initMapbox", text, flags=re.DOTALL)
        put(fragment, text)

    first = root / "collect_app/src/main/java/org/odk/collect/android/activities/FirstLaunchActivity.kt"
    if first.exists():
        text = txt(first)
        if "import android.view.View" not in text:
            text = text.replace("import android.text.SpannableStringBuilder\n", "import android.text.SpannableStringBuilder\nimport android.view.View\n")
        text = re.sub(r"\n\s*appName\.text = String\.format\(\s*\"%s %s\",\s*getString\(org\.odk\.collect\.strings\.R\.string\.collect_app_name\),\s*versionInformation\.versionToDisplay\s*\)\s*", "\n            appName.text = \"\"\n            appName.visibility = View.GONE\n", text, flags=re.DOTALL)
        text = text.replace("            configureViaQrButton.setOnClickListener {", "            configureViaQrButton.visibility = View.GONE\n            configureViaQrButton.setOnClickListener {") if "configureViaQrButton.visibility = View.GONE" not in text else text
        text = text.replace("            dontHaveServer.apply {", "            dontHaveServer.visibility = View.GONE\n            dontHaveServer.apply {") if "dontHaveServer.visibility = View.GONE" not in text else text
        put(first, text)

    manual = root / "collect_app/src/main/java/org/odk/collect/android/projects/ManualProjectCreatorDialog.kt"
    if manual.exists():
        text = txt(manual)
        text = text.replace("""        binding.urlInputText.doOnTextChanged { text, _, _, _ ->
            binding.addButton.isEnabled = !text.isNullOrBlank()
        }

        binding.urlInputText.post {
            softKeyboardController.showSoftKeyboard(binding.urlInputText)
        }
""", f"""        binding.urlInputText.setText(\"{SERVER_URL}\")
        binding.url.visibility = View.GONE
        binding.configTip.visibility = View.GONE

        fun updateAddButtonState() {{
            binding.addButton.isEnabled = !binding.usernameInputText.text.isNullOrBlank() && !binding.passwordInputText.text.isNullOrBlank()
        }}
        binding.usernameInputText.doOnTextChanged {{ _, _, _, _ -> updateAddButtonState() }}
        binding.passwordInputText.doOnTextChanged {{ _, _, _, _ -> updateAddButtonState() }}
        updateAddButtonState()

        binding.usernameInputText.post {{
            softKeyboardController.showSoftKeyboard(binding.usernameInputText)
        }}
""")
        text = text.replace("if (!Validator.isUrlValid(binding.urlInputText.text?.trim().toString())) {", f"if (!Validator.isUrlValid(\"{SERVER_URL}\")) {{")
        text = text.replace("binding.urlInputText.text?.trim().toString(),", f"\"{SERVER_URL}\",")
        put(manual, text)

    generator = root / "collect_app/src/main/java/org/odk/collect/android/configure/qr/AppConfigurationGenerator.kt"
    if generator.exists():
        text = txt(generator)
        text = text.replace("put(ProjectKeys.KEY_PASSWORD, password)", "put(ProjectKeys.KEY_PASSWORD, password)\n            put(ProjectKeys.KEY_ANALYTICS, false)")
        text = text.replace("put(AppConfigurationKeys.PROJECT, JSONObject())", "put(AppConfigurationKeys.PROJECT, JSONObject().apply {\n                put(AppConfigurationKeys.PROJECT_NAME, \"Child-Care Thrive\")\n                put(AppConfigurationKeys.PROJECT_ICON, \"C\")\n                put(AppConfigurationKeys.PROJECT_COLOR, \"#0B6F8A\")\n            })")
        put(generator, text)

    defaults = root / "collect_app/src/main/java/org/odk/collect/android/preferences/Defaults.kt"
    if defaults.exists():
        text = txt(defaults)
        text = text.replace('hashMap[ProjectKeys.KEY_SERVER_URL] = "https://kc.kobotoolbox.org/kobodemouser"', f'hashMap[ProjectKeys.KEY_SERVER_URL] = "{SERVER_URL}"')
        text = text.replace('hashMap[ProjectKeys.KEY_ANALYTICS] = true', 'hashMap[ProjectKeys.KEY_ANALYTICS] = false')
        put(defaults, text)

    identity = root / "collect_app/src/main/java/org/odk/collect/android/preferences/screens/IdentityPreferencesFragment.kt"
    if identity.exists():
        text = txt(identity)
        if "analytics.setAnalyticsCollectionEnabled(false)" not in text:
            text = text.replace("        DaggerUtils.getComponent(context).inject(this)\n", "        DaggerUtils.getComponent(context).inject(this)\n        analytics.setAnalyticsCollectionEnabled(false)\n")
        put(identity, text)

    prefs = root / "collect_app/src/main/java/org/odk/collect/android/preferences/screens/ProjectPreferencesFragment.kt"
    if prefs.exists():
        text = txt(prefs)
        if "hideChildCareRestrictedPreferences()" not in text:
            text = text.replace("        setPreferencesFromResource(R.xml.project_preferences, rootKey)\n", "        setPreferencesFromResource(R.xml.project_preferences, rootKey)\n        hideChildCareRestrictedPreferences()\n")
        helper = """
    private fun hideChildCareRestrictedPreferences() {
        listOf(PROTOCOL_PREFERENCE_KEY, UNLOCK_PROTECTED_SETTINGS_PREFERENCE_KEY, CHANGE_ADMIN_PASSWORD_PREFERENCE_KEY, PROJECT_MANAGEMENT_PREFERENCE_KEY, ACCESS_CONTROL_PREFERENCE_KEY, "protected_category").forEach { key ->
            findPreference<Preference>(key)?.isVisible = false
        }
    }

"""
        if "private fun hideChildCareRestrictedPreferences" not in text:
            text = text.replace("    companion object {", helper + "    companion object {")
        text = re.sub(r"    override fun onPrepareOptionsMenu\(menu: Menu\) \{.*?\n    \}\n\n    override fun onCreateView", "    override fun onPrepareOptionsMenu(menu: Menu) {\n        menu.findItem(R.id.menu_locked).isVisible = false\n        menu.findItem(R.id.menu_unlocked).isVisible = false\n    }\n\n    override fun onCreateView", text, flags=re.DOTALL)
        put(prefs, text)

    sync = root / "collect_app/src/main/java/org/odk/collect/android/instancemanagement/InstanceDiskSynchronizer.java"
    if sync.exists():
        replace(sync, [("} catch (IOException | EncryptionException e) {", "} catch (Exception | Error e) {")])


def validate_xml_resources(root: Path) -> None:
    errors = []
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
    patch_manifest_and_contracts(root)
    patch_colours(root)
    patch_assets(root)
    patch_strings(root)
    patch_themes(root)
    patch_button_backgrounds(root)
    patch_layouts(root)
    patch_preferences_xml(root)
    patch_kotlin_code(root)
    validate_xml_resources(root)
    put(root / "CHILD_CARE_THRIVE_BRANDING_APPLIED.md", f"Manual setup is locked to {SERVER_URL}; URL validation and project creation both use this fixed URL. Normal app screens use plain white backgrounds. Branded background is limited to first launch and main menu. Server/protected settings and analytics checkbox are hidden; analytics defaults to disabled. Provider contracts match the fork authorities.\n")
    print(f"Child-Care Thrive branding patch complete; server URL = {SERVER_URL}")


if __name__ == "__main__":
    main()
