import pytest
from requests.exceptions import HTTPError
from datetime import datetime
from burp_enterprise_sdk.endpoints.scans import ScanProgrammingException
class TestScans():
    
    def test_list_scans(self, burp_api):
        site_id = 9
        scans = burp_api.sites.list(site_id)
        assert len(scans) >= 1
        assert type(scans) == list

    @pytest.mark.parametrize("status_filters", [
        (["SUCCEEDED", "QUEUED"]),
        (["SUCCEEDED"]),
        (["SUCCEEDED", "QUEUED", "RUNNING"]),
        ([]),
    ])
    def test_list_scans_filters(self, burp_api, status_filters):
        scans = burp_api.scans.list(status_filters=status_filters)
        assert len(scans) > 0
        if len(status_filters) > 0:
            for scan in scans:
                assert scan['status'] in status_filters

    @pytest.mark.parametrize("scan_id, exists", [
        (97, True),
        (102, True),
        (5555, False),
        (-1, False),
    ])
    def test_get_scan(self, burp_api, scan_id, exists):
        scan = burp_api.scans.get(scan_id)
        if exists:
            assert scan['id'] == str(scan_id)
        else:
            assert scan['code'] == 41 # "Scan not found"

    @pytest.mark.parametrize("scan_id", [
        (None),
        (""),
        ("None"),
        ("null"),
        (".."),
        ("AES"),
    ])
    def test_get_scan_error(self, burp_api, scan_id):
        with pytest.raises(HTTPError) as ex:
            scan = burp_api.scans.get(scan_id)


    @pytest.mark.parametrize("frecuency, interval, week_day, until, count, expected", [
        ("DAYLY", 5, None, None, None, "FREQ=DAYLY,INTERVAL=5"),
        ("DAYLY", 6, None, None, 5, "FREQ=DAYLY,INTERVAL=6,COUNT=5"),
        ("YEARLY", 6, None, datetime(2023, 5, 3, 15, 30, 21), None, "FREQ=YEARLY,INTERVAL=6,UNTIL=20230503T153021Z"),
        ("WEEKLY", 6, ["MON", "TUESDAY"], datetime(2023, 5, 3, 0, 0, 0), None, "FREQ=WEEKLY,INTERVAL=6,BYDAY=MON,TUE,UNTIL=20230503T000000Z"),
    ])
    def test_program_data_config_rrlues(self, burp_api, frecuency, interval, week_day, until, count, expected):
        config = burp_api.scans._get_program_data_config(None, frecuency, interval, week_day, until, count)
        rrules = config['rrules']
        assert rrules == expected

    @pytest.mark.parametrize("frecuency, interval, week_day, until, count", [
        ("ADAYLY", 5, None, None, None),
        ("DAYLY", None, None, None, None),
        ("DAYLY", "A", None, None, None),
        ("WEEKLY", 3, None, None, None),
    ])
    def test_program_data_config_rrlues_error(self, burp_api, frecuency, interval, week_day, until, count):
        with pytest.raises(ScanProgrammingException):
            config = burp_api.scans._get_program_data_config(None, frecuency, interval, week_day, until, count)

    @pytest.mark.skip
    def test_create_scan(self, burp_api):
        pass

    @pytest.mark.skip
    def test_program_scan(self, burp_api):
        pass

    @pytest.mark.skip
    def test_start_scan(self, burp_api):
        pass

    @pytest.mark.skip
    def test_stop_scan(self, burp_api):
        pass
    
    @pytest.mark.skip
    def test_delete_scan(self, burp_api):
        pass

    
