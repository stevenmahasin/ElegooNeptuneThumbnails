# Copyright (c) 2023 - 2024 Molodos
# The ElegooNeptuneThumbnails plugin is released under the terms of the AGPLv3 or higher.
import uuid
from os import path
from typing import Optional

from PyQt6.QtCore import QObject, pyqtSlot, pyqtProperty
from PyQt6.QtQuick import QQuickItem, QQuickWindow

from UM.Extension import Extension
from UM.Logger import Logger
from cura.CuraApplication import CuraApplication
from .settings import Settings, SettingsManager
from .thumbnail_generator import ThumbnailGenerator


class SettingsTranslator(QObject):
    """
    Settings manager (integration between python code and gui)
    """

    THUMBNAIL_PREVIEW_PATH: str = "../img/thumbnail_preview.png"
    BUY_ME_A_COFFEE_URL: str = "https://img.buymeacoffee.com/button-api/?text=Buy%20me%20a%20coffee&emoji=&slug=molodos&button_colour=196EF0&font_colour=ffffff&font_family=Comic&outline_colour=000000&coffee_colour=FFDD00"

    def __init__(self):
        QObject.__init__(self)
        self._popup: Optional[QQuickWindow] = None
        self._selected_corner: int = -1
        self._support_button_loaded: bool = False

    def set_popup_ref(self, popup: QQuickWindow) -> None:
        """
        Set the popup ref for updates
        """
        self._popup = popup

    def render_thumbnail(self) -> None:
        """
        Render a thumbnail image form settings (needs to be called on settings change)
        """
        ThumbnailGenerator.generate_preview()
        if self._popup:
            thumbnail: QQuickItem = self._popup.findChild(QQuickItem, "thumbnailPreview")
            thumbnail.setProperty("source", "")
            thumbnail.setProperty("source", self.THUMBNAIL_PREVIEW_PATH)

    def update_gui(self) -> None:
        """
        Updates all values in the gui
        """
        # Only update if popup exists
        if self._popup:
            self._popup.findChild(QQuickItem, "thumbnailsEnabled") \
                .setProperty("checked", SettingsManager.get_settings().thumbnails_enabled)
            self._popup.findChild(QQuickItem, "KP3SthumbnailsEnabled") \
                .setProperty("checked", SettingsManager.get_settings().KP3S_thumbnails_enabled)
            self._popup.findChild(QQuickItem, "klipperThumbnailsEnabled") \
                .setProperty("checked", SettingsManager.get_settings().klipper_thumbnails_enabled)
            self._popup.findChild(QQuickItem, "printerModel") \
                .setProperty("currentIndex", SettingsManager.get_settings().printer_model)
            for i, v in enumerate(SettingsManager.get_settings().corner_options):
                self._popup.findChild(QQuickItem, f"corner{i}") \
                    .setProperty("currentIndex", v)
            self._popup.findChild(QQuickItem, "sendStatistics") \
                .setProperty("checked", SettingsManager.get_settings().statistics_enabled)
            self._popup.findChild(QQuickItem, "useCurrentModel") \
                .setProperty("checked", SettingsManager.get_settings().use_current_model)
            if not self._support_button_loaded:
                self._popup.findChild(QQuickItem, "donationLink") \
                    .setProperty("source", self.BUY_ME_A_COFFEE_URL + f"&nonce={str(uuid.uuid4())}")
                self._support_button_loaded = True
            self.render_thumbnail()

    # Thumbnails enabled state

    @pyqtProperty(bool)
    def thumbnails_enabled(self) -> bool:
        return SettingsManager.get_settings().thumbnails_enabled

    @pyqtSlot(bool)
    def set_thumbnails_enabled(self, enabled: bool) -> None:
        updated: bool = SettingsManager.get_settings().thumbnails_enabled != enabled
        SettingsManager.get_settings().thumbnails_enabled = enabled
        if updated:
            # Update preview
            self.render_thumbnail()

    # Klipper thumbnails enabled state

    @pyqtProperty(bool)
    def klipper_thumbnails_enabled(self) -> bool:
        return SettingsManager.get_settings().klipper_thumbnails_enabled

    @pyqtSlot(bool)
    def set_klipper_thumbnails_enabled(self, enabled: bool) -> None:
        updated: bool = SettingsManager.get_settings().klipper_thumbnails_enabled != enabled
        SettingsManager.get_settings().klipper_thumbnails_enabled = enabled
        if updated:
            # Update preview
            self.render_thumbnail()

    # KP3S thumbnails enabled state

    @pyqtProperty(bool)
    def KP3S_thumbnails_enabled(self) -> bool:
        return SettingsManager.get_settings().KP3S_thumbnails_enabled

    @pyqtSlot(bool)
    def set_KP3S_thumbnails_enabled(self, enabled: bool) -> None:
        updated: bool = SettingsManager.get_settings().KP3S_thumbnails_enabled != enabled
        SettingsManager.get_settings().KP3S_thumbnails_enabled = enabled
        if updated:
            # Update preview
            self.render_thumbnail()

    # Printer dropdown

    @pyqtProperty(list)  # List must be untyped!
    def printer_model_list(self) -> list[str]:
        return list(Settings.PRINTER_MODELS.values())

    @pyqtSlot(int)
    def select_printer_model(self, model: int) -> None:
        updated: bool = SettingsManager.get_settings().printer_model != model
        SettingsManager.get_settings().printer_model = model
        if updated:
            # Update preview
            self.render_thumbnail()

    @pyqtProperty(int)
    def selected_printer_model(self) -> int:
        return SettingsManager.get_settings().printer_model

    # Options dropdowns

    @pyqtProperty(list)  # List must be untyped!
    def option_list(self) -> list[str]:
        return list(Settings.OPTIONS.values())

    @pyqtSlot(int)
    def select_corner(self, corner: int) -> None:
        self._selected_corner = corner

    @pyqtProperty(int)
    def selected_corner_option(self) -> int:
        return SettingsManager.get_settings().corner_options[self._selected_corner]

    @pyqtSlot(int, int)
    def set_corner_option(self, corner: int, option: int) -> None:
        updated: bool = SettingsManager.get_settings().corner_options[corner] != option
        SettingsManager.get_settings().corner_options[corner] = option
        if updated:
            # Update preview
            self.render_thumbnail()

    # Statistics enabled state

    @pyqtProperty(bool)
    def statistics_enabled(self) -> bool:
        return SettingsManager.get_settings().statistics_enabled

    @pyqtSlot(bool)
    def set_statistics_enabled(self, enabled: bool) -> None:
        SettingsManager.get_settings().statistics_enabled = enabled

    # Use current model enabled state

    @pyqtProperty(bool)
    def use_current_model(self) -> bool:
        return SettingsManager.get_settings().use_current_model

    @pyqtSlot(bool)
    def set_use_current_model(self, enabled: bool) -> None:
        updated: bool = SettingsManager.get_settings().use_current_model != enabled
        SettingsManager.get_settings().use_current_model = enabled
        if updated:
            # Update preview
            self.render_thumbnail()

    # Save/restore buttons

    @pyqtSlot(bool)
    def visibility_changed(self, visible: bool) -> None:
        """
        Popup open/close
        """
        if not visible:
            # Discard settings on close
            SettingsManager.load()

    @pyqtSlot()
    def save(self) -> None:
        """
        Save the settings
        """
        SettingsManager.save()


class GUIManager(QObject):
    """
    GUI manager (adds gui components to extension)
    """

    GUI_FILE_PATH: str = path.join(path.dirname(path.realpath(__file__)), "gui.qml")

    def __init__(self, extension: Extension):
        QObject.__init__(self)

        # Init settings
        self.settings_translator: SettingsTranslator = SettingsTranslator()

        # Add menu items with popup trigger
        extension.setMenuName("Elegoo Neptune Thumbnails")
        extension.addMenuItem("Thumbnail Settings", self.show_settings_popup)
        self._popup: Optional[QQuickWindow] = None

    def show_settings_popup(self) -> None:
        """
        Show the settings popup
        """
        # Initialize gui if not exists
        if self._popup is None and not self.init_gui():
            Logger.log("e", "Failed to create ElegooNeptuneThumbnails settings window.")

        if self._popup is not None:
            # Update gui and show
            self.settings_translator.update_gui()
            self._popup.show()

    def init_gui(self) -> bool:
        """
        Initialize GUI
        :return: Success state
        """
        # Create the plugin dialog component
        self._popup = CuraApplication.getInstance().createQmlComponent(self.GUI_FILE_PATH, {
            "settings": self.settings_translator
        })

        # Update ref and return
        self.settings_translator.set_popup_ref(self._popup)
        return self._popup is not None
