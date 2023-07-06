"""
Module containing the main monitor program
"""
import json
import sys
from pathlib import Path

import keyring
import requests

from .device import Device
from .exceptions import ValidationError


class Monitor:
    """
    Starts a new monitor program
    """
    keyring_service = 'onoffmonitor'

    def __init__(self, settings_path: str):
        path = self._get_path(settings_path)
        self._process_settings(json.loads(path.read_text()))
        self._login()

    @staticmethod
    def _get_path(settings_path: str):
        path = Path(settings_path)
        if not path.exists():
            raise ValidationError(f'The file {settings_path} doesn\'t exist')
        if not path.is_file():
            raise ValidationError(f'{settings_path} is not a file')
        return path

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

    def _login(self):
        password = keyring.get_password(self.keyring_service, self.username)
        while True:
            if password is None:
                password = input(f'Enter password for {self.username}: ')
            request = requests.post(
                self.host + self.login_path + 'login/', auth=(self.username, password), timeout=10)
            response = request.json()
            if 'token' in response:
                self.token = response['token']
                keyring.set_password(self.keyring_service, self.username, password)
                print('Logged in')
                break
            password = None
            if 'detail' in response:
                print(response['detail'], file=sys.stderr)
            else:
                print('Response from server:', response, file=sys.stderr)
