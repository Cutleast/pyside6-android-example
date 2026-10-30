"""
Copyright (c) Cutleast

Android replacement for the `material_color_utilities` package.

The original package is a C++ extension that has no Android build, so this module maps
the small part of its API used by the core library onto `materialyoucolor`, which is
available as a python-for-android recipe. It only gets copied into the Android build.
"""

from materialyoucolor.hct import Hct as _Hct
from materialyoucolor.utils.color_utils import argb_from_rgb


class Hct:
    """
    A color in the HCT (hue, chroma, tone) color space, created from a hex color.
    """

    __hct: _Hct

    def __init__(self, hex_color: str) -> None:
        """
        Args:
            hex_color (str): The color as hex string, e.g. `#3ddc84`.
        """

        value: str = hex_color.lstrip("#")
        red, green, blue = (int(value[i : i + 2], 16) for i in (0, 2, 4))
        self.__hct = _Hct.from_int(argb_from_rgb(red, green, blue))

    @property
    def hue(self) -> float:
        """The hue of the color in degrees."""

        return self.__hct.hue

    @hue.setter
    def hue(self, value: float) -> None:
        self.__hct.hue = value

    @property
    def chroma(self) -> float:
        """The chroma of the color."""

        return self.__hct.chroma

    @chroma.setter
    def chroma(self, value: float) -> None:
        self.__hct.chroma = value

    @property
    def tone(self) -> float:
        """The tone of the color between 0 and 100."""

        return self.__hct.tone

    @tone.setter
    def tone(self, value: float) -> None:
        self.__hct.tone = value

    @property
    def hex(self) -> str:
        """The color as lowercase hex string, e.g. `#3ddc84`."""

        return f"#{self.__hct.to_int() & 0xFFFFFF:06x}"
