from .exceptions import ValidationError


class Device:
    def __init__(self, setup: dict):
        if isinstance(setup, dict) and isinstance(setup.get('id'), int) and isinstance(setup.get('pin'), int):
            self.id = setup['id']
            self.pin = setup['pin']
        else:
            raise ValidationError(f'Invalid device: {setup}')
