'''
Module for managing a device
'''
# pylint:disable=no-member
import logging
from typing import Callable

import RPi.GPIO as gpio

from .exceptions import ValidationError


class Device:
    '''
    Manage the state, GPIO pin(s), and events of a device
    '''
    _logger = logging.getLogger(__name__)

    def __init__(self, setup: dict):
        self._logger.debug('Initialising (%s)', setup)
        if (
            isinstance(setup, dict)
            and isinstance(setup.get('id'), int)
            and isinstance(setup.get('gpio_input'), int)
        ):
            self._device_id: int = setup['id']
            self._input: int = setup['gpio_input']
            led = setup.get('gpio_led')
            if isinstance(led, int):
                self._led = led
            else:
                self._led = None
            self._state = 0
            self._event = None
        else:
            raise ValidationError(f'Invalid device: {setup}')

    def _on_state_change(self, pin):
        self._logger.debug('Pin %i state change', pin)
        self._state = 1 - self._state
        print(self._state, gpio.input(pin))
        if self._led is not None:
            gpio.output(self._led, self._state)
        if self._event is not None:
            self._event({'device': self._device_id, 'status': self._state})

    def begin(self, event: Callable):
        '''
        Set up the GPIO pin(s) and add events
        '''
        self._logger.debug('Pin %i: begin', self._input)
        self._event = event
        gpio.setup(self._input, gpio.IN)
        if self._led is not None:
            gpio.setup(self._led, gpio.OUT)
        gpio.add_event_detect(
            self._input,
            gpio.BOTH,
            callback=self._on_state_change
        )

    def __repr__(self):
        return f"Device({{'id': {self._device_id}, 'gpio_input': {self._input}, 'gpio_led': {self._led}}})"
