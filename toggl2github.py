
import logging
import re
import sys
import argparse

import pandas as pd

from config import GH_TOKEN, GH_USER, USER, WORKSPACE_ID
from githubpy import get_project_issues, set_field_value
from toggl import get_project

LOG = logging.getLogger(__name__)


def sync(toggl_project_name: str, github_project_number: int):
    """For each task in the Toggl project that has a name identical an issue in the  Github project 
    sets the `time spent` field of the Github issue to the duration of the task."""

    # TODO: Test this whole function

    toggl_project = get_project(toggl_project_name, WORKSPACE_ID, USER)
    df_gh = pd.DataFrame.from_records(get_project_issues(GH_USER,
                                                         GH_TOKEN,
                                                         github_project_number))

    for num, desc, dur in [(int(match.group(1)), match.group(2), t.duration)
                           for t in toggl_project.tasks
                           if (match := re.match(r'#(\d+) (.+)', t.description, re.I))]:

        if not (df := df_gh[(df_gh['Number'] == num) &
                            (df_gh['Title'].str.lower() == desc.lower())]).empty:

            set_field_value(GH_USER,
                            GH_TOKEN,
                            github_project_number,
                            df['Title'].values[0],
                            'Time Spent',
                            'number',
                            round(dur/3600))

            LOG.info(f'{desc} - {dur} hours')

        else:
            LOG.info(f'No issue found for {desc}')


def main():

    parser = argparse.ArgumentParser(description='Sync Toggl project with Github project')
    parser.add_argument('toggl_project_name',
                        help='The name of the Toggl project')
    parser.add_argument('github_project_number',
                        help='The number of the Github project',
                        type=int)

    args = parser.parse_args()

    sync(args.toggl_project_name, args.github_project_number)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    main()
