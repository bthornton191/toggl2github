import logging
from .toggl2github import sync
from .config import set_config
import argparse
import sys


def main():

    parser = argparse.ArgumentParser(description='Sync Toggl project with Github project')

    subparsers = parser.add_subparsers(dest='command')

    sync_parser = subparsers.add_parser('sync')

    sync_parser.add_argument('toggl_project_name',
                             help='The name of the Toggl project')
    sync_parser.add_argument('github_project_number',
                             help='The number of the Github project',
                             type=int)

    config_parser = subparsers.add_parser('config')
    config_parser.add_argument('--gh_user', help='Github user')
    config_parser.add_argument('--gh_token', help='Github token')
    config_parser.add_argument('--toggl_user', help='Toggl user')
    config_parser.add_argument('--toggl_password', help='Toggl password')
    config_parser.add_argument('--toggl_workspace_id', help='Toggl workspace id')

    args = parser.parse_args()

    if args.command == 'sync':
        sync(args.toggl_project_name, args.github_project_number)

    elif args.command == 'config':
        kwargs = {k: v for k, v in vars(args).items() if v}
        set_config(**kwargs)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    main()
