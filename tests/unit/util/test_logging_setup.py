from contextlib import redirect_stderr
from logging import getLogger
import os

from tests.conftest import FIXTURES

from c11h.dataclassutils.util import logging_setup


def test_configure_logger(monkeypatch, capsys):
    logger = getLogger()

    # falling back to null-handler
    monkeypatch.setattr(logging_setup, 'log_config_loc', 'CONFIG_NOT_FOUND')
    with capsys.disabled():
        # send 'no config found' warning to dev/null
        with open(os.devnull, 'w') as dev_null, redirect_stderr(dev_null):
            logging_setup.configure_logger()
        assert repr(logger.handlers) == '[<LogCaptureHandler (NOTSET)>]'

    # load default logger config
    default_config = FIXTURES / 'default_logger_config.json'
    monkeypatch.setattr(logging_setup, 'log_config_loc', default_config)
    with capsys.disabled():
        logging_setup.configure_logger()
        assert repr(logger.handlers) == "[<StreamHandler <stderr> (INFO)>]"
