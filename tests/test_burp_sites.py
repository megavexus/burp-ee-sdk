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


    @pytest.mark.parametrize("id_parent, name, urls, excluded_url, scan_configuration_ids", [
        (7, "test_1", ["www.cats.com"], [], []),
        (7, "test_2", ["www.cats.com", "www.cats.com"], [], []),
        (7, "test_3", ["www.cats.com", "www.cats.com"], ["www.dogs.com"], []),
        (7, "test_4", ["www.cats.com", "www.dogs.com"], [], ["06f9a9d4-6e5a-48e1-8305-c6c45775b5f3"]),
    ])
    def test_create_site(self, burp_api, id_parent, name, urls, excluded_url, scan_configuration_ids):
        data = burp_api.sites.create_site(name, urls, id_parent, excluded_url, scan_configuration_ids)        
        assert 'id' in data
        assert burp_api.sites.delete(data['id'])

    @pytest.mark.parametrize("credentials", [
        ([]),
        ([
            {"label": "perro", "username": "admin", "password": "perrete"}
        ]),
        ([
            {"label": "perro", "username": "admin", "password": "perrete"},
            {"label": "perro2", "username": "admin2", "password": "perrete"}
        ])
    ])
    def test_create_site_w_credentials(self, burp_api, credentials):
        name = "site_test_cred"
        id_parent = 7
        urls = ['www.dogs.com']
        excluded_url = []
        scan_configuration_ids = []
        data = burp_api.sites.create_site(name, urls, id_parent, excluded_url, scan_configuration_ids, credentials)        
        assert 'id' in data
        assert burp_api.sites.delete(data['id'])
        assert credentials == data['credentials']

    @pytest.mark.parametrize(
        "name, urls, excluded_url, scan_configuration_ids, credentials",
        [
            ("TEST_JAVI", None, None, None, None),
            (None, ["perro.com"], None, None, None),
            (None, None, ["www.gato.com/err"], None, None),
            (None, None, ["www.gato.com/err"], ["06f9a9d4-6e5a-48e1-8305-c6c45775b5f3"], None),
            (None, None, None, None, [{"label": "perro", "username": "admin", "password": "perrete"}]),
        ]
    )
    def test_update_site(self, burp_api, name, urls, excluded_url, scan_configuration_ids, credentials):
        name_orig = "site_test_update"
        id_parent = 7
        urls_orig = ['www.dogs.com']
        excluded_url_orig = []
        scan_configuration_ids_orig = []
        data = burp_api.sites.create_site(name_orig, urls_orig, id_parent, excluded_url_orig, scan_configuration_ids_orig)        
        if not 'id' in data:
            data = burp_api.sites.search(name_orig)[0]

        burp_api.sites.update_site(data['id'], name=name, urls=urls, excluded_urls=excluded_url, scan_configuration_ids=scan_configuration_ids, credentials=credentials)
        new_data = burp_api.sites.get(data['id'])
        assert 'id' in new_data
        assert burp_api.sites.delete(data['id'])

        if name != None:
            assert new_data['name'] == name
        else:
            assert new_data['name'] == data['name']

        if urls != None:
            assert new_data['urls'] == urls
        else:
            assert new_data['urls'] == data['urls']

        if excluded_url != None:
            assert new_data['excluded_urls'] == excluded_url
        else:
            assert new_data['excluded_urls'] == data['excluded_urls']

        if scan_configuration_ids != None:
            assert new_data['scan_configuration_ids'] == scan_configuration_ids
        else:
            assert new_data['scan_configuration_ids'] == data['scan_configuration_ids']

        if credentials != None:
            assert new_data['credentials'] == credentials
        else:
            assert new_data['credentials'] == data['credentials']


    def test_delete_folder(self, burp_api):
        data = burp_api.sites.create_folder("test_delete")
        assert 'id' in data

        is_del = burp_api.sites.delete(data['id'])
        assert is_del == True

        data = burp_api.sites.get(data['id'])
        assert data == {}