"""
Copyright (c) Cutleast
"""

import sys
from argparse import Namespace

from core.utilities.android import IS_ANDROID

if IS_ANDROID:
    # The APK only contains the packaged app, so treat it like a built distribution.
    # This hides development tools (like the stylesheet editor) and makes the core lib
    # resolve its data folder next to this file inside the app's private storage.
    sys.frozen = True  # type: ignore[attr-defined]
    sys.argv = [__file__]

from app import App
from resources_rc import qt_resource_data as qt_resource_data

if __name__ == "__main__":
    app = App(Namespace())

    sys.exit(app.exec())
