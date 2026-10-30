# PySide6 Android Example

A small PySide6 Widgets app based on [project-template](https://github.com/Cutleast/project-template) and [cutleast-core-lib](https://github.com/Cutleast/cutleast-core-lib) to try out how PySide6 apps work on Android devices.

The app shows some system information, a counter, a to-do list, a slider and lets you switch between light and dark mode. It runs unchanged on the desktop.

## Running on the Desktop

Requirements: [uv](https://docs.astral.sh/uv/getting-started/installation/)

```
git clone https://github.com/Cutleast/pyside6-android-example --recurse-submodules
run.bat
```

## Building the Android APK

`pyside6-android-deploy` only works on Linux and macOS, so the APK is built by the [Build Android APK](./.github/workflows/build_android.yaml) workflow on GitHub Actions. Download the `android-apk` artifact from the workflow run, unzip it and install the APK on an arm64 device (e.g. with `adb install <apk>` or by copying it to the phone and opening it there).

The workflow runs [scripts/build_android.py](./scripts/build_android.py), which

1. copies `src`, the core lib and the [Android shims](./android/shims) to `build/android/app`,
2. downloads the official PySide6 and shiboken6 Android wheels from download.qt.io,
3. runs `pyside6-android-deploy --init` to generate the python-for-android recipes and the `buildozer.spec`,
4. adds the core lib's dependencies to the `buildozer.spec` and
5. builds a debug APK with buildozer into `./dist`.

The script also works locally on Linux/WSL when the Android SDK, NDK r28c, a JDK 17 and rustup are installed (see the workflow for the exact setup).

### Android specific Notes

- `material-color-utilities` is a C++ extension without an Android build. It is replaced by [a shim](./android/shims/material_color_utilities.py) based on `materialyoucolor`, which has a python-for-android recipe.
- `pydantic` is pinned to 2.12.3 in the APK, because python-for-android's `pydantic-core` recipe is at 2.41.4.
- Qt for Android is built without zstd support, so the Qt resources are compiled without compression for the APK (the desktop `pyside6-rcc` compresses with zstd by default).
- On Android, the app runs like a built distribution (no stylesheet editor), the menu bar is drawn by Qt instead of natively and changing restart-requiring settings asks for a manual restart.

# Licensing

This project is licensed under the [GNU General Public License v3.0](./LICENSE) - Copyright (c) 2026 Cutleast
