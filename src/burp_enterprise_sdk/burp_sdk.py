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


"""
- Crear una Folder o SITE:
<<< REQUEST
POST /api-internal/sites/<ID_PARENT>
Authorization: <TOKEN>
Accept: */*
Accept-Language: en-US,en;q=0.5
Content-Type: application/json

--<FOLDER>--
{"version":null,"name":"ENTIDAD_XY", "parent_id": "<ID_PARENT>"}

--<SITE>--
{
    "name": "gato2.com",
    "parent_id": "1",
    "version": N,
    "urls": ["gato.com"],
    "excluded_urls": [],
    "credentials": [{
        "password": "asdfg",
        "label": "1",
        "username": "asdfg"
    }],
    "scan_configuration_ids": [
        "06f9a9d4-6e5a-48e1-8305-c6c45775b5f3"
    ]
}


<<< RESPONSE
HTTP/1.1 201 Created

{"id":"7","name":"ENTIDAD_XAY","children":[],"version":0,"urls":[],"excluded_urls":[],"scan_configuration_ids":[],"credentials":[],"target":false,"ephemeral":false}

- Crear un Site:
<<< REQUEST
POST /api-internal/sites/<Folder_parent_id>
Authorization: <TOKEN>
Accept: */*
Accept-Language: en-US,en;q=0.5
Content-Type: application/json

{
    "name": "gato2.com",
    "parent_id": "1",
    "version": 1,
    "urls": ["gato.com"],
    "excluded_urls": [],
    "credentials": [{
        "password": "asdfg",
        "label": "1",
        "username": "asdfg"
    }],
    "scan_configuration_ids": ["06f9a9d4-6e5a-48e1-8305-c6c45775b5f3"]
}

<<< RESPONSE
HTTP/1.1 201 Created

{"id":"6","name":"ASDFGG","parent_id":"5","children":[],"version":5,"urls":["dsadsaads.es"],"excluded_urls":[],"scan_configuration_ids":[],"credentials":[],"target":true,"ephemeral":false}


- Editar un Site:
<<< REQUEST
POST /api-internal/sites/<SITE_ID>
Authorization: <TOKEN>
Accept: */*
Accept-Language: en-US,en;q=0.5
Content-Type: application/json

{Edit fields}

<<< RESPONSE
HTTP/1.1 204 No Content

- Programar un escaneo
POST /api-internal/schedule
Authorization: <TOKEN>
Accept: */*
Accept-Language: en-US,en;q=0.5
Content-Type: application/json

{"site_tree_node_id":"4","rrule":"FREQ=DAILY;INTERVAL=1","initial_run_time":null,"scan_configuration_ids":["06f9a9d4-6e5a-48e1-8305-c6c45775b5f3"]}

<<< RESPONSE

HTTP/1.1 201 Created

{"id":"3","site_tree_node_id":"4","site_tree_node_name":"gato.com","rrule":"FREQ\u003DDAILY;INTERVAL\u003D1","initial_run_time":"2019-04-10T06:59:33.338Z","scheduled_run_time":"2019-04-11T06:59:33.000Z","scan_configuration_ids":["06f9a9d4-6e5a-48e1-8305-c6c45775b5f3"],"has_run_more_than_once":false}


- Obtener resultados
<<< REQUEST
GET /api-internal/scans/2/issues/issue_type
Authorization: <TOKEN>
Accept: */*
Accept-Language: en-US,en;q=0.5
Content-Type: application/json

<<< RESPONSE
HTTP/1.1 200 OK

{"issue_type_summaries":[],"scan_delta":{"new_type_indexes":[],"resolved_type_indexes":[],"repeated_type_indexes":[],"regressed_type_indexes":[]}}
"""