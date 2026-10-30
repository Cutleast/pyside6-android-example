"""
Copyright (c) Cutleast
"""

from argparse import Namespace
from typing import Optional, cast, override

from cutleast_core_lib.base_app import BaseApp
from cutleast_core_lib.core.config.app_config import AppConfig as BaseAppConfig
from cutleast_core_lib.core.config.manager import ConfigManager
from cutleast_core_lib.core.utilities.localisation import detect_system_locale
from cutleast_core_lib.core.utilities.singleton import Singleton
from cutleast_core_lib.ui.theme.manager import ThemeManager
from cutleast_core_lib.ui.utilities.state_manager import WidgetStateManager
from PySide6.QtCore import QLocale, QTranslator

from core.config.app_config import AppConfig
from ui.main_window import MainWindow


class App(BaseApp, Singleton):
    """
    Main application class.
    """

    APP_NAME: str = "PySide6 Android Example"
    APP_VERSION: str = "development"  # This gets replaced when building

    @override
    def __init__(self, args: Namespace) -> None:
        Singleton.__init__(self)
        super().__init__(args)

    @override
    def _init(self) -> None:
        self.setApplicationName(App.APP_NAME)
        self.setApplicationVersion(App.APP_VERSION)

        super()._init()

        WidgetStateManager.get().register_geometry("main_window", self.main_window)

    @override
    def _init_app_config_manager(self) -> ConfigManager[BaseAppConfig]:
        return ConfigManager(AppConfig, self.config_path)

    @override
    def _init_main_window(self) -> MainWindow:
        self.__load_translation()
        ThemeManager(
            app=self,
            initial_primary_color=self.app_config.accent_color,
            initial_ui_mode=self.app_config.ui_mode,
            qss_files=ThemeManager.CORE_RES_QSS_FILES + [":/style.qss"],
        )

        return MainWindow(cast(ConfigManager[AppConfig], self.app_config_manager))

    def __load_translation(self) -> None:
        """
        Loads translation for the configured language and installs the translator into
        the app.
        """

        translator = QTranslator(self)

        app_config: AppConfig = cast(AppConfig, self.app_config)

        language: str
        if app_config.language == AppConfig.AppLanguage.System:
            language = detect_system_locale() or "en_US"
        else:
            language = app_config.language.value
            QLocale.setDefault(QLocale.Language[app_config.language.name])

        if language != "en_US":
            res_file: str = f":/loc/{language}.qm"
            if not translator.load(res_file):
                self.log.error(
                    f"Failed to load localisation for {language} from '{res_file}'."
                )
            else:
                self.installTranslator(translator)
                self.log.info(f"Loaded localisation for {language}.")

    # When these three methods return non-None values, the update checker will be enabled
    @override
    @classmethod
    def get_repo_owner(cls) -> Optional[str]:
        return

    @override
    @classmethod
    def get_repo_name(cls) -> Optional[str]:
        return

    @override
    @classmethod
    def get_repo_branch(cls) -> Optional[str]:
        return
