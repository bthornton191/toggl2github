import re
from typing import Dict
import requests

GH_GRAPHQL_URL = 'https://api.github.com/graphql'


def get_project_node_id(user, token, project_number):

    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json',
    }

    payload = {
        'query': f'query{{user(login: "{user}") {{projectV2(number: {project_number}){{id}}}}}}'
    }

    # Send the POST request
    response = requests.post(GH_GRAPHQL_URL, headers=headers, json=payload)

    # Check the response status code
    if response.status_code != 200:
        raise Exception(f'Request failed with status code {response.status_code}')
    elif 'errors' in response.json():
        raise Exception(response.json()['errors'])

    return response.json()['data']['user']['projectV2']['id']


def get_project_issues(user, token, project_number):
    project_id = get_project_node_id(user, token, project_number)

    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json',
    }

    query = '''
    query {{
        node(id: "{project_id}") {{
            ... on ProjectV2 {{
                items(first: 100) {{
                    nodes {{
                        id
                        fieldValues(first: 100) {{
                            nodes {{
                                ... on ProjectV2ItemFieldTextValue {{
                                    text
                                    field {{
                                        ... on ProjectV2FieldCommon {{
                                            name
                                        }}
                                    }}
                                }}
                                ... on ProjectV2ItemFieldDateValue {{
                                    date
                                    field {{
                                        ... on ProjectV2FieldCommon {{
                                            name
                                        }}
                                    }}
                                }}
                                ... on ProjectV2ItemFieldSingleSelectValue {{
                                    name
                                    field {{
                                        ... on ProjectV2FieldCommon {{
                                            name
                                        }}
                                    }}
                                }}
                                ... on ProjectV2ItemFieldNumberValue {{
                                    number
                                    field {{
                                        ... on ProjectV2FieldCommon {{
                                            name
                                        }}
                                    }}
                                }}
                            }}
                        }}
                        content {{
                            ... on Issue {{
                                url
                            }}
                        }}
                    }}
                }}
            }}
        }}
    }}
    '''

    payload = {
        'query': query.format(project_id=project_id)
    }

    response = requests.post(GH_GRAPHQL_URL, headers=headers, json=payload)

    if response.status_code != 200:
        raise Exception(f'Request failed with status code {response.status_code}')
    elif 'errors' in response.json():
        raise Exception(response.json()['errors'])

    issues = []
    for item in response.json()['data']['node']['items']['nodes']:
        item: Dict[str, dict]
        issue = {'id': item['id']}
        for field in (f for f in item['fieldValues']['nodes'] if f != {}):
            field: dict
            issue[field.pop('field')['name']] = list(field.values())[0]

        for k, v in item.get('content', {}).items():
            issue[k] = v

        issues.append(issue)

        if 'url' in issue and (match := re.match(r'.*/issues/(\d+)', issue['url'])):
            match: re.Match
            issue['Number'] = int(match.group(1))
        else:
            issue['Number'] = None

    return issues


def get_project_fields(user, token, project_number):
    project_id = get_project_node_id(user, token, project_number)

    # Set the request headers
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json',
    }

    # Set the request payload
    payload = {
        'query': (f'query{{ node(id: "{project_id}") {{ '
                  '... on ProjectV2 { fields(first: 100) { nodes { '
                  '... on ProjectV2Field { id name } '
                  '... on ProjectV2IterationField { id name configuration { iterations { startDate id }}} '
                  '... on ProjectV2SingleSelectField { id name options { id name }}}}}}}')
    }

    # Send the POST request
    response = requests.post(GH_GRAPHQL_URL, headers=headers, json=payload)

    # Check the response status code
    if response.status_code != 200:
        raise Exception(f'Request failed with status code {response.status_code}')
    elif 'errors' in response.json():
        raise Exception(response.json()['errors'])

    # Print the response content
    return response.json()['data']['node']['fields']['nodes']


def get_project_field_id(user, token, project_number, field_name):
    fields = get_project_fields(user, token, project_number)
    return next((f['id'] for f in fields if f['name'].lower() == field_name.lower()), None)


def get_project_issue_id(user, token, project_number, title):
    return next((issue['id'] for issue in get_project_issues(user, token, project_number)
                if issue['Title'] == title), None)


def create_issue(user, token, project_number, title, body, field_values: Dict[str, str]):
    ...


def delete_issue(user, token, project_number, title):
    ...


def set_field_value(user, token, project_number, issue_name, field_name, field_type, value):

    project_id = get_project_node_id(user, token, project_number)
    field_id = get_project_field_id(user, token, project_number, field_name)
    issue_id = get_project_issue_id(user, token, project_number, issue_name)

    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json',
    }

    query = '''
    mutation {{
        updateProjectV2ItemFieldValue( 
        input: {{ 
            projectId: "{project_id}" 
            itemId: "{issue_id}" 
            fieldId: "{field_id}" 
            value: {{ 
                {field_type}: {value}
            }}
        }}) 
        {{ projectV2Item {{ id }} }}
    }}'''

    if field_type in ['text', 'date'] or value == '':
        value = f'"{value}"'

    payload = {'query': query.format(project_id=project_id,
                                     issue_id=issue_id,
                                     field_id=field_id,
                                     field_type=field_type,
                                     value=value)}

    response = requests.post(GH_GRAPHQL_URL, headers=headers, json=payload)

    if response.status_code != 200:
        raise Exception(f'Request failed with status code {response.status_code}')
    elif 'errors' in response.json():
        raise Exception(response.json()['errors'])

    return response.json()
