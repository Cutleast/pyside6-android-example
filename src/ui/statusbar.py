"""
Copyright (c) Cutleast
"""

from typing import Optional, cast, override

from cutleast_core_lib.core.utilities.logger import Logger
from cutleast_core_lib.ui.utilities.icon_provider import IconProvider
from cutleast_core_lib.ui.utilities.window_manager import WindowManager
from cutleast_core_lib.ui.widgets.copy_button import CopyButton
from cutleast_core_lib.ui.widgets.elided_label import ElidedLabel
from cutleast_core_lib.ui.widgets.icon_button import IconButton
from cutleast_core_lib.ui.widgets.log_window import LogWindow
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QApplication, QLabel, QStatusBar


class StatusBar(QStatusBar):
    """
    Status bar for main window.
    """

    __log_signal = Signal(str)

    __logger: Logger

    __status_label: QLabel

    __log_window: Optional[LogWindow] = None

    @override
    def __init__(self) -> None:
        super().__init__()

        self.__logger = Logger.get()
        self.__logger.set_callback(self.__log_signal.emit)

        self.__init_ui()

    def __init_ui(self) -> None:
        self.setSizeGripEnabled(False)

        self.__status_label = ElidedLabel()
        self.__status_label.setProperty("monospace", True)
        self.__status_label.setTextFormat(Qt.TextFormat.PlainText)
        self.__log_signal.connect(
            lambda text: self.__status_label.setText(cast(str, text).splitlines()[0]),
            Qt.ConnectionType.QueuedConnection,
        )
        self.insertPermanentWidget(0, self.__status_label, stretch=1)

        copy_log_button = CopyButton()
        copy_log_button.clicked.connect(
            lambda: QApplication.clipboard().setText(self.__logger.get_content())
        )
        copy_log_button.setToolTip(self.tr("Copy log to clipboard"))
        self.addPermanentWidget(copy_log_button)

        open_log_button = IconButton()
        IconProvider.bind_qta_icon(
            open_log_button, open_log_button.setIcon, "mdi6.open-in-new"
        )
        open_log_button.setToolTip(self.tr("View log"))
        open_log_button.clicked.connect(self.__open_log_window)
        self.addPermanentWidget(open_log_button)

    def __open_log_window(self) -> None:
        if self.__log_window is None:
            self.__log_window = LogWindow(self.__logger.get_content())
            self.__log_signal.connect(
                self.__log_window.addMessage, Qt.ConnectionType.QueuedConnection
            )

        WindowManager.get().show(self.__log_window, delete_on_close=False)

    def set_log_visible(self, visible: bool) -> None:
        """
        Args:
            visible (bool): If the last log line will be displayed in the status bar.
        """

        self.__status_label.setVisible(visible)
