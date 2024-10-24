import logging

import coloredlogs


class LogConfig:
    FIELD_STYLES = dict(
        asctime=dict(color='green'),
        name=dict(color='blue'),
        filename=dict(color='magenta'),
        pathname=dict(color='magenta'),
        lineno=dict(color='yellow'),
        levelname=dict(color='cyan', bold=True),
        processName=dict(color='green', bold=True),
    )
    """Mapping of log format names to default font styles."""

    LEVEL_STYLES = dict(
        debug=dict(color='blue'),
        info=dict(color='green'),
        warning=dict(color='yellow'),
        error=dict(color='red'),
        critical=dict(background='red', bold=True),
    )

    BASIC_FORMAT = '{asctime} - {name:12} - {filename:15} - [{levelname:^7}]: {message}'

    COLORD_BASIC_FORMAT = coloredlogs.ColoredFormatter(
        fmt=BASIC_FORMAT,
        style='{',
        level_styles=LEVEL_STYLES,
        field_styles=FIELD_STYLES
    )

    @staticmethod
    def get_console_handler(level):
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)
        console_handler.setFormatter(LogConfig.COLORD_BASIC_FORMAT)
        return console_handler

    @staticmethod
    def get_file_handler(filename):
        file_handler = logging.FileHandler(filename, encoding='utf-8')
        file_handler.setFormatter(logging.Formatter(LogConfig.BASIC_FORMAT, style='{'))
        return file_handler


def logging_config(logger_name, level=logging.INFO, file_name=None):
    logging.getLogger(logger_name).setLevel(level)
    logging.getLogger(logger_name).handlers = [LogConfig.get_console_handler(level)]
    if file_name:
        logging.getLogger(logger_name).addHandler(LogConfig.get_file_handler(file_name))
