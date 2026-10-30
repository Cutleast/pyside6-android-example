"""
Copyright (c) Cutleast
"""

import webbrowser
from typing import override

from cutleast_core_lib.core.utilities.updater import Updater
from cutleast_core_lib.ui.utilities.icon_provider import IconProvider
from cutleast_core_lib.ui.widgets.menu import Menu
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QAction
from PySide6.QtWidgets import QMenuBar, QToolButton


class MenuBar(QMenuBar):
    """
    Menu bar for main window.
    """

    settings_signal = Signal()
    """Signal emitted when the user clicks on the settings button."""

    updater_signal = Signal()
    """Signal emitted when the user clicks on the updater button."""

    about_signal = Signal()
    """Signal emitted when the user clicks on the about button."""

    about_qt_signal = Signal()
    """Signal emitted when the user clicks on the about Qt button."""

    exit_signal = Signal()
    """Signal emitted when the user clicks on the exit button."""

    # Replace this with your own Discord server
    DISCORD_URL: str = "https://discord.gg/pqEHdWDf8z"
    """URL to our Discord server."""

    # Replace this with a link to your Nexus Mods page (if applicable)
    NEXUSMODS_URL: str = "https://www.nexusmods.com/site/mods/1366"
    """URL to the project's Nexus Mods page."""

    # Replace this with a link to your GitHub repository
    GITHUB_URL: str = "https://github.com/Cutleast/pyside6-android-example"
    """URL to the GitHub repository."""

    # Replace this with your own Ko-fi page
    KOFI_URL: str = "https://ko-fi.com/cutleast"
    """URL to Ko-fi page."""

    __settings_action: QAction
    __exit_action: QAction

    __update_action: QAction
    __discord_action: QAction
    __nm_action: QAction
    __github_action: QAction
    __about_action: QAction
    __about_qt_action: QAction

    __ko_fi_action: QAction
    __ko_fi_button: QToolButton

    @override
    def __init__(self) -> None:
        super().__init__()

        self.__init_file_menu()
        self.__init_help_menu()

        self.__ko_fi_action = QAction(self.tr("Support me on Ko-fi"))
        self.__ko_fi_action.setIcon(IconProvider.get_icon("ko-fi", set_colors=False))
        self.__ko_fi_action.setToolTip(MenuBar.KOFI_URL)
        self.__ko_fi_action.triggered.connect(lambda: webbrowser.open(MenuBar.KOFI_URL))

        self.__ko_fi_button = QToolButton()
        self.__ko_fi_button.setDefaultAction(self.__ko_fi_action)
        self.__ko_fi_button.setAutoRaise(True)
        self.__ko_fi_button.setToolButtonStyle(
            Qt.ToolButtonStyle.ToolButtonTextBesideIcon
        )
        self.setCornerWidget(self.__ko_fi_button, Qt.Corner.TopRightCorner)

        self.__settings_action.triggered.connect(self.settings_signal.emit)
        self.__exit_action.triggered.connect(self.exit_signal.emit)

        self.__update_action.triggered.connect(self.updater_signal.emit)
        self.__discord_action.triggered.connect(
            lambda: webbrowser.open(MenuBar.DISCORD_URL)
        )
        self.__nm_action.triggered.connect(
            lambda: webbrowser.open(MenuBar.NEXUSMODS_URL)
        )
        self.__github_action.triggered.connect(
            lambda: webbrowser.open(MenuBar.GITHUB_URL)
        )

        self.__about_action.triggered.connect(self.about_signal.emit)
        self.__about_qt_action.triggered.connect(self.about_qt_signal.emit)

    def __init_file_menu(self) -> None:
        file_menu = Menu(title=self.tr("File"))
        self.addMenu(file_menu)

        self.__settings_action = file_menu.addAction(self.tr("Settings"))
        IconProvider.bind_qta_icon(
            self.__settings_action, self.__settings_action.setIcon, "mdi6.cog"
        )

        file_menu.addSeparator()

        self.__exit_action = file_menu.addAction(self.tr("Exit"))
        IconProvider.bind_icon(self.__exit_action, self.__exit_action.setIcon, "exit")

    def __init_help_menu(self) -> None:
        help_menu = Menu(title=self.tr("Help"))
        self.addMenu(help_menu)

        self.__update_action = help_menu.addAction(self.tr("Check for updates..."))
        IconProvider.bind_qta_icon(
            self.__update_action, self.__update_action.setIcon, "mdi6.refresh"
        )
        self.__update_action.setVisible(Updater.has_instance())

        help_menu.addSeparator()

        self.__discord_action = help_menu.addAction(
            self.tr("Get support on our Discord server...")
        )
        IconProvider.bind_icon(
            self.__discord_action, self.__discord_action.setIcon, "discord"
        )
        self.__discord_action.setToolTip(MenuBar.DISCORD_URL)

        self.__nm_action = help_menu.addAction(self.tr("Open mod page on Nexus Mods..."))
        IconProvider.bind_icon(self.__nm_action, self.__nm_action.setIcon, "nexus_mods")
        self.__nm_action.setToolTip(MenuBar.NEXUSMODS_URL)

        self.__github_action = help_menu.addAction(
            self.tr("View source code on GitHub...")
        )
        IconProvider.bind_qta_icon(
            self.__github_action, self.__github_action.setIcon, "mdi6.github"
        )
        self.__github_action.setToolTip(MenuBar.GITHUB_URL)

        help_menu.addSeparator()

        self.__about_action = help_menu.addAction(self.tr("About"))
        IconProvider.bind_qta_icon(
            self.__about_action, self.__about_action.setIcon, "mdi6.information"
        )

        self.__about_qt_action = help_menu.addAction(self.tr("About Qt"))
        IconProvider.bind_icon(
            self.__about_qt_action, self.__about_qt_action.setIcon, "qt"
        )
