from .connection import Connection

class AbstractEndpointApi(object):
    ENDPOINT_GET = None
    ENDPOINT_LIST = None
    ENDPOINT_POST = None
    ENDPOINT_DELETE = None

    def __init__(self, connection:Connection):
        self.connection = connection

    def list(self, *args, **kwargs):
        return self.get()

    def get(self, id=None, uri=None, params=None):
        if not uri:
            if not self.ENDPOINT_GET:
                raise NotImplementedError()

            uri = self.ENDPOINT_GET
            if id != None:
                uri += str(id)
        
        res = self.connection.get_request(uri, params)
        return res.get("data")

    def post(self, id, data, id_parent=None, is_update=False):
        if not self.ENDPOINT_POST:
            raise NotImplementedError()
        uri = self.ENDPOINT_POST + str(id)
        headers = None
        if is_update:
            headers = {"Content-Type": "application/merge-patch+json"}
        res = self.connection.post_request(uri, data=data, headers=headers)
        return res.get("data")


    def put(self, id, uri=None, data=None):
        if not uri and not self.ENDPOINT_PUT:
            raise NotImplementedError()
        
        if not uri:
            uri = self.ENDPOINT_PUT + str(id)

        res = self.connection.post_request(uri, data=data, headers=headers)
        return res.get("data")


    def delete(self, id):
        if not self.ENDPOINT_DELETE:
            raise NotImplementedError()
        uri = self.ENDPOINT_DELETE + str(id)
        res = self.connection.delete_request(uri)
        return res
