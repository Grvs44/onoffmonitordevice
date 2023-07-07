"""
Module containing the main monitor program
"""
import getpass
import json
import sys
from time import sleep
from pathlib import Path

import keyring
import requests
import RPi.GPIO as gpio

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
        self._token = None

    def run(self):
        self._login()
        self._monitor()

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
        devices: list[Device] = []
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
        self._host = settings['host']
        self._username = settings['username']
        self._devices = devices
        self._monitor_path = settings.get('monitorapi', '/api/onoffmonitor/')
        self._login_path = settings.get('loginapi', '/api/')

    def _login(self):
        password = keyring.get_password(self.keyring_service, self._username)
        while True:
            if password is None:
                password = getpass.getpass(
                    f'Enter password for {self._username}: ')
            request = requests.post(
                self._host + self._login_path + 'login/', auth=(self._username, password), timeout=10)
            response = request.json()
            if 'token' in response:
                self._token = response['token']
                keyring.set_password(self.keyring_service,
                                     self._username, password)
                print('Logged in')
                break
            password = None
            if 'detail' in response:
                print(response['detail'], file=sys.stderr)
            else:
                print('Response from server:', response, file=sys.stderr)

    def _monitor(self):
        gpio.setmode(gpio.BOARD)
        for device in self._devices:
            device.begin(self.on_device_state_change)
        print('Sleeping')
        sleep(20)

    def on_device_state_change(self, data):
        print('Sending', data)
        request = requests.post(self._host + self._monitor_path + 'status/', json=data, headers={'Authorization': 'Token ' + self._token})
        print(request.text)

    def __del__(self):
        print('del')
