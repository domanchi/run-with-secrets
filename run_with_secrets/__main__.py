import argparse
import json
import os
import subprocess
import sys
from grp import getgrnam
from pwd import getpwnam
from typing import Callable
from typing import Dict
from typing import List
from typing import Optional

import yaml


def main(argv: Optional[List[str]] = None):
    args = parse_args(argv)

    env = {}
    for filepath in args.config:
        additions = process_file(filepath)
        if not additions:
            continue

        duplicate_keys = set(env.keys()) & set(additions.keys())
        if duplicate_keys:
            for key in duplicate_keys:
                print(
                    f'warning: duplicate key found. using "{key}" from {filepath}',
                    file=sys.stderr,
                )

        env.update(additions)

    try:
        subprocess.call(
            ' '.join(args.command),
            shell=True,
            env=env,
            preexec_fn=set_user(args.user),
        )
    except subprocess.SubprocessError as e:
        if not str(e) == 'Exception occurred in preexec_fn.':
            raise

        print('error: unable to change user. are you root?')


def parse_args(argv: Optional[List[str]] = None):
    parser = argparse.ArgumentParser(
        usage='run-with-secrets [-h] [-v] config [config ...] -- command',
    )
    parser.add_argument(
        '-v',
        '--verbose',
        action='count',
    )
    parser.add_argument(
        '-u',
        '--user',
        type=str,
        help=(
            'Specifies the user to run the command. This is handy when you want to '
            'run it as a specific user, that would not normally have access to the '
            'credentials file. Example: user[:group]'
        ),
    )
    parser.add_argument(
        'config',
        nargs='+',
    )

    output = parser.parse_args(argv)
    for index, parameter in enumerate(sys.argv[1:][::-1]):
        # argparse removes the first `--` parameter, and lumps it altogether with
        # config (since nargs='+'). Therefore, we count backwards until we hit this
        # parameter, and we know how many args in the command.
        if parameter == '--':
            break
    else:
        raise argparse.ArgumentTypeError('Unspecified command.')
    
    output.command = output.config[index:]
    output.config = output.config[:index]

    return output


def process_file(filepath: str, prefix: str = 'SECRET') -> Dict[str, str]:
    try:
        with open(filepath) as f:
            data = yaml.safe_load(f)
    except OSError as e:
        print('warning:', str(e), file=sys.stderr)
        return

    output = {}
    for key, value in data.items():
        if isinstance(value, dict):
            value = json.dumps(value, separators=(',', ':',))

        output[f'{prefix.upper()}_{key.upper()}'] = str(value)
    
    return output


def set_user(user: str) -> Callable:
    if ':' in user:
        username, groupname = user.split(':')
        uid = getpwnam(username).pw_uid
        gid = getgrnam(groupname).gr_gid
    else:
        uid = getpwnam(user).pw_uid
        gid = None

    def demote():
        # setgid needs to come first, otherwise, the new user won't have
        # the permission to change the group.
        if gid:
            os.setgid(gid)

        os.setuid(uid)
    
    return demote


if __name__ == '__main__':
    try:
        main()
    except argparse.ArgumentTypeError as e:
        print('error:', str(e), file=sys.stderr)
