"""
Copyright (c) Cutleast
"""

from typing import Optional, cast, override

from PySide6.QtCore import QEvent, QObject, Qt
from PySide6.QtGui import QKeyEvent
from PySide6.QtWidgets import QApplication, QMessageBox, QWidget


class AndroidWindowAdapter(QObject):
    """
    Adapts secondary windows to Android, where windows have no title bar to move or
    close them: Windows and dialogs are shown maximized like separate screens and the
    system back gesture closes the topmost popup, dialog or window.
    """

    MAXIMIZED_WINDOW_TYPES: tuple[Qt.WindowType, ...] = (
        Qt.WindowType.Window,
        Qt.WindowType.Dialog,
    )
    """Window types that are shown maximized (popups, tool windows etc. are not)."""

    __main_window: QWidget

    def __init__(self, app: QApplication, main_window: QWidget) -> None:
        """
        Args:
            app (QApplication): The application to install the event filter on.
            main_window (QWidget):
                The main window, which is left to Android's default back behavior
                (closing the app).
        """

        super().__init__(app)

        self.__main_window = main_window

        app.installEventFilter(self)

    @override
    def eventFilter(self, watched: QObject, event: QEvent) -> bool:
        if event.type() == QEvent.Type.Show and isinstance(watched, QWidget):
            self.__maximize_window(watched)

        elif (
            event.type() == QEvent.Type.KeyPress
            and cast(QKeyEvent, event).key() == Qt.Key.Key_Back
        ):
            return self.__close_topmost_window()

        return super().eventFilter(watched, event)

    def __maximize_window(self, widget: QWidget) -> None:
        """
        Maximizes the specified widget if it is a secondary window or dialog.

        Args:
            widget (QWidget): The widget that is about to be shown.
        """

        if (
            not widget.isWindow()
            or widget is self.__main_window
            or widget.windowType() not in AndroidWindowAdapter.MAXIMIZED_WINDOW_TYPES
            # Message boxes are small and can be closed with their own buttons
            or isinstance(widget, QMessageBox)
        ):
            return

        widget.setWindowState(widget.windowState() | Qt.WindowState.WindowMaximized)

    def __close_topmost_window(self) -> bool:
        """
        Closes the topmost popup, dialog or secondary window.

        Returns:
            bool: Whether a window was closed and the back event should be consumed.
        """

        window: Optional[QWidget] = (
            QApplication.activePopupWidget()
            or QApplication.activeModalWidget()
            or QApplication.activeWindow()
        )

        if window is None or window is self.__main_window:
            return False

        window.close()
        return True
