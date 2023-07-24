"""
Module for entry to program
"""
from argparse import ArgumentParser
import logging

from .monitor import Monitor
from .exceptions import ValidationError


_logger = logging.getLogger(__name__)


def main():
    """
    Main entry point: parse args and start monitor
    """
    parser = ArgumentParser(
        prog='onoffmonitor',
        description='Monitor the on/off status of devices and report to the server'
    )
    parser.add_argument('path', help='The path to the configuration JSON file')
    parser.add_argument(
        '-ll', '-loglevel',
        help='Logging level {debug, info, warning (default), error, critical}',
        type=int,
        choices=[logging.DEBUG, logging.INFO, logging.WARNING, logging.ERROR, logging.CRITICAL],
        default=logging.WARNING,
    )
    parser.add_argument(
        '-lf', '-logfile',
        help='Log output file path (defaults to stdout)',
        type=str,
        default=None,
    )
    args = parser.parse_args()
    logging.basicConfig(
        format='%(levelname)s: %(asctime)s: %(name)s: %(funcName)s: %(message)s',
        level=args.ll,
        filename=args.lf,
    )
    monitor = None
    try:
        monitor = Monitor(args.path)
        monitor.run()
    except ValidationError as exc:
        _logger.critical('Validation error: %s', '\n'.join(exc.args))
    except KeyboardInterrupt:
        pass
    finally:
        if monitor is not None:
            monitor.stop()
        _logger.debug('Finished')


if __name__ == '__main__':
    main()
