from typing import Callable

import RPi.GPIO as gpio

from .exceptions import ValidationError


class Device:
    def __init__(self, setup: dict):
        if isinstance(setup, dict) and isinstance(setup.get('id'), int) and isinstance(setup.get('pin'), int):
            self._device_id = setup['id']
            self._pin = setup['pin']
        else:
            raise ValidationError(f'Invalid device: {setup}')

    def _serialize_request(self, status: int):
        return {'id': self._device_id, 'status': status}

    def begin(self, event: Callable):
        gpio.setup(self._pin, gpio.IN, pull_up_down=gpio.PUD_UP)
        gpio.add_event_detect(
            self._pin,
            gpio.RISING,
            callback=lambda pin: event(self._serialize_request(1))
        )
        gpio.add_event_detect(
            self._pin,
            gpio.FALLING,
            callback=lambda pin: event(self._serialize_request(0))
        )
