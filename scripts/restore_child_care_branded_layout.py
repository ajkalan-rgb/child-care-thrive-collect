#!/usr/bin/env python3
from pathlib import Path

root = Path.cwd()

def write(path: str, text: str) -> None:
    p = root / path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")

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

first_launch = '''<?xml version="1.0" encoding="utf-8"?>
<androidx.constraintlayout.widget.ConstraintLayout xmlns:android="http://schemas.android.com/apk/res/android" xmlns:app="http://schemas.android.com/apk/res-auto" xmlns:tools="http://schemas.android.com/tools" android:layout_width="match_parent" android:layout_height="match_parent" android:background="@android:color/white">
    <ImageView android:id="@+id/child_care_startup_background" android:layout_width="0dp" android:layout_height="0dp" android:contentDescription="@null" android:importantForAccessibility="no" android:scaleType="fitCenter" android:src="@drawable/child_care_thrive_startup" app:layout_constraintBottom_toBottomOf="parent" app:layout_constraintEnd_toEndOf="parent" app:layout_constraintStart_toStartOf="parent" app:layout_constraintTop_toTopOf="parent" />
    <androidx.constraintlayout.widget.ConstraintLayout android:id="@+id/center" android:layout_width="0dp" android:layout_height="wrap_content" android:layout_marginHorizontal="32dp" app:layout_constraintBottom_toBottomOf="parent" app:layout_constraintEnd_toEndOf="parent" app:layout_constraintStart_toStartOf="parent" app:layout_constraintTop_toTopOf="parent" app:layout_constraintVertical_bias="0.54">
        <ImageView android:id="@+id/logo" android:layout_width="0dp" android:layout_height="0dp" android:contentDescription="@string/collect_app_name" android:visibility="gone" />
        <TextView android:id="@+id/tagline" android:layout_width="wrap_content" android:layout_height="wrap_content" android:text="Configure project" android:textAppearance="?textAppearanceHeadline4" android:textColor="@color/child_care_text_primary" app:layout_constraintEnd_toEndOf="parent" app:layout_constraintStart_toStartOf="parent" app:layout_constraintTop_toTopOf="parent" />
        <org.odk.collect.androidshared.ui.multiclicksafe.MultiClickSafeMaterialButton android:id="@+id/configure_via_qr_button" style="?materialButtonIconStyle" android:layout_width="0dp" android:layout_height="0dp" android:text="@string/configure_with_qr_code" android:visibility="gone" app:icon="@drawable/ic_baseline_qr_code_scanner_24" />
        <org.odk.collect.androidshared.ui.multiclicksafe.MultiClickSafeMaterialButton android:id="@+id/configure_manually_button" style="?materialButtonOutlinedIconStyle" android:layout_width="0dp" android:layout_height="wrap_content" android:layout_marginTop="40dp" android:text="@string/configure_manually" app:icon="@drawable/ic_outline_edit_24" app:layout_constraintEnd_toEndOf="parent" app:layout_constraintStart_toStartOf="parent" app:layout_constraintTop_toBottomOf="@id/tagline" />
        <androidx.constraintlayout.widget.Barrier android:id="@+id/barrierEnd" android:layout_width="0dp" android:layout_height="0dp" app:barrierDirection="end" app:constraint_referenced_ids="configure_via_qr_button,configure_manually_button" />
    </androidx.constraintlayout.widget.ConstraintLayout>
    <TextView android:id="@+id/app_name" android:layout_width="0dp" android:layout_height="0dp" android:visibility="gone" tools:text="Child-Care Thrive" />
    <TextView android:id="@+id/dont_have_server" android:layout_width="0dp" android:layout_height="0dp" android:visibility="gone" />
</androidx.constraintlayout.widget.ConstraintLayout>
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

print("Child-Care Thrive branded layout applied: startup uses child_care_startup; main menu uses Updated_background; Start new form begins just below the roof apex.")
