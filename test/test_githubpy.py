from math import isnan
import sys
import unittest
from pathlib import Path

import pandas as pd

from config import GH_TOKEN, GH_USER
from githubpy import create_issue, get_project_field_id, get_project_fields, set_field_value
from githubpy import get_project_issue_id, get_project_issues
from githubpy import get_project_node_id, delete_issue

sys.path.insert(0, str(Path(__file__).parent.parent))

TEST_PROJECT_NUMBER = 1


class TestGetProjectIssues(unittest.TestCase):

    def test_gets_correct_columns(self):
        df = pd.DataFrame.from_records(get_project_issues(GH_USER, GH_TOKEN, TEST_PROJECT_NUMBER))

        expected_columns = ['id',
                            'title',
                            'url',
                            'status',
                            'phase',
                            'target date',
                            'completed date',
                            'start date',
                            'number',
                            'time spent']
        actual_columns = df.columns.str.lower().tolist()
        self.assertCountEqual(expected_columns, actual_columns)


class TestCreateIssue(unittest.TestCase):
    ...


class TestSetFieldValue(unittest.TestCase):
    TEST_ISSUE_NAME = 'Phase 3B Project Work Plan'
    TEST_VALUE = 999

    def setUp(self) -> None:

        df = pd.DataFrame.from_records(get_project_issues(GH_USER, GH_TOKEN, TEST_PROJECT_NUMBER))
        self.current_value = df[df['Title'] == self.TEST_ISSUE_NAME]['Time Spent'].values[0]
        set_field_value(GH_USER,
                        GH_TOKEN,
                        TEST_PROJECT_NUMBER,
                        self.TEST_ISSUE_NAME,
                        'Time Spent',
                        'number',
                        self.TEST_VALUE)

    def test_field_value_set(self):
        df = pd.DataFrame.from_records(get_project_issues(GH_USER, GH_TOKEN, TEST_PROJECT_NUMBER))
        actual_value = df[df['Title'] == self.TEST_ISSUE_NAME]['Time Spent'].values[0]

        self.assertEqual(self.TEST_VALUE, actual_value)

    def tearDown(self) -> None:
        set_field_value(GH_USER,
                        GH_TOKEN,
                        TEST_PROJECT_NUMBER,
                        self.TEST_ISSUE_NAME,
                        'Time Spent',
                        'number',
                        self.current_value if not isnan(self.current_value) else 0)


if __name__ == '__main__':
    unittest.main()
