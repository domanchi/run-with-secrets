import argparse
import os
import subprocess
import sys
from typing import Dict
from typing import List
from typing import Optional

import yaml


def main(argv: Optional[List[str]] = None):
    args = parse_args(argv)

    env = {}
    for filepath in args.config:
        env.update(process_file(filepath))

    subprocess.call(' '.join(args.command), shell=True, env=env)


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
        'config',
        nargs='+',
    )

    output = parser.parse_args(argv)
    for index, parameter in enumerate(sys.argv[1:]):
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
        output[f'{prefix.upper()}_{key.upper()}'] = value
    
    return output


if __name__ == '__main__':
    try:
        main()
    except argparse.ArgumentTypeError as e:
        print('error:', str(e), file=sys.stderr)