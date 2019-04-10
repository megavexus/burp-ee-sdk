import pytest
import configparser
import os
from burp_enterprise_sdk import BurpApi

@pytest.fixture()
def connection_data():
    mypath = os.path.dirname(os.path.abspath(__file__))
    config_file = os.path.join(mypath, 'config', 'burp.conf')
    config = configparser.ConfigParser()
    config.read(config_file)

    data = {
        'host': config['burp'].get('host'),
        'token': config['burp'].get('token'),
    }
    return data

@pytest.fixture()
def burp_api(connection_data):

    burp_api = BurpApi(connection_data['host'], connection_data['token'])
    return burp_api
