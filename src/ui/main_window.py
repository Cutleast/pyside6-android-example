"""
Copyright (c) Cutleast
"""

from typing import override

from cutleast_core_lib.core.config.manager import ConfigManager
from cutleast_core_lib.core.utilities.updater import Updater
from cutleast_core_lib.ui.utilities.window_manager import WindowManager
from cutleast_core_lib.ui.widgets.about_dialog import AboutDialog
from PySide6.QtCore import Qt
from PySide6.QtGui import QCloseEvent
from PySide6.QtWidgets import QMainWindow, QMessageBox

from core.config.app_config import AppConfig
from core.utilities.android import IS_ANDROID
from licenses import LICENSES

from .main_widget import MainWidget
from .menubar import MenuBar
from .settings.settings_dialog import SettingsDialog
from .statusbar import StatusBar


class MainWindow(QMainWindow):
    """
    Main window of the application.
    """

    __app_config_manager: ConfigManager[AppConfig]
    __app_config: AppConfig

    __menu_bar: MenuBar
    __main_widget: MainWidget
    __status_bar: StatusBar

    def __init__(self, app_config_manager: ConfigManager[AppConfig]) -> None:
        """
        Args:
            app_config_manager (ConfigManager[AppConfig]):
                Manager for the application configuration.
        """

        super().__init__()

        self.__app_config_manager = app_config_manager
        self.__app_config = app_config_manager.config

        if not IS_ANDROID:
            self.resize(500, 400)

        self.__init_ui()

        self.__menu_bar.settings_signal.connect(self.__open_settings)
        self.__menu_bar.updater_signal.connect(self.__check_for_updates)
        self.__menu_bar.about_signal.connect(self.__show_about)
        self.__menu_bar.about_qt_signal.connect(self.__show_about_qt)
        self.__menu_bar.exit_signal.connect(self.close)

        self.__app_config_manager.saved.connect(self.__on_config_saved)

    def __init_ui(self) -> None:
        self.__init_menu_bar()
        self.__init_main_widget()
        self.__init_status_bar()

    def __init_menu_bar(self) -> None:
        self.__menu_bar = MenuBar()
        self.setMenuBar(self.__menu_bar)

    def __init_main_widget(self) -> None:
        self.__main_widget = MainWidget()
        self.setCentralWidget(self.__main_widget)

    def __init_status_bar(self) -> None:
        self.__status_bar = StatusBar()
        self.__status_bar.set_log_visible(self.__app_config.log_visible)
        self.setStatusBar(self.__status_bar)

    def __on_config_saved(self) -> None:
        self.__status_bar.set_log_visible(self.__app_config.log_visible)

    def __open_settings(self) -> None:
        SettingsDialog(self.__app_config_manager).exec()

    def __check_for_updates(self) -> None:
        upd = Updater.get()
        if upd.is_update_available():
            upd.run()
        else:
            messagebox = QMessageBox(self)
            messagebox.setWindowTitle(self.tr("No Updates Available"))
            messagebox.setText(self.tr("There are no updates available."))
            messagebox.setTextFormat(Qt.TextFormat.RichText)
            messagebox.setIcon(QMessageBox.Icon.Information)
            messagebox.exec()

    def __show_about(self) -> None:
        AboutDialog(app_license="GPL-3.0", licenses=LICENSES, parent=self).exec()

    def __show_about_qt(self) -> None:
        QMessageBox.aboutQt(self, self.tr("About Qt"))

    @override
    def closeEvent(self, event: QCloseEvent) -> None:
        WindowManager.get().close_all()

        return super().closeEvent(event)
