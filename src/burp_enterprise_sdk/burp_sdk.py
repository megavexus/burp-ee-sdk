from burp_enterprise_sdk.connection import Connection
from burp_enterprise_sdk.endpoints import SitesApi, ScansApi, IssuesApi

class BurpApi(object):

    def __init__(self, url, token):
        self._version = "0.1"
        self.url = url
        self.token = token
        self.connection = Connection(url, token, self._version)

        self.sites = SitesApi(self.connection)
        self.scans = ScansApi(self.connection)
        self.issues = IssuesApi(self.connection)

    def get_permissions(self):
        uri = "/api-internal/permissions"
        res = self.connection.get_request(uri)
        return res.get("data")