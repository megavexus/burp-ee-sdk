from burp_enterprise_sdk.abstract import AbstractEndpointApi
from requests.exceptions import HTTPError
import logging
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
            logging.info("{} == {}".format(site_name, name))
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
            "version": null,
            "name": name
        }
        if id_parent:
            data['parent_id'] = id_parent
        
        ret = super.post(
            id=id_parent,
            data=data
        )
        return ret

    def create_site(self, name, id_parent, urls=[], excluded_urls=[], scan_configuration_ids = [], credentials = []):
        data = {
            "version": 0,
            "name": name,
            "parent_id": id_parent,
            "urls": urls,
            "excluded_urls": excluded_urls,
            "scan_configuration_ids": scan_configuration_ids,
            "credentials": [
                {
                    "label": credential['label'],
                    "password": credential['password'],
                    "admin": credential['admin'],
                } for credential in credentials
            ]
        }

        ret = super.post(
            id=id_parent,
            data=data
        )
        return ret
    
    def update_folder(self, id, name=None, id_parent=None):
        """

        """

    def update_site(self, id, name=None, id_parent=None, urls=[], excluded_urls=[], scan_configuration_ids = [], credentials = []):
        """
    
        """
        pass

    def delete(self, id):
        super.delete(id)