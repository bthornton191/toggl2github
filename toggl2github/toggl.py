from __future__ import annotations
from datetime import datetime, timezone
from typing import List
import requests
from base64 import b64encode
from .config import get_config

API_ENDPOINT = 'https://api.track.toggl.com/api/v9'


def get_auth(user: str):
    toggl_password = get_config(['toggl_password']).get('toggl_password')

    if not toggl_password:
        raise ValueError('You must set the toggl_password in the config file')
    
    return b64encode(f'{user}:{toggl_password}'.encode()).decode('ascii')


def get_all_projects(workspace_id: int, user: str):
    return [Project(user, **r) for r in
            requests.get(url=f'{API_ENDPOINT}/workspaces/{workspace_id}/projects',
                         headers={'content-type': 'application/json',
                                  'Authorization': f'Basic {get_auth(user)}'}).json()]


def get_project(name: str, workspace_id: int, user: str):
    return next((p for p in get_all_projects(workspace_id, user)
                 if p.name.lower() == name.lower()), None)


class Project:
    def __init__(self, user, **kwargs):
        self.id = kwargs.get('id', None)
        self.workspace_id = kwargs.get('workspace_id', None)
        self.client_id = kwargs.get('client_id', None)
        self.name = kwargs.get('name', None)
        self.is_private = kwargs.get('is_private', None)
        self.active = kwargs.get('active', None)
        self.at = kwargs.get('at', None)
        self.created_at = kwargs.get('created_at', None)
        self.server_deleted_at = kwargs.get('server_deleted_at', None)
        self.color = kwargs.get('color', None)
        self.billable = kwargs.get('billable', None)
        self.template = kwargs.get('template', None)
        self.auto_estimates = kwargs.get('auto_estimates', None)
        self.estimated_hours = kwargs.get('estimated_hours', None)
        self.estimated_seconds = kwargs.get('estimated_seconds', None)
        self.rate = kwargs.get('rate', None)
        self.rate_last_updated = kwargs.get('rate_last_updated', None)
        self.currency = kwargs.get('currency', None)
        self.recurring = kwargs.get('recurring', None)
        self.template_id = kwargs.get('template_id', None)
        self.recurring_parameters = kwargs.get('recurring_parameters', None)
        self.fixed_fee = kwargs.get('fixed_fee', None)
        self.actual_hours = kwargs.get('actual_hours', None)
        self.actual_seconds = kwargs.get('actual_seconds', None)
        self.start_date = kwargs.get('start_date', None)
        self.status = kwargs.get('status', None)
        self.wid = kwargs.get('wid', None)
        self.cid = kwargs.get('cid', None)
        self.guid = kwargs.get('guid', None)
        self.json = kwargs
        self.user = user

    def __repr__(self) -> str:
        return f'<Project>: {self.name}'

    def get_task(self, name: str):
        return next((t for t in self.tasks if t.description.lower() == name.lower()), None)

    @property
    def entries(self) -> List[Entry]:
        response = requests.get(url='https://api.track.toggl.com/api/v9/me/time_entries',
                                headers={'content-type': 'application/json',
                                         'Authorization': f'Basic {get_auth(self.user)}'})

        if response.status_code != 200:
            raise Exception(f'Error: {response.status_code} - {response.text}')

        return [Entry(**r) for r in
                response.json()
                if r.get('pid', None) == self.id]

    @property
    def tasks(self) -> List[Task]:
        unique_names = set(e.description for e in self.entries)
        return [Task([e for e in self.entries if e.description == name]) for name in unique_names]


class Entry:
    def __init__(self, **kwargs):
        self.id = kwargs.get('id', None)
        self.workspace_id = kwargs.get('workspace_id', None)
        self.project_id = kwargs.get('project_id', None)
        self.billable = kwargs.get('billable', None)
        self.start = datetime.fromisoformat(kwargs.get('start', None))
        self.stop = (datetime.fromisoformat(kwargs.get('stop', None))
                     if kwargs.get('stop', None)
                     else datetime.now(timezone.utc))
        # self.duration = kwargs.get('duration', None)
        self.description = kwargs.get('description', None)
        self.tags = kwargs.get('tags', None)
        self.tag_ids = kwargs.get('tag_ids', None)
        self.duronly = kwargs.get('duronly', None)
        self.at = kwargs.get('at', None)
        self.server_deleted_at = kwargs.get('server_deleted_at', None)
        self.user_id = kwargs.get('user_id', None)
        self.uid = kwargs.get('uid', None)
        self.wid = kwargs.get('wid', None)
        self.pid = kwargs.get('pid', None)
        self.json = kwargs

    def __repr__(self) -> str:
        return f'<Entry>: {self.description} | {self.start.date()} - {self.stop.date()} | {self.duration/3600:.1f} hrs'

    def __hash__(self) -> int:
        return hash(self.id)

    def __eq__(self, other: Entry) -> bool:
        return self.id == other.id

    @property
    def duration(self) -> int:
        return int((self.stop - self.start).total_seconds())


class Task:
    def __init__(self, entries: List[Entry]):
        self.entries = entries
        self.id = entries[0].id
        self.workspace_id = entries[0].workspace_id
        self.project_id = entries[0].project_id
        self.billable = entries[0].billable
        self.description: str = entries[0].description
        self.tags = entries[0].tags
        self.tag_ids = entries[0].tag_ids
        self.duronly = entries[0].duronly
        self.at = entries[0].at
        self.server_deleted_at = entries[0].server_deleted_at
        self.user_id = entries[0].user_id
        self.uid = entries[0].uid
        self.wid = entries[0].wid
        self.pid = entries[0].pid

    @property
    def start(self) -> datetime:
        return min(e.start for e in self.entries)

    @property
    def stop(self) -> datetime:
        return max(e.stop for e in self.entries if e.stop is not None)

    @property
    def duration(self) -> int:
        return int(sum(e.duration for e in self.entries))

    def __repr__(self) -> str:
        return f'<Task>: {self.description} | {self.start.date()} - {self.stop.date()} | {self.duration/3600:.1f} hrs'
