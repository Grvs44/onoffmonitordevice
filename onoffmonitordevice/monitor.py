import json
import keyring
from pathlib import Path

from .device import Device
from .exceptions import ValidationError


class Monitor:
    def __init__(self, settings_path: Path):
        self._process_settings(json.loads(settings_path.read_text()))

    def _process_settings(self, settings: dict):
        errors = []
        devices = []
        if not isinstance(settings.get('host'), str):
            errors.append('"host" property missing or not a string')
        if not isinstance(settings.get('username'), str):
            errors.append('"username" property missing or not a string')
        if isinstance(settings.get('devices'), list):
            for device in settings['devices']:
                devices.append(Device(device))
        else:
            errors.append('"devices" property missing or not a list')
        if len(errors) != 0:
            raise ValidationError(*errors)
        self.host = settings['host']
        self.username = settings['username']
        self.devices = devices
        self.monitor_path = settings.get('monitorapi', '/api/onoffmonitor/')
        self.login_path = settings.get('loginapi', '/api/')
