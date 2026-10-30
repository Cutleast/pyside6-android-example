"""
Copyright (c) Cutleast
"""

from typing import Annotated

from cutleast_core_lib.core.config.app_config import AppConfig as BaseAppConfig
from cutleast_core_lib.core.utilities.base_enum import BaseEnum
from cutleast_core_lib.core.utilities.dynamic_default_model import default_factory
from pydantic import Field


class AppConfig(BaseAppConfig):
    """
    App configuration.
    """

    class AppLanguage(BaseEnum):
        """Enum for the languages supported by the app."""

        System = "System"
        German = "de_DE"
        English = "en_US"

    language: Annotated[AppLanguage, Field(alias="ui.language")] = AppLanguage.System

    @default_factory("accent_color")
    @classmethod
    def get_default_accent_color(cls) -> str:
        """
        Returns:
            str: Default accent color.
        """

        return "#3ddc84"
