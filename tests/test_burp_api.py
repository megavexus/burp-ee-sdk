import pytest


def test_login(burp_api):
    res = burp_api.get_permissions()
    assert 'global' in res