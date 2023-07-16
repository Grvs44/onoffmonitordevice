# pylint:disable=no-member
import logging
from typing import Callable

import RPi.GPIO as gpio

from .exceptions import ValidationError


class Device:
    _logger = logging.getLogger(__name__)

    def __init__(self, setup: dict):
        self._logger.debug('Initialising (%s)', str(setup))
        if isinstance(setup, dict) and isinstance(setup.get('id'), int) and isinstance(setup.get('gpio_pin'), int):
            self._device_id: int = setup['id']
            self._pin: int = setup['gpio_pin']
            self._state = 0
            self._event = None
        else:
            raise ValidationError(f'Invalid device: {setup}')

    def _on_state_change(self, pin):
        self._logger.debug('Pin %i state change', pin)
        self._state = 1 - self._state
        print(self._state, gpio.input(pin))
        if self._event is not None:
            self._event({'device': self._device_id, 'status': self._state})

    def begin(self, event: Callable):
        self._logger.debug('Pin %i: begin', self._pin)
        self._event = event
        gpio.setup(self._pin, gpio.IN)  # type: ignore
        gpio.add_event_detect(  # type: ignore
            self._pin,
            gpio.BOTH,  # type: ignore
            callback=self._on_state_change
        )

    def __repr__(self):
        return f'Device({{"id": {self._device_id}, "gpio_pin": {self._pin}}})'
