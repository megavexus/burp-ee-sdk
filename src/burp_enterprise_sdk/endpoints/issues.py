from burp_enterprise_sdk.abstract import AbstractEndpointApi
from burp_enterprise_sdk.utils.enum import OrderedEnum

class SeverityLevel(OrderedEnum):
    HIGH = 3
    MEDIUM = 2
    LOW = 1
    INFO = 0

class ConfidenceLevel(OrderedEnum):
    CERTAIN = 2
    FIRM = 1
    TENTATIVE = 0

def normalize(text):
    return text.upper().strip()

    
class IssuesApi(AbstractEndpointApi):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ENDPOINT_GET = "/api-internal/scans/"
        self.ENDPOINT_GET_ISSUE_DEFINITION = "/api-internal/issue_definitions/"
        self.ENDPOINT_LIST = "/api-internal/scans"
        self.ENDPOINT_POST = "/api-internal/scans/"
        self.ENDPOINT_DELETE = "/api-internal/scans/"
        self.issues_definition = {}

    def get(self, id_scan, issue_id):
        return self.get_issue_detail(id_scan, issue_id)
        

    def list(self, id_scan, confidence_filter=None, severity_filter=None, get_occurrences=True, get_details=False):
        return self.get_issues_list(id_scan, confidence_filter, severity_filter, get_occurrences, get_details)


    def delete(self, *args, **kwargs):
        raise NotImplementedError("No aplica")


    def post(self, *args, **kwargs):
        raise NotImplementedError("No aplica")


    def get_issues_definition(self):
        if len(self.issues_definition) == 0:
            # TODO:
            issues_def = super().get(uri=self.ENDPOINT_GET_ISSUE_DEFINITION)
            self.issues_definition = {
                issue['issue_type_id']: issue
                for issue in issues_def['definitions']
            }
        return self.issues_definition



    def get_issues_list(self, id_scan, confidence_filter=None, severity_filter=None, get_occurrences=True, get_details=False):
        """
        Este método obtiene el listado de tipos de issue de un escaneo, con el listado 
        de los issues.
        Está filtrado por confianza y severidad.
        """
        uri_scan_types = "{}{}/issues/issue_type".format(self.ENDPOINT_GET, id_scan)
        scan_issue_types = super().get(uri=uri_scan_types)

        if type(severity_filter) == str:
            severity_filter = SeverityLevel[normalize(severity_filter)]

        if type(confidence_filter) == str:
            confidence_filter = ConfidenceLevel[normalize(confidence_filter)]

        issue_types_filtered = []

        for issue_type in scan_issue_types['issue_type_summaries']:
            if severity_filter and SeverityLevel[issue_type['severity']] < severity_filter:
                continue

            if confidence_filter and ConfidenceLevel[issue_type['confidence']] < confidence_filter:
                continue
            
            if get_occurrences:
                issues_list = self.get_issues_for_issue_type(id_scan, issue_type["type_index"], confidence_filter, severity_filter)
                issue_type['issues'] = issues_list

            issue_types_filtered.append(issue_type)

        return issue_types_filtered
        

    def get_issues_for_issue_type(self, id_scan, issue_type_id, confidence_filter=None, severity_filter=None, get_details=False):
        """
        Dado un tipo de Issue, obtiene sus issues de un scan con ese tipo.
        """
        issues_list_uri = "{}{}/issues/issue_type/{}".format(self.ENDPOINT_GET, id_scan, issue_type_id)
        issues_list = super().get(uri=issues_list_uri)

        if type(severity_filter) == str:
            severity_filter = SeverityLevel[normalize(severity_filter)]

        if type(confidence_filter) == str:
            confidence_filter = ConfidenceLevel[normalize(confidence_filter)]

        issues_list_filtered = []
        for issue in issues_list["issue_summaries"]:

            if severity_filter and SeverityLevel[issue['severity']] < severity_filter:
                continue

            if confidence_filter and ConfidenceLevel[issue['confidence']] < confidence_filter:
                continue
            
            issue_id = issue['serial_number']
            if get_details:
                issue_details = self.get_issue_detail(id_scan, issue_id)
                issue['issue'] = issue_details['issue']

            issues_list_filtered.append(issue)

        return issues_list_filtered


    def get_issue_detail(self, id_scan, issue_id):
        uri = "{}{}/issues/{}".format(self.ENDPOINT_GET, id_scan, issue_id)
        issue_details = super().get(uri=uri)
        if 'code' in issue_details and issue_details['code'] == 37:
            return None
        return issue_details
