"""
Copyright (c) Cutleast
"""

import platform
from typing import override

import PySide6
from cutleast_core_lib.ui.theme.manager import ThemeManager
from cutleast_core_lib.ui.theme.ui_mode import UiMode
from cutleast_core_lib.ui.widgets.enum_dropdown import EnumDropdown
from cutleast_core_lib.ui.widgets.toast import Toast
from PySide6.QtCore import QSysInfo, Qt, qVersion
from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import (
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QProgressBar,
    QPushButton,
    QScrollArea,
    QScroller,
    QSlider,
    QVBoxLayout,
    QWidget,
)

from core.utilities.android import IS_ANDROID


class MainWidget(QScrollArea):
    """
    The central widget of the main window, showing a few interactive demo sections.
    """

    __vlayout: QVBoxLayout

    __counter: int = 0
    __counter_label: QLabel

    __todo_edit: QLineEdit
    __todo_list: QListWidget

    __slider: QSlider
    __progress_bar: QProgressBar

    @override
    def __init__(self) -> None:
        super().__init__()

        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        # Enables kinetic scrolling by swiping on touch screens
        QScroller.grabGesture(
            self.viewport(), QScroller.ScrollerGestureType.TouchGesture
        )

        content = QWidget()
        self.setWidget(content)

        self.__vlayout = QVBoxLayout()
        content.setLayout(self.__vlayout)

        self.__init_header()
        self.__init_info_section()
        self.__init_counter_section()
        self.__init_todo_section()
        self.__init_slider_section()
        self.__init_theme_section()

        self.__vlayout.addStretch()

    def __init_header(self) -> None:
        title_label = QLabel(self.tr("Hello Android!"))
        title_label.setProperty("title", True)
        self.__vlayout.addWidget(title_label, alignment=Qt.AlignmentFlag.AlignCenter)

        subtitle_label = QLabel(
            self.tr("This is a PySide6 Widgets app based on the cutleast-core-lib.")
        )
        subtitle_label.setProperty("secondary", True)
        subtitle_label.setWordWrap(True)
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.__vlayout.addWidget(subtitle_label)

    def __init_info_section(self) -> None:
        group_box = QGroupBox(self.tr("System"))
        flayout = QFormLayout()
        flayout.setRowWrapPolicy(QFormLayout.RowWrapPolicy.WrapLongRows)
        group_box.setLayout(flayout)
        self.__vlayout.addWidget(group_box)

        python_version: str = platform.python_version()
        screen = QGuiApplication.primaryScreen()
        screen_size = screen.size()

        platform_name: str
        if IS_ANDROID:
            # sys.getandroidapilevel() returns the API level Python was built for
            platform_name = f"Android {QSysInfo.productVersion()}"
        else:
            platform_name = f"{platform.system()} {platform.release()}"

        flayout.addRow(self.tr("Platform:"), QLabel(platform_name))
        flayout.addRow(self.tr("Architecture:"), QLabel(platform.machine()))
        flayout.addRow(self.tr("Python:"), QLabel(python_version))
        flayout.addRow(
            self.tr("PySide6 / Qt:"), QLabel(f"{PySide6.__version__} / {qVersion()}")
        )
        flayout.addRow(
            self.tr("Screen:"),
            QLabel(
                f"{screen_size.width()} x {screen_size.height()} "
                f"@ {screen.devicePixelRatio():g}x"
            ),
        )

    def __init_counter_section(self) -> None:
        group_box = QGroupBox(self.tr("Counter"))
        hlayout = QHBoxLayout()
        group_box.setLayout(hlayout)
        self.__vlayout.addWidget(group_box)

        self.__counter_label = QLabel("0")
        self.__counter_label.setProperty("title", True)
        hlayout.addWidget(self.__counter_label, stretch=1)

        reset_button = QPushButton(self.tr("Reset"))
        reset_button.clicked.connect(lambda: self.__set_counter(0))
        hlayout.addWidget(reset_button)

        increase_button = QPushButton(self.tr("Tap me!"))
        increase_button.clicked.connect(lambda: self.__set_counter(self.__counter + 1))
        hlayout.addWidget(increase_button)

    def __init_todo_section(self) -> None:
        group_box = QGroupBox(self.tr("To-do list"))
        vlayout = QVBoxLayout()
        group_box.setLayout(vlayout)
        self.__vlayout.addWidget(group_box)

        hlayout = QHBoxLayout()
        vlayout.addLayout(hlayout)

        self.__todo_edit = QLineEdit()
        self.__todo_edit.setPlaceholderText(self.tr("What needs to be done?"))
        self.__todo_edit.returnPressed.connect(self.__add_todo)
        hlayout.addWidget(self.__todo_edit, stretch=1)

        add_button = QPushButton(self.tr("Add"))
        add_button.clicked.connect(self.__add_todo)
        hlayout.addWidget(add_button)

        self.__todo_list = QListWidget()
        self.__todo_list.setMinimumHeight(150)
        QScroller.grabGesture(
            self.__todo_list.viewport(), QScroller.ScrollerGestureType.TouchGesture
        )
        self.__todo_list.itemClicked.connect(
            lambda item: self.__todo_list.takeItem(self.__todo_list.row(item))
        )
        vlayout.addWidget(self.__todo_list)

        hint_label = QLabel(self.tr("Tap an entry to remove it."))
        hint_label.setProperty("secondary", True)
        vlayout.addWidget(hint_label)

    def __init_slider_section(self) -> None:
        group_box = QGroupBox(self.tr("Slider"))
        vlayout = QVBoxLayout()
        group_box.setLayout(vlayout)
        self.__vlayout.addWidget(group_box)

        self.__slider = QSlider(Qt.Orientation.Horizontal)
        self.__slider.setRange(0, 100)
        vlayout.addWidget(self.__slider)

        self.__progress_bar = QProgressBar()
        self.__progress_bar.setRange(0, 100)
        self.__progress_bar.setTextVisible(False)
        vlayout.addWidget(self.__progress_bar)

        self.__slider.valueChanged.connect(self.__progress_bar.setValue)
        self.__slider.setValue(42)

    def __init_theme_section(self) -> None:
        group_box = QGroupBox(self.tr("Appearance"))
        vlayout = QVBoxLayout()
        group_box.setLayout(vlayout)
        self.__vlayout.addWidget(group_box)

        ui_mode_dropdown = EnumDropdown(UiMode, ThemeManager.get().ui_mode)
        ui_mode_dropdown.currentValueChanged.connect(ThemeManager.get().set_ui_mode)
        vlayout.addWidget(ui_mode_dropdown)

        toast_button = QPushButton(self.tr("Show toast"))
        toast_button.clicked.connect(self.__show_toast)
        vlayout.addWidget(toast_button)

    def __set_counter(self, value: int) -> None:
        self.__counter = value
        self.__counter_label.setText(str(value))

    def __add_todo(self) -> None:
        text: str = self.__todo_edit.text().strip()

        if text:
            self.__todo_list.addItem(text)
            self.__todo_edit.clear()

    def __show_toast(self) -> None:
        Toast(self.tr("Greetings from PySide6!"), parent=self.window()).show()
