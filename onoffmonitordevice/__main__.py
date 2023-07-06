"""
Module for entry to program
"""
from argparse import ArgumentParser
import sys

from .monitor import Monitor
from .exceptions import ValidationError


def main():
    """
    Main entry point: parse args and start monitor
    """
    parser = ArgumentParser(
        prog='onoffmonitor',
        description='Monitor the on/off status of devices and report to the server'
    )
    parser.add_argument('path', help='The path to the configuration JSON file')
    args = parser.parse_args()
    try:
        Monitor(args.path).run()
    except ValidationError as exc:
        print('\n'.join(exc.args), file=sys.stderr)
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    main()
