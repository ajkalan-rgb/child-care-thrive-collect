#!/usr/bin/env python3
from pathlib import Path
import shutil

root = Path.cwd()
src = root / "branding/new_background_only.png"
drawable = root / "collect_app/src/main/res/drawable"
layout = root / "collect_app/src/main/res/layout"
values = root / "collect_app/src/main/res/values"
menu_dir = root / "collect_app/src/main/res/menu"

if not src.exists():
    raise SystemExit(f"Missing required app background: {src}")

for p in (drawable, layout, values, menu_dir):
    p.mkdir(parents=True, exist_ok=True)

shutil.copyfile(src, drawable / "child_care_thrive_new_background_only.png")

items = [
    ("enter_data", "StartNewFormButton", None, None, 96),
    ("review_data", "MainMenuButton", "ic_edit_24", "review_data", 96),
    ("send_data", "MainMenuButton", "ic_send_24", "send_data", 97),
    ("view_sent_forms", "MainMenuButton", "ic_check_circle_24", "view_sent_forms", 98),
    ("get_forms", "MainMenuButton", "ic_download_24", "get_forms", 97),
    ("manage_forms", "MainMenuButton", "ic_delete_24", "manage_files", 98),
]
gaps = [28, 28, 28, 28, 27]
children = []
for i, (view_id, cls, icon, label, weight) in enumerate(items):
    attrs = ""
    if icon:
        attrs += f' app:icon="@drawable/{icon}" app:name="@string/{label}"'
    if view_id == "send_data":
        attrs += ' app:highlightable="true"'
    children.append(
        f'<org.odk.collect.android.mainmenu.{cls} android:id="@+id/{view_id}" '
        f'android:layout_width="match_parent" android:layout_height="0dp" '
        f'android:layout_weight="{weight}"{attrs} />'
    )
    if i < len(gaps):
        children.append(
            f'<Space android:layout_width="1dp" android:layout_height="0dp" '
            f'android:layout_weight="{gaps[i]}" />'
        )

main_xml = f'''<?xml version="1.0" encoding="utf-8"?>
<androidx.coordinatorlayout.widget.CoordinatorLayout xmlns:android="http://schemas.android.com/apk/res/android" xmlns:app="http://schemas.android.com/apk/res-auto" xmlns:tools="http://schemas.android.com/tools" android:layout_width="match_parent" android:layout_height="match_parent" android:background="@android:color/white" android:clipChildren="true" android:clipToPadding="true">
<ImageView android:id="@+id/child_care_background" android:layout_width="match_parent" android:layout_height="match_parent" android:contentDescription="@null" android:importantForAccessibility="no" android:scaleType="fitXY" android:src="@drawable/child_care_thrive_new_background_only" />
<androidx.constraintlayout.widget.ConstraintLayout android:layout_width="match_parent" android:layout_height="match_parent">
<androidx.fragment.app.FragmentContainerView android:id="@+id/map_box_initialization_fragment" android:layout_width="1dp" android:layout_height="1dp" android:visibility="gone" app:layout_constraintStart_toStartOf="parent" app:layout_constraintTop_toTopOf="parent" />
<include android:id="@+id/google_drive_deprecation_banner" layout="@layout/google_drive_deprecation_banner" android:layout_width="1dp" android:layout_height="1dp" android:visibility="gone" app:layout_constraintStart_toStartOf="parent" app:layout_constraintTop_toTopOf="parent" />
<androidx.constraintlayout.widget.Guideline android:id="@+id/menu_top" android:layout_width="wrap_content" android:layout_height="wrap_content" android:orientation="horizontal" app:layout_constraintGuide_percent="0.2877604" />
<androidx.constraintlayout.widget.Guideline android:id="@+id/menu_bottom" android:layout_width="wrap_content" android:layout_height="wrap_content" android:orientation="horizontal" app:layout_constraintGuide_percent="0.7571615" />
<LinearLayout android:id="@+id/child_care_menu_stack" android:layout_width="0dp" android:layout_height="0dp" android:orientation="vertical" android:weightSum="721" app:layout_constraintTop_toBottomOf="@id/menu_top" app:layout_constraintBottom_toTopOf="@id/menu_bottom" app:layout_constraintStart_toStartOf="parent" app:layout_constraintEnd_toEndOf="parent" app:layout_constraintWidth_percent="0.53125">
{''.join(children)}
</LinearLayout>
<TextView android:id="@+id/app_name" android:layout_width="1dp" android:layout_height="1dp" android:visibility="gone" tools:text="Child-Care Thrive" />
<TextView android:id="@+id/version_sha" android:layout_width="1dp" android:layout_height="1dp" android:visibility="gone" />
</androidx.constraintlayout.widget.ConstraintLayout>
<include layout="@layout/app_bar_layout" />
</androidx.coordinatorlayout.widget.CoordinatorLayout>
'''

main_button = '''<?xml version="1.0" encoding="utf-8"?>
<androidx.constraintlayout.widget.ConstraintLayout xmlns:android="http://schemas.android.com/apk/res/android" xmlns:app="http://schemas.android.com/apk/res-auto" xmlns:tools="http://schemas.android.com/tools" android:layout_width="match_parent" android:layout_height="match_parent" android:background="@drawable/child_care_main_menu_button_background" android:clipToOutline="true" android:elevation="4dp">
<ImageView android:id="@+id/icon" android:layout_width="28dp" android:layout_height="28dp" android:layout_marginStart="25dp" android:contentDescription="@null" app:layout_constraintBottom_toBottomOf="parent" app:layout_constraintStart_toStartOf="parent" app:layout_constraintTop_toTopOf="parent" app:tint="@android:color/white" tools:src="@drawable/ic_delete_24" />
<TextView android:id="@+id/name" android:layout_width="0dp" android:layout_height="wrap_content" android:layout_marginStart="20dp" android:layout_marginEnd="16dp" android:ellipsize="end" android:fontFamily="sans-serif-medium" android:includeFontPadding="false" android:maxLines="1" android:textColor="@android:color/white" android:textSize="17sp" app:layout_constraintBottom_toBottomOf="parent" app:layout_constraintEnd_toEndOf="parent" app:layout_constraintStart_toEndOf="@id/icon" app:layout_constraintTop_toTopOf="parent" tools:text="Ready to send" />
<TextView android:id="@+id/number" android:layout_width="1dp" android:layout_height="1dp" android:visibility="gone" app:layout_constraintEnd_toEndOf="parent" app:layout_constraintTop_toTopOf="parent" />
</androidx.constraintlayout.widget.ConstraintLayout>
'''

start_button = main_button.replace("child_care_main_menu_button_background", "child_care_start_menu_button_background").replace('tools:text="Ready to send"', 'android:text="@string/enter_data"').replace('<TextView android:id="@+id/number" android:layout_width="1dp" android:layout_height="1dp" android:visibility="gone" app:layout_constraintEnd_toEndOf="parent" app:layout_constraintTop_toTopOf="parent" />', '').replace('tools:src="@drawable/ic_delete_24"', 'android:src="@drawable/ic_add_white_24"')

(layout / "main_menu.xml").write_text(main_xml, encoding="utf-8")
(layout / "main_menu_button.xml").write_text(main_button, encoding="utf-8")
(layout / "start_new_from_button.xml").write_text(start_button, encoding="utf-8")
(drawable / "child_care_main_menu_button_background.xml").write_text('<?xml version="1.0" encoding="utf-8"?><shape xmlns:android="http://schemas.android.com/apk/res/android" android:shape="rectangle"><solid android:color="#00266A"/><corners android:radius="24dp"/></shape>', encoding="utf-8")
(drawable / "child_care_start_menu_button_background.xml").write_text('<?xml version="1.0" encoding="utf-8"?><shape xmlns:android="http://schemas.android.com/apk/res/android" android:shape="rectangle"><solid android:color="#00ADB3"/><corners android:radius="24dp"/></shape>', encoding="utf-8")
(values / "child_care_main_menu_strings.xml").write_text('<?xml version="1.0" encoding="utf-8"?><resources><string name="enter_data">Start new form</string><string name="review_data">Drafts</string><string name="send_data">Ready to send</string><string name="view_sent_forms">Sent</string><string name="get_forms">Download form</string><string name="manage_files">Delete form</string></resources>', encoding="utf-8")
(menu_dir / "main_menu.xml").write_text('<?xml version="1.0" encoding="utf-8"?><menu xmlns:android="http://schemas.android.com/apk/res/android" xmlns:app="http://schemas.android.com/apk/res-auto"><item android:id="@+id/projects" android:icon="@drawable/ic_outline_settings_accent_24" android:title="@string/project_settings" app:showAsAction="always"/></menu>', encoding="utf-8")
print("Applied new_background_only.png with approved exact main-menu positioning")
