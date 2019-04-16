import pytest 

class TestSites():
    def test_list_sites(self, burp_api):
        sites = burp_api.sites.list()
        assert len(sites) > 0

    def test_list_plain_sites(self, burp_api):
        sites = burp_api.sites.list_plain()
        sites_normal = burp_api.sites.list()
        assert len(sites) > len(sites_normal)

    @pytest.mark.parametrize('id, exists', (
        [1, True],
        [2, True],
        [7, True],
        [123, False],
        ["ASDFG", False],
        [9, True]
    ))
    def test_get_site_info(self, burp_api, id, exists):
        site = burp_api.sites.get(id)
        if exists:
            assert type(site) == dict
            assert site['id'] == str(id)
        else:
            assert site == {}

    @pytest.mark.parametrize('id, has_childrens', (
        [1, True],
        [123, False],
        ["ASDFG", False],
        [9, False]
    ))
    def test_get_folder_childrens(self, burp_api, id, has_childrens):
        sites = burp_api.sites.get_childrens(id)
        if has_childrens:
            assert type(sites) == list
            assert len(sites) > 0
        else:
            assert sites == []
    

    @pytest.mark.parametrize('search, expected', (
        ["XX", True],
        ["XAY", True],
        ["ASDF", True],
        ["ASDFGG", True],
        ["gato.com", True],
        [".com", True],
        ["POIUUYRDSADU SAHNDSAD", False],
        [9, False]
    ))
    def test_search_site(self, burp_api, search, expected):
        sites = burp_api.sites.search(search)
        have_sites = len(sites) > 0
        assert have_sites == expected

    def test_create_folder(self, burp_api):
        folder_name = "test_create"
        data = burp_api.sites.create_folder(folder_name)
        assert 'id' in data
        burp_api.sites.delete(data['id'])

    def test_create_subfolder(self, burp_api):
        folder_name = "test_create"
        data = burp_api.sites.create_folder(folder_name)
        id_parent = data['id']
        folder_name = "test_create_subfolder"
        data = burp_api.sites.create_folder(folder_name, id_parent=id_parent)
        assert 'id' in data

        assert burp_api.sites.delete(id_parent)

    @pytest.mark.skip
    def test_create_site(self):
        pass
    
    @pytest.mark.skip
    def test_fail_create_site(self):
        pass

    @pytest.mark.skip
    def test_update_site(self):
        pass
    
    @pytest.mark.skip
    def test_update_site_fail(self):
        pass

    def test_delete_folder(self, burp_api):
        data = burp_api.sites.create_folder("test_delete")
        assert 'id' in data

        is_del = burp_api.sites.delete(data['id'])
        assert is_del == True

        data = burp_api.sites.get(data['id'])
        assert data == {}