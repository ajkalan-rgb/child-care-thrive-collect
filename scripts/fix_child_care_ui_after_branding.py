#!/usr/bin/env python3
from pathlib import Path
import re

ROOT = Path.cwd()

def read(path: str) -> str:
    return (ROOT / path).read_text(encoding='utf-8')

def write(path: str, text: str) -> None:
    p = ROOT / path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding='utf-8')

# 1) Stop using the full artwork as a startup/config background. It causes cropped logos and the duplicate ribbon.
startup_bg = '''<?xml version="1.0" encoding="utf-8"?>
<layer-list xmlns:android="http://schemas.android.com/apk/res/android">
    <item android:drawable="@android:color/white" />
</layer-list>
'''
write('collect_app/src/main/res/drawable/child_care_thrive_startup_background.xml', startup_bg)

# 2) Main menu keeps the branded background but masks the duplicate lower ribbon area from the bad asset.
main_menu_bg = '''<?xml version="1.0" encoding="utf-8"?>
<layer-list xmlns:android="http://schemas.android.com/apk/res/android">
    <item android:drawable="@android:color/white" />
    <item>
        <bitmap android:src="@drawable/child_care_thrive_app_background_image" android:gravity="fill" />
    </item>
    <item android:top="700dp">
        <shape android:shape="rectangle">
            <solid android:color="@android:color/white" />
        </shape>
    </item>
</layer-list>
'''
write('collect_app/src/main/res/drawable/child_care_thrive_main_menu_background.xml', main_menu_bg)

# 3) Keep functional startup/config screen clean and readable.
first_layout = Path('collect_app/src/main/res/layout/first_launch_layout.xml')
if first_layout.exists():
    s = read(str(first_layout))
    s = s.replace('@drawable/child_care_thrive_app_background', '@android:color/white')
    s = s.replace('@drawable/child_care_thrive_startup_background', '@android:color/white')
    write(str(first_layout), s)

# 4) Main menu: background and button stack placement.
main_layout = Path('collect_app/src/main/res/layout/main_menu.xml')
if main_layout.exists():
    s = read(str(main_layout))
    s = s.replace('@drawable/child_care_thrive_app_background', '@drawable/child_care_thrive_main_menu_background')
    s = re.sub(r'android:layout_marginTop="(?:@dimen/margin_extra_small|\d+dp)"', 'android:layout_marginTop="260dp"', s, count=1)
    write(str(main_layout), s)

for layout_name in ['main_menu_button.xml', 'start_new_from_button.xml']:
    p = Path('collect_app/src/main/res/layout') / layout_name
    if p.exists():
        s = read(str(p))
        s = s.replace('android:layout_marginHorizontal="42dp"', 'android:layout_marginHorizontal="24dp"')
        s = s.replace('android:layout_marginHorizontal="@dimen/margin_standard"', 'android:layout_marginHorizontal="24dp"')
        s = s.replace('android:layout_marginStart="24dp"', 'android:layout_marginStart="20dp"')
        s = s.replace('android:layout_marginEnd="24dp"', 'android:layout_marginEnd="20dp"')
        write(str(p), s)

# 5) Project settings: only safe sections visible; restricted items kept as hidden placeholders so Kotlin lookups don't crash.
project_preferences_xml = '''<?xml version="1.0" encoding="utf-8"?>
<PreferenceScreen xmlns:android="http://schemas.android.com/apk/res/android">

    <Preference
        android:icon="@drawable/ic_outline_color_lens_accent_24"
        android:key="project_display"
        android:title="@string/project_display_title"
        android:summary="@string/project_display_subtext" />

    <Preference
        android:icon="@drawable/ic_outline_phonelink_setup_accent_24"
        android:key="user_interface"
        android:title="@string/client"
        android:summary="@string/user_interface_settings_subtext" />

    <Preference
        android:icon="@drawable/ic_outline_map_accent_24"
        android:key="maps"
        android:title="@string/maps"
        android:summary="@string/maps_settings_subtext" />

    <Preference
        android:icon="@drawable/ic_outline_assignment_accent_24"
        android:key="form_management"
        android:title="@string/form_management_preferences"
        android:summary="@string/form_management_settings_subtext" />

    <Preference android:key="protocol" android:visible="false" />
    <Preference android:key="user_and_device_identity" android:visible="false" />
    <Preference android:key="experimental" android:visible="false" />
    <Preference android:key="unlock_protected_settings" android:visible="false" />
    <Preference android:key="admin_password" android:visible="false" />
    <Preference android:key="project_management" android:visible="false" />
    <Preference android:key="access_control" android:visible="false" />
    <PreferenceCategory android:key="protected_category" android:title="@string/protected_settings" android:visible="false" />
</PreferenceScreen>
'''
write('collect_app/src/main/res/xml/project_preferences.xml', project_preferences_xml)

# 6) Access Control and protected user settings must not expose server/analytics controls.
write('collect_app/src/main/res/xml/access_control_preferences.xml', '''<?xml version="1.0" encoding="utf-8"?>
<PreferenceScreen xmlns:android="http://schemas.android.com/apk/res/android" android:title="@string/access_control_section_title" />
''')
user_access = Path('collect_app/src/main/res/xml/user_settings_access_preferences.xml')
if user_access.exists():
    s = read(str(user_access))
    for key in ['change_server', 'analytics']:
        s = re.sub(r'\n\s*<CheckBoxPreference\b(?=[^>]*android:key="' + re.escape(key) + r'")[^>]*/>', '', s, flags=re.DOTALL)
    write(str(user_access), s)

# 7) Harden the ProjectPreferencesFragment so restricted rows never come back after visibility-state refresh.
prefs = Path('collect_app/src/main/java/org/odk/collect/android/preferences/screens/ProjectPreferencesFragment.kt')
if prefs.exists():
    s = read(str(prefs))
    if 'private fun hideChildCareRestrictedPreferences' not in s:
        helper = '''
    private fun hideChildCareRestrictedPreferences() {
        listOf(
            PROTOCOL_PREFERENCE_KEY,
            USER_AND_DEVICE_IDENTITY_PREFERENCE_KEY,
            EXPERIMENTAL_PREFERENCE_KEY,
            UNLOCK_PROTECTED_SETTINGS_PREFERENCE_KEY,
            CHANGE_ADMIN_PASSWORD_PREFERENCE_KEY,
            PROJECT_MANAGEMENT_PREFERENCE_KEY,
            ACCESS_CONTROL_PREFERENCE_KEY,
            "protected_category"
        ).forEach { key ->
            findPreference<Preference>(key)?.isVisible = false
        }
    }

'''
        s = s.replace('    companion object {', helper + '    companion object {')
    s = s.replace('''                    preferenceVisibilityHandler.updatePreferencesVisibility(preferenceScreen, state.value)
                    requireActivity().invalidateOptionsMenu()''', '''                    preferenceVisibilityHandler.updatePreferencesVisibility(preferenceScreen, state.value)
                    hideChildCareRestrictedPreferences()
                    requireActivity().invalidateOptionsMenu()''')
    s = s.replace('''        setPreferencesFromResource(R.xml.project_preferences, rootKey)

        findPreference<Preference>(PROTOCOL_PREFERENCE_KEY)!!''', '''        setPreferencesFromResource(R.xml.project_preferences, rootKey)
        hideChildCareRestrictedPreferences()

        findPreference<Preference>(PROTOCOL_PREFERENCE_KEY)!!''')
    s = re.sub(
        r'    override fun onPrepareOptionsMenu\(menu: Menu\) \{.*?\n    \}\n\n    override fun onCreateView',
        '    override fun onPrepareOptionsMenu(menu: Menu) {\n        menu.findItem(R.id.menu_locked).isVisible = false\n        menu.findItem(R.id.menu_unlocked).isVisible = false\n    }\n\n    override fun onCreateView',
        s,
        flags=re.DOTALL,
    )
    write(str(prefs), s)

print('Applied final Child-Care Thrive UI cleanup: white startup/config, cleaned main-menu background, lower button stack, safe settings only.')
