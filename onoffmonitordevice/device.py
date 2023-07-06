import RPi.GPIO as gpio

from .exceptions import ValidationError


class Device:
    def __init__(self, setup: dict):
        if isinstance(setup, dict) and isinstance(setup.get('id'), int) and isinstance(setup.get('pin'), int):
            self._device_id = setup['id']
            self._pin = setup['pin']
            self._state = False
        else:
            raise ValidationError(f'Invalid device: {setup}')
    def check_state_change(self):
        new_state = gpio.input(self._pin)
        if new_state == self._state:
            return None
        self._state = new_state
        return {'id': self._device_id, 'status': new_state}
