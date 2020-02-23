from unittest import mock
import argparse
import os
import subprocess
import tempfile

import pytest

from run_with_secrets.__main__ import main


def test_basic_yaml():
    values = run('testing/configA.yaml')

    assert 'SECRET_TOKEN=configA' in values
    assert_not_in_environment()


def test_basic_json():
    values = run('testing/configB.json')

    assert 'SECRET_TOKEN=configB' in values
    assert_not_in_environment()


def run(*configs):
    with tempfile.NamedTemporaryFile() as f:
        argv = [
            'prog',
            *configs,
            '--',
            os.path.join(os.path.dirname(__file__), '../testing/checker.sh'),
            f.name,
        ]

        with mock.patch('sys.argv', argv):
            main(argv[1:])

        return f.read().decode('utf-8').splitlines()


def assert_not_in_environment():
    # Secrets should only reside in the subprocess.
    assert not os.environ.get('SECRET_TOKEN')
    with tempfile.NamedTemporaryFile() as f:
        subprocess.call(
            ' '.join([
                os.path.join(os.path.dirname(__file__), '../testing/checker.sh'),
                f.name,
            ]),
            shell=True,
        )

        assert b'SECRET_TOKEN' not in f.read()


class TestUsage:
    def test_throws_error_on_no_command(self):
        with pytest.raises(argparse.ArgumentTypeError):
            main('testing/configA.yaml'.split())

