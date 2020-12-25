import json 
from bunch import Bunch

def get_config_from_json(json_file):
    """Gets the config data from json file"""
    with open(json_file, 'r') as config_file:
        config_dict = json.load(config_file)
    config = Bunch(config_dict)
    return config
