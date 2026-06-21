#!/usr/bin/env python3
from pathlib import Path
import shutil

ROOT = Path.cwd()
SRC = ROOT / "branding/new_only_startup_screen.png"
DRAWABLE = ROOT / "collect_app/src/main/res/drawable"
LAYOUT = ROOT / "collect_app/src/main/res/layout/first_launch_layout.xml"
NAME = "child_care_thrive_new_only_startup"
REF = f"@drawable/{NAME}"

XML = f'''<?xml version="1.0" encoding="utf-8"?>
<androidx.constraintlayout.widget.ConstraintLayout xmlns:android="http://schemas.android.com/apk/res/android" xmlns:app="http://schemas.android.com/apk/res-auto" android:layout_width="match_parent" android:layout_height="match_parent" android:background="@android:color/white" android:clipChildren="true" android:clipToPadding="true">
    <ImageView android:id="@+id/startup_background" android:layout_width="0dp" android:layout_height="0dp" android:contentDescription="@null" android:scaleType="fitXY" android:src="{REF}" app:layout_constraintTop_toTopOf="parent" app:layout_constraintBottom_toBottomOf="parent" app:layout_constraintStart_toStartOf="parent" app:layout_constraintEnd_toEndOf="parent" />
    <androidx.constraintlayout.widget.Guideline android:id="@+id/configure_band_top" android:layout_width="wrap_content" android:layout_height="wrap_content" android:orientation="horizontal" app:layout_constraintGuide_percent="0.575" />
    <androidx.constraintlayout.widget.Guideline android:id="@+id/configure_band_bottom" android:layout_width="wrap_content" android:layout_height="wrap_content" android:orientation="horizontal" app:layout_constraintGuide_percent="0.765" />
    <LinearLayout android:id="@+id/center" android:layout_width="0dp" android:layout_height="wrap_content" android:layout_marginStart="24dp" android:layout_marginEnd="24dp" android:gravity="center_horizontal" android:orientation="vertical" app:layout_constraintTop_toBottomOf="@id/configure_band_top" app:layout_constraintBottom_toTopOf="@id/configure_band_bottom" app:layout_constraintStart_toStartOf="parent" app:layout_constraintEnd_toEndOf="parent" app:layout_constraintVertical_bias="0.5">
        <ImageView android:id="@+id/logo" android:layout_width="1dp" android:layout_height="1dp" android:contentDescription="@null" android:visibility="gone" />
        <TextView android:id="@+id/tagline" android:layout_width="match_parent" android:layout_height="wrap_content" android:fontFamily="sans-serif-medium" android:gravity="center" android:includeFontPadding="false" android:maxLines="1" android:text="@string/tagline" android:textColor="@color/child_care_text_primary" android:textSize="24sp" />
        <org.odk.collect.androidshared.ui.multiclicksafe.MultiClickSafeMaterialButton android:id="@+id/configure_via_qr_button" style="?materialButtonIconStyle" android:layout_width="1dp" android:layout_height="1dp" android:text="@string/configure_with_qr_code" android:visibility="gone" app:icon="@drawable/ic_baseline_qr_code_scanner_24" />
        <org.odk.collect.androidshared.ui.multiclicksafe.MultiClickSafeMaterialButton android:id="@+id/configure_manually_button" style="?materialButtonOutlinedIconStyle" android:layout_width="match_parent" android:layout_height="54dp" android:layout_marginTop="12dp" android:gravity="center" android:maxLines="1" android:minHeight="54dp" android:paddingStart="18dp" android:paddingEnd="18dp" android:text="@string/configure_manually" android:textAllCaps="false" android:textColor="@color/child_care_text_primary" app:autoSizeMaxTextSize="16sp" app:autoSizeMinTextSize="12sp" app:autoSizeStepGranularity="1sp" app:autoSizeTextType="uniform" app:cornerRadius="27dp" app:icon="@drawable/ic_outline_edit_24" app:iconPadding="12dp" app:iconTint="@color/child_care_text_primary" app:strokeColor="@color/child_care_text_primary" app:strokeWidth="1dp" />
    </LinearLayout>
    <TextView android:id="@+id/app_name" android:layout_width="1dp" android:layout_height="1dp" android:visibility="gone" app:layout_constraintStart_toStartOf="parent" app:layout_constraintTop_toTopOf="parent" />
    <TextView android:id="@+id/dont_have_server" android:layout_width="1dp" android:layout_height="1dp" android:visibility="gone" app:layout_constraintStart_toStartOf="parent" app:layout_constraintTop_toTopOf="parent" />
</androidx.constraintlayout.widget.ConstraintLayout>
'''

if not SRC.exists():
    raise SystemExit(f"Missing required startup asset: {SRC}")
DRAWABLE.mkdir(parents=True, exist_ok=True)
shutil.copyfile(SRC, DRAWABLE / f"{NAME}.png")
(DRAWABLE / "child_care_thrive_startup_background.xml").write_text(f'''<?xml version="1.0" encoding="utf-8"?>
<layer-list xmlns:android="http://schemas.android.com/apk/res/android"><item android:drawable="@android:color/white"/><item><bitmap android:src="{REF}" android:gravity="fill"/></item></layer-list>
''', encoding="utf-8")
LAYOUT.write_text(XML, encoding="utf-8")
print("Applied new_only_startup_screen.png with contained configure controls")
