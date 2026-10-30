"""
Copyright (c) Cutleast
"""

import webbrowser
from typing import override

from PySide6.QtCore import QUrl
from PySide6.QtGui import QDesktopServices


class QtBrowser(webbrowser.BaseBrowser):
    """
    A browser for Python's `webbrowser` module that opens URLs with Qt. This is used on
    Android, where `webbrowser` finds no browser and Qt opens URLs via an intent.
    """

    @override
    def open(self, url: str, new: int = 0, autoraise: bool = True) -> bool:
        return QDesktopServices.openUrl(QUrl(url))

    @classmethod
    def register(cls) -> None:
        """
        Registers the browser as preferred browser, so that all `webbrowser.open()`
        calls (including the ones in the core lib) use it.
        """

        webbrowser.register("qt", None, cls("qt"), preferred=True)
