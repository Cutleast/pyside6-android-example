"""
Copyright (c) Cutleast
"""

import sys

IS_ANDROID: bool = hasattr(sys, "getandroidapilevel")
"""Whether the app is running on Android."""
