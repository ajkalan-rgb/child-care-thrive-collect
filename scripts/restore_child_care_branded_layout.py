#!/usr/bin/env python3
from pathlib import Path
import shutil

root = Path.cwd()

def write(path: str, text: str) -> None:
    p = root / path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")

startup_drawable = "@drawable/child_care_thrive_startup"
branding = root / "branding"
drawable = root / "collect_app/src/main/res/drawable"
if branding.exists():
    for asset in sorted(branding.iterdir()):
        name = asset.name.lower().replace("-", "_").replace(" ", "_")
        if asset.is_file() and name.startswith("child_care_kobocollect") and asset.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp"}:
            ext = ".jpg" if asset.suffix.lower() == ".jpeg" else asset.suffix.lower()
            target = drawable / f"child_care_thrive_kobocollect{ext}"
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(asset, target)
            startup_drawable = "@drawable/child_care_thrive_kobocollect"
            print(f"First-launch image asset: {asset} -> {target}")
            break

main_menu = '''<?xml version="1.0" encoding="utf-8"?>
<androidx.coordinatorlayout.widget.CoordinatorLayout xmlns:android="http://schemas.android.com/apk/res/android" xmlns:app="http://schemas.android.com/apk/res-auto" xmlns:tools="http://schemas.android.com/tools" android:layout_width="match_parent" android:layout_height="match_parent" android:background="@android:color/white">
    <ImageView android:id="@+id/child_care_background" android:layout_width="match_parent" android:layout_height="match_parent" android:contentDescription="@null" android:importantForAccessibility="no" android:scaleType="fitCenter" android:src="@drawable/child_care_thrive_app_background_image" />
    <include layout="@layout/app_bar_layout" />
    <androidx.core.widget.NestedScrollView android:layout_width="match_parent" android:layout_height="match_parent" android:background="@android:color/transparent" android:fillViewport="true" app:layout_behavior="@string/appbar_scrolling_view_behavior">
        <androidx.constraintlayout.widget.ConstraintLayout android:layout_width="match_parent" android:layout_height="match_parent" android:minHeight="620dp" android:paddingBottom="@dimen/margin_standard">
            <androidx.fragment.app.FragmentContainerView android:id="@+id/map_box_initialization_fragment" android:layout_width="match_parent" android:layout_height="1dp" app:layout_constraintEnd_toEndOf="parent" app:layout_constraintStart_toStartOf="parent" app:layout_constraintTop_toTopOf="parent" />
            <include android:id="@+id/google_drive_deprecation_banner" layout="@layout/google_drive_deprecation_banner" android:layout_width="match_parent" android:layout_height="0dp" android:visibility="gone" app:layout_constraintEnd_toEndOf="parent" app:layout_constraintStart_toStartOf="parent" app:layout_constraintTop_toBottomOf="@id/map_box_initialization_fragment" />
            <LinearLayout android:id="@+id/child_care_menu_stack" android:layout_width="0dp" android:layout_height="wrap_content" android:layout_marginHorizontal="24dp" android:layout_marginTop="150dp" android:orientation="vertical" app:layout_constraintEnd_toEndOf="parent" app:layout_constraintStart_toStartOf="parent" app:layout_constraintTop_toTopOf="parent" app:layout_constraintWidth_max="@dimen/max_content_width">
                <org.odk.collect.android.mainmenu.StartNewFormButton android:id="@+id/enter_data" android:layout_width="match_parent" android:layout_height="wrap_content" />
                <org.odk.collect.android.mainmenu.MainMenuButton android:id="@+id/review_data" android:layout_width="match_parent" android:layout_height="wrap_content" app:icon="@drawable/ic_edit_24" app:name="@string/review_data" />
                <org.odk.collect.android.mainmenu.MainMenuButton android:id="@+id/send_data" android:layout_width="match_parent" android:layout_height="wrap_content" app:highlightable="true" app:icon="@drawable/ic_send_24" app:name="@string/send_data" />
                <org.odk.collect.android.mainmenu.MainMenuButton android:id="@+id/view_sent_forms" android:layout_width="match_parent" android:layout_height="wrap_content" app:icon="@drawable/ic_check_circle_24" app:name="@string/view_sent_forms" />
                <org.odk.collect.android.mainmenu.MainMenuButton android:id="@+id/get_forms" android:layout_width="match_parent" android:layout_height="wrap_content" app:icon="@drawable/ic_download_24" app:name="@string/get_forms" />
                <org.odk.collect.android.mainmenu.MainMenuButton android:id="@+id/manage_forms" android:layout_width="match_parent" android:layout_height="wrap_content" app:icon="@drawable/ic_delete_24" app:name="@string/manage_files" />
            </LinearLayout>
            <TextView android:id="@+id/app_name" android:layout_width="0dp" android:layout_height="0dp" android:visibility="gone" tools:text="Child-Care Thrive" />
            <TextView android:id="@+id/version_sha" android:layout_width="0dp" android:layout_height="0dp" android:visibility="gone" />
        </androidx.constraintlayout.widget.ConstraintLayout>
    </androidx.core.widget.NestedScrollView>
</androidx.coordinatorlayout.widget.CoordinatorLayout>
'''
write("collect_app/src/main/res/layout/main_menu.xml", main_menu)

# Restore first-launch/manual-login screen structure. Only the logo image changes to child_care_kobocollect; login/manual flow remains intact.
first_launch = f'''<?xml version="1.0" encoding="utf-8"?>
<ScrollView xmlns:android="http://schemas.android.com/apk/res/android" xmlns:app="http://schemas.android.com/apk/res-auto" xmlns:tools="http://schemas.android.com/tools" android:layout_width="match_parent" android:layout_height="match_parent" android:fillViewport="true" android:background="@android:color/white">
    <androidx.constraintlayout.widget.ConstraintLayout android:layout_width="match_parent" android:layout_height="wrap_content">
        <androidx.constraintlayout.widget.ConstraintLayout android:id="@+id/center" android:layout_width="wrap_content" android:layout_height="wrap_content" android:layout_marginHorizontal="@dimen/margin_large" android:paddingHorizontal="@dimen/margin_large" app:layout_constraintBottom_toBottomOf="parent" app:layout_constraintEnd_toEndOf="parent" app:layout_constraintStart_toStartOf="parent" app:layout_constraintTop_toTopOf="parent" app:layout_constraintVertical_bias="0.5">
            <ImageView android:id="@+id/logo" android:layout_width="160dp" android:layout_height="wrap_content" android:adjustViewBounds="true" android:contentDescription="@string/collect_app_name" android:src="{startup_drawable}" app:layout_constraintStart_toStartOf="parent" app:layout_constraintEnd_toEndOf="parent" app:layout_constraintTop_toTopOf="parent" />
            <TextView android:id="@+id/tagline" android:layout_width="wrap_content" android:layout_height="wrap_content" android:layout_marginTop="@dimen/margin_extra_small" android:text="Configure project" android:textAppearance="?textAppearanceHeadline4" android:textColor="@color/child_care_text_primary" app:layout_constraintEnd_toEndOf="parent" app:layout_constraintStart_toStartOf="parent" app:layout_constraintTop_toBottomOf="@id/logo" />
            <org.odk.collect.androidshared.ui.multiclicksafe.MultiClickSafeMaterialButton android:id="@+id/configure_via_qr_button" style="?materialButtonIconStyle" android:layout_width="0dp" android:layout_height="0dp" android:visibility="gone" android:text="@string/configure_with_qr_code" app:icon="@drawable/ic_baseline_qr_code_scanner_24" app:layout_constraintTop_toBottomOf="@id/tagline" app:layout_constraintEnd_toEndOf="@id/barrierEnd" app:layout_constraintStart_toStartOf="parent" />
            <org.odk.collect.androidshared.ui.multiclicksafe.MultiClickSafeMaterialButton android:id="@+id/configure_manually_button" style="?materialButtonOutlinedIconStyle" android:layout_width="0dp" android:layout_height="wrap_content" android:layout_marginTop="@dimen/margin_standard" android:text="@string/configure_manually" app:icon="@drawable/ic_outline_edit_24" app:layout_constraintEnd_toEndOf="@id/barrierEnd" app:layout_constraintStart_toStartOf="parent" app:layout_constraintTop_toBottomOf="@id/tagline" app:layout_constraintWidth_min="wrap" />
            <androidx.constraintlayout.widget.Barrier android:id="@+id/barrierEnd" android:layout_width="0dp" android:layout_height="0dp" app:barrierDirection="end" app:constraint_referenced_ids="configure_via_qr_button,configure_manually_button" app:layout_constraintStart_toStartOf="parent" app:layout_constraintTop_toTopOf="parent" />
        </androidx.constraintlayout.widget.ConstraintLayout>
        <TextView android:id="@+id/app_name" android:layout_width="0dp" android:layout_height="0dp" android:visibility="gone" />
        <TextView android:id="@+id/dont_have_server" android:layout_width="0dp" android:layout_height="0dp" android:visibility="gone" />
    </androidx.constraintlayout.widget.ConstraintLayout>
</ScrollView>
'''
write("collect_app/src/main/res/layout/first_launch_layout.xml", first_launch)

for name in ["main_menu_button.xml", "start_new_from_button.xml"]:
    p = root / "collect_app/src/main/res/layout" / name
    if p.exists():
        s = p.read_text(encoding="utf-8")
        s = s.replace('android:layout_marginVertical="2dp"', 'android:layout_marginVertical="5dp"')
        s = s.replace('android:layout_marginHorizontal="42dp"', 'android:layout_marginHorizontal="24dp"')
        s = s.replace('android:layout_marginHorizontal="@dimen/margin_standard"', 'android:layout_marginHorizontal="24dp"')
        p.write_text(s, encoding="utf-8")

# If an APK is installed over an older development build, a current project can already exist with no saved username/password.
# In that case KoboCollect skips FirstLaunchActivity and lands on MainMenuActivity. Force it back to setup until credentials exist.
main_activity = root / "collect_app/src/main/java/org/odk/collect/android/mainmenu/MainMenuActivity.kt"
if main_activity.exists():
    s = main_activity.read_text(encoding="utf-8")
    if "import org.odk.collect.settings.keys.ProjectKeys" not in s:
        s = s.replace("import org.odk.collect.settings.SettingsProvider\n", "import org.odk.collect.settings.SettingsProvider\nimport org.odk.collect.settings.keys.ProjectKeys\n")
    old = """        if (!currentProjectViewModel.hasCurrentProject()) {
            super.onCreate(null)
            ActivityUtils.startActivityAndCloseAllOthers(this, FirstLaunchActivity::class.java)
            return
        } else {
"""
    new = """        if (!currentProjectViewModel.hasCurrentProject()) {
            super.onCreate(null)
            ActivityUtils.startActivityAndCloseAllOthers(this, FirstLaunchActivity::class.java)
            return
        } else if (!hasServerCredentials()) {
            super.onCreate(null)
            ActivityUtils.startActivityAndCloseAllOthers(this, FirstLaunchActivity::class.java)
            return
        } else {
"""
    s = s.replace(old, new)
    if "private fun hasServerCredentials()" not in s:
        s = s.replace("\n    private fun initSplashScreen() {", """
    private fun hasServerCredentials(): Boolean {
        val settings = settingsProvider.getUnprotectedSettings()
        return !settings.getString(ProjectKeys.KEY_USERNAME).isNullOrBlank() &&
            !settings.getString(ProjectKeys.KEY_PASSWORD).isNullOrBlank()
    }

    private fun initSplashScreen() {""")
    main_activity.write_text(s, encoding="utf-8")

first_activity = root / "collect_app/src/main/java/org/odk/collect/android/activities/FirstLaunchActivity.kt"
if first_activity.exists():
    s = first_activity.read_text(encoding="utf-8")
    if "import org.odk.collect.settings.keys.ProjectKeys" not in s:
        s = s.replace("import org.odk.collect.settings.SettingsProvider\n", "import org.odk.collect.settings.SettingsProvider\nimport org.odk.collect.settings.keys.ProjectKeys\n")
    s = s.replace("if (currentProject != null) {", "if (currentProject != null && hasServerCredentials()) {")
    if "private fun hasServerCredentials()" not in s:
        s = s.replace("\n}\n\nprivate class FirstLaunchViewModel", """

    private fun hasServerCredentials(): Boolean {
        val settings = settingsProvider.getUnprotectedSettings()
        return !settings.getString(ProjectKeys.KEY_USERNAME).isNullOrBlank() &&
            !settings.getString(ProjectKeys.KEY_PASSWORD).isNullOrBlank()
    }
}

private class FirstLaunchViewModel""")
    first_activity.write_text(s, encoding="utf-8")

print(f"Child-Care Thrive layout applied: first-launch/manual login restored; first-launch image uses {startup_drawable}; main menu redirects to first launch until username/password exist.")
