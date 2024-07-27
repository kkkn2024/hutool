import json
import os.path


def get_cur_dir():
    return os.path.dirname(os.path.realpath(__file__))


def get_config():
    with open(os.path.join(get_cur_dir(), 'config.json'), 'r') as f:
        config = json.load(f)
    return config
