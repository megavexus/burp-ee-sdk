from requests import request, Session
import json

class Connection(object):
    def __init__(self, url, token, version):
        self._version = version
        self.url = url
        self.token = token
        self.session = Session()
        self.session.headers.update({'Authorization': self.token})
        self.session.headers.update({'Accept': "*/*"})
        self.session.headers.update({'Accept-Language': "en-US,en;q=0.5"})
        self.session.headers.update({'Content-Type': "application/json"})

    def get_request(self, uri, params={}, data={}, headers={}):
        url = self.make_url(uri)
        response = self.session.get(url, params=params, data=data, headers=headers)
        return self.process_response(response)
        

    def post_request(self, uri, params={}, data={}, headers={}):
        url = self.make_url(uri)
        payload = json.dumps(data)
        if headers:
            for key, value in headers.items():
                self.session.headers[key] = value

        response = self.session.post(url, params=params, data=payload, headers=headers)
        return self.process_response(response)
        

    def put_request(self, uri, params={}, data={}, headers={}):
        url = self.make_url(uri)
        if data:
            payload = json.dumps(data)
        else:
            payload = None

        if headers:
            for key, value in headers.items():
                self.session.headers[key] = value

        response = self.session.put(url, params=params, data=payload, headers=headers)
        return self.process_response(response)

    def delete_request(self, uri, params={}, data={}, headers={}):
        url = self.make_url(uri)
        response = self.session.delete(url, params=params, data=data, headers=headers)
        return response.status_code == 204

    def make_url(self, uri):
        url = "{}{}".format(self.url, uri)
        return url

    def process_response(self, response):
        if response.status_code > 400:
            response.raise_for_status()
        else:
            ret = {
                "code": response.status_code,
                "reason": response.reason
            }
            if len(response.content):
                ret["data"] = response.json()
            return ret