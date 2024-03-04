import random
import string
from typing import List, Tuple
import unittest
import datetime
from unittest import mock
from unittest.mock import MagicMock, patch

from config import GH_TOKEN, GH_USER
from toggl2github import sync


class TestToggl2Github(unittest.TestCase):

    @patch('toggl2github.get_project')
    @patch('toggl2github.get_project_issues')
    @patch('toggl2github.set_field_value')
    def test_sync(self,
                  mock_set_field_value: MagicMock,
                  mock_get_project_issues: MagicMock,
                  mock_get_project: MagicMock) -> None:
        toggle_project_name: str = 'Test Toggl Project'
        github_project_name: str = 'Test Github Project'
        github_project_number: int = 123

        # Mocking the return values
        mock_issues, mock_tasks = mock_issues_and_tasks(GH_USER, github_project_name, 1)
        mock_get_project.return_value = MockTogglProject(mock_tasks)
        mock_get_project_issues.return_value = mock_issues

        sync(toggle_project_name, github_project_number)

        # Asserting that the set_field_value function is called with the correct arguments
        mock_set_field_value.assert_called_with(GH_USER,
                                                GH_TOKEN,
                                                github_project_number,
                                                mock_issues[0]['Title'],
                                                'Time Spent',
                                                'number',
                                                round(mock_tasks[0].duration/3600))


class MockTask:
    def __init__(self, description, duration):
        self.description = description
        self.duration = duration


class MockTogglProject:
    def __init__(self, mock_tasks: List[MockTask] = None):
        self.tasks: List[MockTask] = [] if mock_tasks is None else mock_tasks


class MockGithubIssue:
    def __init__(self, number, title):
        self.Number = number
        self.Title = title


def mock_issues_and_tasks(user: str, project_name: str, num: int) -> Tuple[List[dict],
                                                                           List[MockTask]]:
    mock_issues = [
        {
            'id': ''.join(random.choices(string.ascii_uppercase + string.ascii_lowercase, k=10)),
            'Title': ' '.join(''.join(random.choices(string.ascii_uppercase, k=random.randint(5, 10)))
                              for _ in range(random.randint(2, 5))).title(),
            'url': f'https://github.com/{user}/{project_name}/issues/' + str(number := random.randint(1, 1000)),
            'Status': random.choice(['Open', 'Closed']),
            'Phase': 'Phase' + str(random.randint(1, 10)),
            'Target Date': str(datetime.date.today() + datetime.timedelta(days=random.randint(1, 30))),
            'Completed Date': str(datetime.date.today() - datetime.timedelta(days=random.randint(1, 30))),
            'Start Date': str(datetime.date.today() - datetime.timedelta(days=random.randint(1, 30))),
            'Number': number,
            'Time Spent': random.randint(1, 10)
        }
        for _ in range(num)]

    mock_tasks = [MockTask(f'#{issue["Number"]} {issue["Title"]}',
                           issue['Time Spent'])
                  for issue in mock_issues]

    return mock_issues, mock_tasks


if __name__ == '__main__':
    unittest.main()
