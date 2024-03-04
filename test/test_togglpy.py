import unittest

from config import USER, WORKSPACE_ID
from toggl2github.toggl import Project, get_all_projects, get_project

TEST_PROJECT_NAME = 'NNL'


class TestTogglpy(unittest.TestCase):

    def test_get_all_projects(self):
        project = get_all_projects(WORKSPACE_ID, USER)[0]
        self.assertTrue(isinstance(project, Project))

    def test_get_project(self):
        self.assertEqual(get_project(TEST_PROJECT_NAME, WORKSPACE_ID, USER).name, TEST_PROJECT_NAME)

    def test_task_duration(self):
        """Tests that the duration of a task is equal to the sum of the duration of it's entries."""
        project = get_project(TEST_PROJECT_NAME, WORKSPACE_ID, USER)
        for task in project.tasks:
            self.assertEqual(task.duration, sum([entry.duration for entry in task.entries]))

    def test_all_tasks_have_unique_names(self):
        """Tests that all tasks have unique names."""
        project = get_project(TEST_PROJECT_NAME, WORKSPACE_ID, USER)
        task_names = [task.description for task in project.tasks]
        self.assertEqual(len(task_names), len(set(task_names)))

    def test_all_entries_of_same_name_are_in_one_task(self):
        """Tests that all entries of the same name are in one task."""
        project = get_project(TEST_PROJECT_NAME, WORKSPACE_ID, USER)

        tasks = {task.description: task for task in project.tasks}
        for entry in project.entries:
            task = tasks.get(entry.description, None)
            self.assertTrue(task is not None)
            self.assertTrue(entry in task.entries)
