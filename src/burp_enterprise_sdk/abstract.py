from .connection import Connection

class AbstractEndpointApi(object):
    def __init__(self, connection:Connection):
        self.connection = connection

    def list(self):
        pass

    def get(self, id):
        pass

    def post(self, id, data):
        pass

    def delete(self, id):
        pass

