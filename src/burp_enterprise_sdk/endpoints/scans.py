from burp_enterprise_sdk.abstract import AbstractEndpointApi
from burp_enterprise_sdk.endpoints.issues import IssuesApi
from burp_enterprise_sdk.endpoints.sites import SitesApi
from burp_enterprise_sdk.utils.str_utils import normalize
from datetime import datetime
from enum import Enum

class ScanProgrammingException(Exception):
    """
    Excepcion que se lanza cuando ocurre algun fallo al programar un escaneo.
    """

class ScanStatus(Enum):
    RUNNING = 0 # Scanning
    SUCCEEDED = 1 # Completed
    QUEUED = 2 # Waiting for agent
    SCHEDULED = 3
    FAILED = 4
    CANCELLED = 5

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

frecuency_list = ["MINUTELY", "DAILY", "WEEKLY", "MONTHLY", "YEARLY"]
#week_days_list = ['MON', 'TUE', 'WEN', 'THU', 'FRI', 'SAT', 'SUN']
week_days_list = ['MO', 'TU', 'WE', 'TH', 'FR', 'SA', 'SU']

class ScansApi(AbstractEndpointApi):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ENDPOINT_GET = "/api-internal/scans/"
        self.ENDPOINT_GET_SCHEDULE = "/api-internal/schedule/"
        self.ENDPOINT_LIST = "/api-internal/scan_summaries"
        self.ENDPOINT_POST = "/api-internal/schedule/"
        self.ENDPOINT_PUT = "/api-internal/scans/"
        self.ENDPOINT_DELETE = "/api-internal/scans/"


    def _get_page_scans(self, id_scan, page=0, status_filters=[]):
        if id_scan:
            uri = "/api-internal/scans/{}/scan_summaries".format(id_scan)
        else:
            uri = self.ENDPOINT_LIST

        params = {
            "page": page,
        }
        if len(status_filters):
            params["filters"] = status_filters
        ret = super().get(
            uri=uri,
            params=params
        )
        return ret


    def list(self, id_scan=None, status_filters=[]):
        if type(status_filters) == str:
            status_filters = [status_filters]
        
        status = [ ScanStatus(ScanStatus[normalize(status)]).name for status in status_filters]
        
        ret = self._get_page_scans(id_scan, 0, status_filters)
        page = ret["page"]
        page_size = ret["page_size"]
        results = ret['rows']
        num_scans = len(results)
        while num_scans == page_size:
            page += 1
            ret = self._get_page_scans(id_scan, page, status_filters)
            results = results + ret['rows']
            num_scans = len(ret['rows'])

        return results


    def get_schedule(self, id_scan):
        uri = self.ENDPOINT_GET_SCHEDULE + str(id_scan)
        schedule_data = super().get(uri=uri)
        return schedule_data

    def get(self, id_scan, get_issues=False):
        scan_data = super().get(id_scan)
        if get_issues and 'id' in scan_data:
            issues_api = IssuesApi(self.connection)
            issues = issues_api.get(id_scan)
            scan_data['issues'] = issues

        if "schedule_item_id" in scan_data:
            schedule_item = self.get_schedule(scan_data['schedule_item_id'])
            scan_data['schedule_item'] = schedule_item

        return scan_data


    def _get_program_data_config(self, start:datetime, frecuency=None, interval=None, week_days=[], until:datetime=None, count:int=None, scan_configurations=[], is_update=False):
        """
        - start: None si es para empezar ya, o un datetime si es programado
        - frecuency: Tipo de repetición. Valen los valores: ["MINUTELY", "DAILY", "WEEKLY", "MONTHLY", "YEARLY"]
        - interval: Intervalo de tiempo en el que se repite
        - week_days: Listado con los dias qeu aplica (sólo si es semanal): ['MON', 'TUE', 'WEN', 'THU', 'FRI', 'SAT', 'SUN']
        - until: Fecha hasta la que se repite. 
        - count. Número de veces que se ejecutará.

        initial_run_time:{ null | YYYY-MM-DDTHH:MM:SS+01:00 }
        rrule: {
            FREQ=(DAILY|WEEKLY|MONTHLY)
            INTERVAL=N
            BYDAY=MON,TUE,WEN,...
            UNTIL=YYYYMMDDTHHMMSSZ
            COUNT=N
        }
        """
        data = {}
        if scan_configurations and scan_configurations != []:
            data["scan_configuration_ids"] = scan_configurations 

        if start:
            data["initial_run_time"] = start.strftime("%Y-%m-%dT%H:%M:%S+00:00")
            #data["start_now"]=False
        elif is_update:
            data["start_now"]=True

        rrule = {}
        if frecuency:
            if frecuency.upper() not in frecuency_list:
                raise ScanProgrammingException("The parameter frecuency must be in the values {}".format(frecuency_list))
            rrule['FREQ'] = frecuency.upper()
            
            if not interval or type(interval) != int:
                raise ScanProgrammingException("To set an interval, you must provide minimum the frecuency and interval, and the byday if is MONTHLY")
            rrule['INTERVAL'] = interval
            
            if rrule['FREQ'] == "WEEKLY":
                if not week_days or len(week_days) == 0:
                    raise ScanProgrammingException("With the frecuency WEEKLY you must set the parameter week_days with an array of the days")
                week_days = set(week_days)
                rrule['BYDAY'] = []
                for day in sorted(week_days):
                    day_normalized = day.upper()[0:2]
                    if day_normalized not in week_days_list:
                        raise ScanProgrammingException("The day {} must be in {}".format(day, week_days_list))
                    rrule['BYDAY'].append(day_normalized)
                rrule['BYDAY'] = ','.join(rrule['BYDAY'])
            
            if until:
                rrule['UNTIL'] = until.strftime("%Y%m%dT%H%M%SZ")
            elif count:
                rrule['COUNT'] = count

            data['rrule'] = ";".join([ "{}={}".format(key, value) for key, value in rrule.items() ])

        return data


    def create(self, site_id, start:datetime=None, frecuency=None, interval=None, week_days=[], until:datetime=None, count:int=None, scan_configurations=None):
        if not scan_configurations:
            site_ep = SitesApi(self.connection)
            site_data = site_ep.get(site_id)
            scan_configurations = site_data['scan_configuration_ids']

        data = self._get_program_data_config(start, frecuency, interval, week_days, until, count, scan_configurations)
        data["site_tree_node_id"] = site_id

        scan_data = self.post(id="", data=data)
        if 'id' in scan_data:
            # blackmagic.. pero parece que BURP lo hace así. Hay que sumar 1 al ID (2019/04/30)
            scan_data['id'] = str(int(scan_data['id']) + 1)
        return scan_data


    def program(self, scan_id, start:datetime=None, frecuency=None, interval=None, week_days=[], until:datetime=None, count:int=None, scan_configurations=None):
        data = self._get_program_data_config(start, frecuency, interval, week_days, until, count, scan_configurations, is_update=True)
        scan_data = self.get(scan_id)
        scan_data_schedule_id = scan_data['schedule_item_id']
        uri = self.ENDPOINT_GET_SCHEDULE + scan_data_schedule_id
        res = self.post(uri=uri, data=data, is_update=True)
        if res == None:
            return True
        else:
            raise Exception("{} - {}".format(res['code'], res['error']))


    def start(self, scan_id):
        return self.program(scan_id, start=None)


    def stop(self, scan_id):
        uri_put = "{}{}/status/cancelled".format(self.ENDPOINT_PUT, scan_id)
        res = self.put(id=scan_id, uri=uri_put)
        if res == None:
            return True
        else:
            raise Exception("{} - {}".format(res['code'], res['error']))


    def delete(self, scan_id):
        res = super().delete(id=scan_id)
        return res
