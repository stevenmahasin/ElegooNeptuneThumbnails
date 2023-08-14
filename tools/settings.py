# Copyright (c) 2023 Molodos
# The ElegooNeptuneThumbnails plugin is released under the terms of the AGPLv3 or higher.

import json
import uuid
from os import path
from typing import Any, Optional

from UM.Application import Application
from UM.Logger import Logger


class Settings:
    """
    Thumbnail settings
    """

    OPTIONS: dict[str, str] = {
        "nothing": "Nothing",
        "includeTimeEstimate": "Time Estimate",
        "includeFilamentGramsEstimate": "Filament Grams Estimate",
        "includeLayerHeight": "Layer Height",
        "includeModelHeight": "Model Height",
        "includeFilamentMetersEstimate": "Filament Meters Estimate",
        # "includeCostEstimate": "Cost Estimate"
    }
    PRINTER_MODELS: dict[str, str] = {
        "elegoo_neptune_2": "Elegoo Neptune 2",
        "elegoo_neptune_2_s": "Elegoo Neptune 2S",
        "elegoo_neptune_3_pro": "Elegoo Neptune 3 Pro",
        "elegoo_neptune_3_plus": "Elegoo Neptune 3 Plus",
        "elegoo_neptune_3_max": "Elegoo Neptune 3 Max"
    }

    def __init__(self, statistics_id: str, plugin_json: dict[str, Any]):
        # Read stuff from files
        self.statistics_id: str = statistics_id
        self.plugin_json: dict[str, Any] = plugin_json

        # Define config
        self.thumbnails_enabled: bool = True
        self.printer_model: int = 2
        self.corner_options: list[int] = [0, 0, 3, 1]
        self.statistics_enabled: bool = True
        self.use_current_model: bool = False

    def get_printer_model_id(self) -> str:
        """
        Get str id of printer model
        """
        return list(self.PRINTER_MODELS.keys())[self.printer_model]

    def get_corner_option_ids(self) -> list[str]:
        """
        Get corner option ids (str) if not "Nothing"
        """
        # Find selected options
        option_ids: list[str] = list(self.OPTIONS.keys())
        selected_options: list[str] = [option_ids[i] for i in self.corner_options if i > 0]

        # Remove duplicates
        selected_options = list(dict.fromkeys(selected_options))

        # Add "includeThumbnail" if thumbnails are enabled
        if self.thumbnails_enabled:
            selected_options.insert(0, "includeThumbnail")
        return selected_options

    def is_old_thumbnail(self) -> bool:
        """
        Check if old thumbnail is required
        """
        return list(self.PRINTER_MODELS.keys())[self.printer_model] in ["elegoo_neptune_2", "elegoo_neptune_2_s"]

    def load_json(self, data: dict[str, Any]) -> None:
        """
        Load from json
        """
        self.thumbnails_enabled = data["thumbnails_enabled"]
        self.printer_model = data["printer_model"]
        self.corner_options = data["corner_options"]
        self.statistics_enabled = data["statistics_enabled"]
        self.use_current_model = data["use_current_model"]

    def to_json(self) -> dict[str, Any]:
        """
        Parse to json
        """
        return {
            "thumbnails_enabled": self.thumbnails_enabled,
            "printer_model": self.printer_model,
            "corner_options": self.corner_options,
            "statistics_enabled": self.statistics_enabled,
            "use_current_model": self.use_current_model
        }


class SettingsManager:
    """
    Thumbnail settings manager
    """

    SETTINGS_KEY: str = "elegoo_neptune_thumbnails"
    STATISTICS_ID_KEY: str = "general/statistics_id"
    PLUGIN_JSON_PATH: str = path.join(path.dirname(path.realpath(__file__)), "..", "plugin.json")

    _settings: Optional[Settings] = None

    @classmethod
    def get_settings(cls) -> Settings:
        """
        Get the settings instance
        """
        if not cls._settings:
            cls.load()
        return cls._settings

    @classmethod
    def load(cls) -> None:
        """
        Load settings (also used to discard changes)
        """
        # Init settings if None
        if not cls._settings:
            cls._settings = Settings(statistics_id=cls._generate_statistics_id(), plugin_json=cls._read_plugin_json())

        # Load settings and update
        plain_data: str = Application.getInstance().getGlobalContainerStack().getMetaDataEntry(cls.SETTINGS_KEY)
        if plain_data:
            data: dict[str, Any] = json.loads(plain_data)
            cls._settings.load_json(data=data)
        else:
            # Default settings
            cls._settings.thumbnails_enabled = True
            cls._settings.printer_model = 2  # Neptune 3 Pro is most probable
            cls._settings.corner_options = [0, 0, 3, 1]
            cls._settings.statistics_enabled = True
            cls._settings.use_current_model = False

            # Try to determine current printer model
            printer_id: str = Application.getInstance().getMachineManager().activeMachine.definition.getId()
            if printer_id in ["elegoo_neptune_2"]:
                cls._settings.printer_model = 0
            if printer_id in ["elegoo_neptune_2s", "elegoo_neptune_2_s"]:
                cls._settings.printer_model = 1
            if printer_id in ["elegoo_neptune_3pro", "elegoo_neptune_3_pro"]:
                cls._settings.printer_model = 2
            if printer_id in ["elegoo_neptune_3plus", "elegoo_neptune_3_plus"]:
                cls._settings.printer_model = 3
            if printer_id in ["elegoo_neptune_3max", "elegoo_neptune_3_max"]:
                cls._settings.printer_model = 4
            # Printer ids, that most likely have no thumbnail: elegoo_neptune_1
            # Printer ids, that need to be added: elegoo_neptune_4, elegoo_neptune_4_pro, elegoo_neptune_4pro

    @classmethod
    def save(cls) -> None:
        """
        Save settings
        """
        # Init settings if None
        if not cls._settings:
            cls.load()

        # Get data and save
        data: dict[str, Any] = cls._settings.to_json()
        Application.getInstance().getGlobalContainerStack().setMetaDataEntry(cls.SETTINGS_KEY, json.dumps(data))

    @classmethod
    def _generate_statistics_id(cls) -> str:
        """
        Generates an id for anonymous statistics
        """
        # Generate if not exists
        if not Application.getInstance().getPreferences().getValue(cls.STATISTICS_ID_KEY):
            Application.getInstance().getPreferences().addPreference(cls.STATISTICS_ID_KEY, "")
            Application.getInstance().getPreferences().setValue(cls.STATISTICS_ID_KEY, str(uuid.uuid4()))
            Application.getInstance().savePreferences()

        # Read and return
        return Application.getInstance().getPreferences().getValue(cls.STATISTICS_ID_KEY)

    @classmethod
    def _read_plugin_json(cls) -> dict[str, Any]:
        """
        Read the plugin json
        """
        # Read plugin json
        with open(cls.PLUGIN_JSON_PATH, "r") as file:
            return json.load(file)
