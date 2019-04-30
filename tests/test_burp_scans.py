import pytest
from requests.exceptions import HTTPError
from datetime import datetime, timedelta
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
        ("DAILY", 5, None, None, None, "FREQ=DAILY;INTERVAL=5"),
        ("DAILY", 6, None, None, 5, "FREQ=DAILY;INTERVAL=6;COUNT=5"),
        ("YEARLY", 6, None, datetime(2023, 5, 3, 15, 30, 21), None, "FREQ=YEARLY;INTERVAL=6;UNTIL=20230503T153021Z"),
        ("WEEKLY", 6, ["MON", "TUESDAY"], datetime(2023, 5, 3, 0, 0, 0), None, "FREQ=WEEKLY;INTERVAL=6;BYDAY=MO,TU;UNTIL=20230503T000000Z"),
    ])
    def test_program_data_config_rrlues(self, burp_api, frecuency, interval, week_day, until, count, expected):
        config = burp_api.scans._get_program_data_config(None, frecuency, interval, week_day, until, count)
        rrule = config['rrule']
        assert rrule == expected

    @pytest.mark.parametrize("frecuency, interval, week_day, until, count", [
        ("ADAILY", 5, None, None, None),
        ("DAILY", None, None, None, None),
        ("DAILY", "A", None, None, None),
        ("WEEKLY", 3, None, None, None),
    ])
    def test_program_data_config_rrlues_error(self, burp_api, frecuency, interval, week_day, until, count):
        with pytest.raises(ScanProgrammingException):
            config = burp_api.scans._get_program_data_config(None, frecuency, interval, week_day, until, count)

    @pytest.mark.parametrize("site_id, scan_configuration_expected", [
        (9, ["06f9a9d4-6e5a-48e1-8305-c6c45775b5f3"]),
        (7, []),
    ])
    def test_create_scan(self, burp_api, site_id, scan_configuration_expected):
        scan = burp_api.scans.create(site_id)
        assert 'id' in scan
        assert scan['scan_configuration_ids'] == scan_configuration_expected
        burp_api.scans.delete(scan['id'])


    def test_delete_scan(self, burp_api):
        scan = burp_api.scans.create(9)
        assert 'id' in scan
        scan_get1 = burp_api.scans.get(scan['id'])
        assert 'id' in scan_get1

        burp_api.scans.delete(scan['id'])
        scan_get_delete = burp_api.scans.get(scan['id'])
        assert scan_get_delete['code'] == 41

    @pytest.mark.parametrize("frecuency, interval, week_day, until, count, expected", [
        ("DAILY", 5, None, None, None, "FREQ=DAILY;INTERVAL=5"),
        ("DAILY", 6, None, None, 5, "FREQ=DAILY;INTERVAL=6;COUNT=5"),
        ("YEARLY", 6, None, datetime(2023, 5, 3, 15, 30, 21), None, "FREQ=YEARLY;INTERVAL=6;UNTIL=20230503T153021Z"),
        ("WEEKLY", 6, ["MON", "TUESDAY"], datetime(2023, 5, 3, 0, 0, 0), None, "FREQ=WEEKLY;INTERVAL=6;BYDAY=MO,TU;UNTIL=20230503T000000Z"),
    ])
    def test_program_scan(self, burp_api, frecuency, interval, week_day, until, count, expected):
        scan = burp_api.scans.create(9)
        scan_get1 = burp_api.scans.get(scan['id'])
        assert 'id' in scan_get1

        # Se le reprograma
        now_date = datetime.now()
        start_time = datetime.now() + timedelta(days=1)
        start_expected = start_time.strftime("%Y-%m-%dT%T.000Z")
        assert burp_api.scans.program(scan['id'], start=start_time, frecuency=frecuency, interval=interval, week_days=week_day, until=until, count=count)

        scan_mod = burp_api.scans.get(scan['id'])
        burp_api.scans.delete(scan['id'])

        schedule_item = scan_mod['schedule_item']
        assert start_expected == schedule_item['initial_run_time']
        assert expected == schedule_item['rrule']


    def test_start_scan(self, burp_api):
        scan = burp_api.scans.create(9)
        scan_get1 = burp_api.scans.get(scan['id'])
        orig_scan_run_time = scan_get1['schedule_item']['initial_run_time'][:-1]+"000"
        orig_scan_run_time = datetime.strptime(orig_scan_run_time, "%Y-%m-%dT%H:%M:%S.%f")
        assert 'id' in scan_get1

        assert burp_api.scans.start(scan['id'])
        scan_get2 = burp_api.scans.get(scan['id'])
        assert burp_api.scans.delete(scan['id'])

        mod_scan_run_time = scan_get2['schedule_item']['initial_run_time'][:-1]+"000"
        mod_scan_run_time = datetime.strptime(mod_scan_run_time, "%Y-%m-%dT%H:%M:%S.%f")
        assert mod_scan_run_time > orig_scan_run_time

        mod_scan_scheduled_time = scan_get2['schedule_item']['scheduled_run_time'][:-1]+"000"
        mod_scan_scheduled_time = datetime.strptime(mod_scan_scheduled_time, "%Y-%m-%dT%H:%M:%S.%f")
        assert mod_scan_run_time <= mod_scan_scheduled_time

    def test_stop_scan(self, burp_api):
        scan = burp_api.scans.create(9)
        scan_get1 = burp_api.scans.get(scan['id'])
        assert scan_get1['status'] in ['QUEUED', "RUNNING"]

        assert burp_api.scans.stop(scan['id'])
        scan_stopped = burp_api.scans.get(scan['id'])
        assert burp_api.scans.delete(scan['id'])
        assert scan_stopped['status'] == "CANCELLED"    
