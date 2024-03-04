import json
import re
from pathlib import Path
from typing import Any, Dict, List

import keyring

CONFIG_FILE = Path.home() / '.toggl2github'

RE_PASSWORD = re.compile(r'password|pwd|pw|token|secret|pass|auth', re.I)


def set_config(**kwargs):
    """Sets the configuration values in a json in the users home directory. 

    # Passwords
    Behavior is different if the kw contains "password". In this case it uses the keyring library 
    to store the password in the system keyring. All password kw must be accompanied by a user kw.

    """
    for key in [k for k in kwargs if RE_PASSWORD.search(k)]:
        if RE_PASSWORD.sub('user', key) not in kwargs:
            raise ValueError(f'You must provide a user for the {key} password')

        keyring.set_password(service_name='toggl2github',
                             username=kwargs[RE_PASSWORD.sub('user', key)],
                             password=kwargs.pop(key))

    # Write the rest to a json file in the users home directory. Combine with the existing config
    config = {}
    if CONFIG_FILE.exists():
        with CONFIG_FILE.open('r') as f:
            config = json.load(f)

    config.update(kwargs)

    with CONFIG_FILE.open('w') as f:
        json.dump(config, f, indent=4)


def get_config(keys: List[str]) -> Dict[str, Any]:
    """Gets the configuration values from a json in the users home directory. 

    # Passwords
    Behavior is different if the kw contains "password". In this case it uses the keyring library 
    to store the password in the system keyring. All password kw must be accompanied by a user kw.

    """
    config = {}
    if CONFIG_FILE.exists():
        with CONFIG_FILE.open('r') as f:
            config = json.load(f)

    missing = [k for k in keys if k not in config]
    if missing:
        raise ValueError(f'The following keys are missing from {CONFIG_FILE}: '
                         + ', '.join(missing))

    for key in [k for k in keys if RE_PASSWORD.search(k)]:
        if RE_PASSWORD.sub('user', key) not in config:
            raise ValueError(f'You must have a {RE_PASSWORD.sub("user")} in the config '
                             f'file to retrieve {key} from the keyring.')

        config[key] = keyring.get_password(service_name='toggl2github',
                                           username=config[RE_PASSWORD.sub('user', key)])

    return {k: config[k] for k in keys}
