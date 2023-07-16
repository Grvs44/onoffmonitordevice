"""
Module containing the main monitor program
"""
import getpass
import json
import logging
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
    _logger = logging.getLogger(__name__)

    def __init__(self, settings_path: str):
        self._logger.debug('Initialising (%s)', settings_path)
        path = self._get_path(settings_path)
        self._devices: list[Device] = []
        self._process_settings(json.loads(path.read_text()))
        self._token = ''

    def run(self):
        self._logger.debug('Running')
        self._login()
        self._fetch_devices()
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
        self._logger.debug('Processing settings')
        errors = []
        if not isinstance(settings.get('host'), str):
            errors.append('"host" property missing or not a string')
        if not isinstance(settings.get('username'), str):
            errors.append('"username" property missing or not a string')
        if not isinstance(settings.get('id'), int):
            errors.append('"id" property missing or not an integer')
        if len(errors) != 0:
            raise ValidationError(*errors)
        self._host = settings['host']
        self._username = settings['username']
        self._monitor_id = settings['id']
        self._monitor_path = settings.get('monitorapi', '/api/onoffmonitor/')
        self._login_path = settings.get('loginapi', '/api/')

    def _login(self):
        self._logger.debug('Logging in')
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
                self._logger.info('Logged in as %s', self._username)
                break
            password = None
            if 'detail' in response:
                self._logger.error(response['detail'])
            else:
                self._logger.error('Response from server: %s', response)

    def _fetch_devices(self):
        self._logger.debug('Fetching device configuration')
        request = requests.get('%s%sdevice/?monitor=%i' % (self._host, self._monitor_path, self._monitor_id), headers={'Authorization': 'Token ' + self._token})
        response = request.json()
        for device in response:
            self._devices.append(Device(device))
        self._logger.debug('Devices: %s', str(self._devices))

    def _monitor(self):
        gpio.setmode(gpio.BOARD)
        for device in self._devices:
            device.begin(self.on_device_state_change)
        print('Sleeping')
        sleep(20)

    def on_device_state_change(self, data):
        self._logger.debug('Sending %s', str(data))
        request = requests.post(self._host + self._monitor_path + 'status/', json=data, headers={'Authorization': 'Token ' + self._token})
        self._logger.debug(request.text)

    def __del__(self):
        print('del')
