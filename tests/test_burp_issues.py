import pytest

class TestIssues():

    def test_get_issues_definitions(self, burp_api):
        issues_definition = burp_api.issues.get_issues_definition()
        assert len(issues_definition) > 100


    @pytest.mark.parametrize("scan_id, num_expected",[
        (8, 27)
    ])
    def test_get_issue_list(self, burp_api, scan_id, num_expected):
        issues_list = burp_api.issues.list(scan_id)
        assert len(issues_list) == num_expected


    @pytest.mark.parametrize("scan_id, issue_id, expected_issue_name",[
        (8, "5723501564132548608", "SQL injection"),
    ])
    def test_get_issue_detail(self, burp_api, scan_id, issue_id, expected_issue_name):
        issue_data = burp_api.issues.get(scan_id, issue_id)
        issue_data = issue_data['issue']
        assert issue_data['name'] == expected_issue_name

    @pytest.mark.parametrize("scan_id, issue_id",[
        (8, "572350156413254860")
    ])
    def test_get_issue_detail_fail(self, burp_api, scan_id, issue_id):
        issue_data = burp_api.issues.get(scan_id, issue_id)
        assert issue_data == None


    @pytest.mark.parametrize("scan_id, criticity_filter, confidence_filter, num_expected",[
        (8, None, None, 27),
        (8, "HIGH", None, 7),
        (8, "MEDIUM", None, 8),
        (8, None, "CERTAIN", 14),
        (8, "HIGH", "CERTAIN", 4),
    ])
    def test_get_filtered_issues_list(self, burp_api, scan_id, criticity_filter, confidence_filter, num_expected):
        issues_list = burp_api.issues.list(scan_id, severity_filter=criticity_filter, confidence_filter=confidence_filter)
        assert len(issues_list) == num_expected


    @pytest.mark.parametrize("scan_id, issue_type",[
        (8, 1049088),
        (8, 2097920),
        (8, 1048832),
        (8, 4195072),
    ])
    def test_get_issue_occurences(self, burp_api, scan_id, issue_type):
        issues_list = burp_api.issues.list(scan_id, get_occurrences=False)
        issue_type_data = None
        for issue in issues_list:
            if issue['type_index'] == str(issue_type):
                issue_type_data = issue
                break
            
        issues_list_occurences = burp_api.issues.get_issues_for_issue_type(scan_id, issue_type)
        assert len(issues_list_occurences) == issue_type_data['number_of_children']

    @pytest.mark.parametrize("scan_id, issue_type, criticity_filter, confidence_filter, num_expected",[
        (8, 2097920, None, None, 24),
        (8, 2097920, "HIGH", None, 5),
        (8, 2097920, "MEDIUM", None, 22),
        (8, 2097920, None, "CERTAIN", 23),
        (8, 2097920, "HIGH", "CERTAIN", 4),
        (8, 4197376, None, None, 68),
        (8, 4197376, "INFO", None, 68),
        (8, 4197376, None, "CERTAIN", 68),
        (8, 4197376, "INFO", "CERTAIN", 68),
        (8, 4197376, "HIGH", "CERTAIN", 0),
    ])
    def test_get_issue_occurences_filtered(self, burp_api, scan_id, issue_type, criticity_filter, confidence_filter, num_expected):
        issues_list_occurences = burp_api.issues.get_issues_for_issue_type(scan_id, issue_type, severity_filter=criticity_filter, confidence_filter=confidence_filter)
        assert len(issues_list_occurences) == num_expected