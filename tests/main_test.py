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


def test_multiple_config_files():
    values = run('testing/configA.yaml', 'testing/configC.yaml')

    assert {
        'SECRET_TOKEN=configA',
        'SECRET_APIKEY=configC',
    } == set(values)
    assert_not_in_environment()


def test_conflicting_values():
    values = run('testing/configA.yaml', 'testing/configB.json')

    assert values == ['SECRET_TOKEN=configB']
    assert_not_in_environment()


def test_nested_values():
    values = run('testing/configD.yaml')
    
    assert values == ['SECRET_NESTED={"value":"apikey"}']
    assert_not_in_environment()


def test_custom_prefix():
    values = run('--prefix', 'custom', 'testing/configA.yaml', prefix='CUSTOM')

    assert values == ['CUSTOM_TOKEN=configA']
    assert_not_in_environment()


def run(*configs, prefix='SECRET'):
    with tempfile.NamedTemporaryFile() as f:
        argv = [
            'prog',
            *configs,
            '--',
            os.path.join(os.path.dirname(__file__), '../testing/check_user.sh'),
            f.name,
            prefix,
        ]

        with mock.patch('sys.argv', argv):
            main(argv[1:])

        return f.read().decode('utf-8').splitlines()


def assert_not_in_environment(prefix='SECRET'):
    # Secrets should only reside in the subprocess.
    secrets = list(
        filter(
            lambda x: x.startswith(f'{prefix}_'),
            os.environ,
        )
    )
    assert not secrets
    with tempfile.NamedTemporaryFile() as f:
        subprocess.call(
            ' '.join([
                os.path.join(os.path.dirname(__file__), '../testing/check_user.sh'),
                f.name,
                prefix,
            ]),
            shell=True,
        )

        assert not f.read()


class TestUsage:
    def test_throws_error_on_no_command(self):
        with pytest.raises(argparse.ArgumentTypeError):
            main('testing/configA.yaml'.split())

    def test_prefix_must_not_be_null(self):
        argv = [
            'prog',
            '--prefix',
            '',
            'testing/configA.yaml',
            '--',
            'blah',
        ]

        with mock.patch('sys.exit') as m, mock.patch('sys.argv', argv):
            main(argv[1:])

        assert m.called
