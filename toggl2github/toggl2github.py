
import logging
import re

import pandas as pd

from toggl2github.githubpy import get_project_issues, set_field_value
from toggl2github.toggl import get_project

from .config import get_config

LOG = logging.getLogger(__name__)


def sync(toggl_project_name: str, github_project_number: int):
    """For each task in the Toggl project that has a name identical an issue in the  Github project 
    sets the `time spent` field of the Github issue to the duration of the task."""

    (workspace_id, toggl_user, gh_user, gh_token) = get_config(['toggl_workspace_id',
                                                                'toggl_user',
                                                                'gh_user',
                                                                'gh_token']).values()

    toggl_project = get_project(toggl_project_name, workspace_id, toggl_user)
    df_gh = pd.DataFrame.from_records(get_project_issues(gh_user,
                                                         gh_token,
                                                         github_project_number))

    for num, desc, dur in [(int(match.group(1)), match.group(2), task.duration)
                           for task in toggl_project.tasks
                           if (match := re.match(r'#(\d+) (.+)', task.description, re.I))]:
        df = df_gh[(df_gh['Number'] == num) & (df_gh['Title'].str.lower() == desc.lower())]

        if df.empty:
            LOG.info(f'No issue found for {desc}')

        elif 'Assignees' not in df.columns:
            LOG.info(f'Skipping {desc} - No assignees metadata')

        elif gh_user in df['Assignees'].values[0] and len(df['Assignees'].values[0]) > 1:
            LOG.info(f'Skipping {desc} - More than one person is assigned')

        elif gh_user not in df['Assignees'].values[0]:
            LOG.info(f'Skipping {desc} - Not assigned to {gh_user}')

        else:
            LOG.info(f'{desc} - {dur/3600:.1f} hours')
            set_field_value(gh_user,
                            gh_token,
                            github_project_number,
                            df['Title'].values[0],
                            'Time Spent',
                            'number',
                            round(dur/3600))
