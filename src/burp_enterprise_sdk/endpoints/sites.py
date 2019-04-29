from burp_enterprise_sdk.abstract import AbstractEndpointApi
from requests.exceptions import HTTPError

class SitesApi(AbstractEndpointApi):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ENDPOINT_GET = "/api-internal/sites/"
        self.ENDPOINT_LIST = "/api-internal/sites"
        self.ENDPOINT_POST = "/api-internal/sites/"
        self.ENDPOINT_DELETE = "/api-internal/sites/"

    def get(self, *args, **kwargs):
        try:
            ret = super().get(*args, **kwargs)
        except HTTPError as ex:
            status_code = ex.response.status_code
            if status_code == 404:
                return {}
            else:
                raise

        if ret.get('code') == 28:
            return {}
        
        if 'trees' in ret:
            ret = ret['trees']
        return ret


    def list_plain(self):
        list_elems = self.list()
        listed = self.extract_childrens(list_elems)
        return listed


    def extract_childrens(self, list_elems):
        res = []
        for elem in list_elems:
            res.append(elem)
            childs = elem.get('children')
            childs_extract = self.extract_childrens(childs)
            res = res + childs_extract
        return res    


    def search(self, name, exact_match = False):
        tree = self.list_plain()
        results = []
        name = str(name).lower().strip()
        for site in tree:
            site_name = site['name'].lower().strip()
            if exact_match:
                if name == site_name:
                    return site

            elif site_name.find(name) != -1:
                results.append(site)
      
        return results

    def get_childrens(self, id):
        sites = self.list_plain()
        target_site = {}
        for site in sites:
            if site['id'] == str(id):
                target_site = site
                break

        childrens = target_site.get('children', [])
        return childrens

    def create_folder(self, name, id_parent=None):
        data = {
            "name": name,
            "version": 0
        }

        if id_parent:
            data['parent_id'] = id_parent

        if id_parent == None:
            id_parent = ""

        ret = super().post(
            id=id_parent,
            data=data
        )
        return ret

    def create_site(self, name, urls, id_parent=None, excluded_urls=[], scan_configuration_ids = [], credentials = []):
        """
        Scan_config_ids:
           - minimize false positives: 06f9a9d4-6e5a-48e1-8305-c6c45775b5f3
           - critical only: 79f11341-7d81-4a37-a090-4169eff55cd7
        """
        if type(urls) != list or len(urls) == 0:
            raise Exception("There must be URLS in array format ['url1', 'url2']: {}".format(urls))   
        
        data = {
            "version": 0,
            "name": name,
            "parent_id": id_parent,
            "urls": urls,
            "excluded_urls": excluded_urls,
            "scan_configuration_ids": scan_configuration_ids
        }
        if credentials:
            data["credentials"] = [
                {
                    "label": credential['label'],
                    "password": credential['password'],
                    "username": credential['username']
                } for credential in credentials
            ]

        ret = super().post(
            id=id_parent,
            data=data
        )

        return ret


    def update_folder(self, id, name=None, id_parent=None):
        return self.update_site(id, name, id_parent)


    def update_site(self, id, name=None, id_parent=None, urls=None, excluded_urls=None, scan_configuration_ids = None, credentials = None):
        existent_data = self.get(id)
        data = {}

        if name:
            data["name"] = name

        if id_parent:
            data["id_parent"] = id_parent

        if urls:
            if type(urls) != list:
                raise TypeError("Type of urls parameter must be a list of urls")
            data["urls"] = urls

        if excluded_urls:
            if type(excluded_urls) != list:
                raise TypeError("Type of excluded_urls parameter must be a list of urls")
            data["excluded_urls"] = excluded_urls

        if scan_configuration_ids:
            if type(scan_configuration_ids) != list:
                raise TypeError("Type of scan_configuration_ids parameter must be a list of ids")
            data["scan_configuration_ids"] = scan_configuration_ids

        if credentials != None:
            if type(credentials) != list:
                raise TypeError("Type of credentials parameter must be a list of credentials")
            data["credentials"] = [
                {
                    "label": credential['label'],
                    "password": credential['password'],
                    "username": credential['username']
                } for credential in credentials
            ]

        ret = super().post(
            id=id,
            data=data,
            is_update=True
        )
        return ret

"""
    def _get_page_scans(self, id, page=0):
        uri = "{}{}/scan_summaries".format(self.ENDPOINT_GET, id)
        params = {
            "page": page
        }
        ret = super().get(
            uri=uri,
            params=params
        )
        return ret

    def get_scans(self, id):
        ret = self._get_page_scans(id)
        page = ret["page"]
        page_size = ret["page_size"]
        results = ret['rows']
        num_scans = len(results)
        while num_scans == page_size:
            page += 1
            ret = self._get_page_scans(id, page)
            results = results + ret['rows']
            num_scans = len(ret['rows'])

        return results
"""