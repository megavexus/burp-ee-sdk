from requests import request, Session

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
        response = self.session.post(url, params=params, data=data, headers=headers)
        return self.process_response(response)

    def make_url(self, uri):
        url = "{}{}".format(self.url, uri)
        return url

    def process_response(self, response):
        if response.status_code > 400:
            response.raise_for_status()
        else:
            return {
                "code": response.status_code,
                "reason": response.reason,
                "data": response.json()
            }