# Child-Care Thrive Collect

Android source-build wrapper for the **Child-Care Thrive** branded KoboCollect fork.

Branding target:

- App name: **Child-Care Thrive**
- Package ID: `za.co.childcarethrive.collect`
- Branding line: **Child-Care Thrive powered by HIV Survivors & Partners Network**
- Field engine: KoboCollect / ODK Collect open-source technology
- App menu background: safe-zone Child-Care Thrive asset under `branding/`

This repository is intentionally lightweight. The GitHub Actions workflow clones the official KoboCollect source, applies the Child-Care Thrive branding patch, and attempts to build a signed debug APK artifact.

## Build

Open **Actions → Build Child-Care Thrive APK → Run workflow**, or push to `main`.

The APK artifact, if the build succeeds, will be available under the workflow run artifacts.

## Important

This is a source-level build route, not the failed compiled-APK patch route. It should create a real launcher app with a separate package ID and proper Android build metadata.

Do not store production signing keys, Kobo credentials, API keys, or patient/client data in this repository.
