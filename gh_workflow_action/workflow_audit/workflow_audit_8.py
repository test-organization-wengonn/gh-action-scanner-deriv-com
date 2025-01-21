
import re

PASS = '\033[92m'
FAIL = '\033[91m'
ENDC = '\033[0m'


vuln_refs = [
    "github.event.pull_request.head.sha",
    "github.event.workflow_run.head_sha"
]    


def workflow_audit_8(yaml_content):
    '''
        Check if public workflows is using Verify User Reusable Actions
    '''

    print("[Workflow Audit 8] Checking Verify User Workflow on Public Workflows")

    org_verify_user_action = "deriv-com/shared-actions/.github/actions/verify_user_in_organization@v1"
    
    failed_jobs = []

    try:
        for job in list(yaml_content["jobs"].keys()):

            has_vuln_ref = False

            # check if `vuln_ref` is present within the job 
            for step in yaml_content["jobs"][job]["steps"]:
                if step.get("with"):
                    # Not really needed but check just in case
                    if step.get("uses"):
                        if step.get("uses").split("@")[0] == "actions/checkout" and step.get("with").get("ref"):
                            for vuln_ref in vuln_refs:
                                if re.search(vuln_ref, step.get("with").get("ref")):
                                    has_vuln_ref = True
                                    
            if has_vuln_ref:
                # Get the first step within the job
                verify_user = yaml_content["jobs"][job]["steps"][0]["uses"]
                if not org_verify_user_action == verify_user:
                    failed_jobs.append(job)
                    
    except Exception as e:
        error_message = f"Exception Occurred in workflow_audit_8: {e}"
        print(error_message)
                
    
    if failed_jobs:
        audit_result = f" {FAIL}[ FAILED ]{ENDC} Missing verify user check, Please add verify user at the start of these jobs: {', '.join(failed_jobs)}"
        print(audit_result)
        return False, audit_result
    else:
        audit_result = f" {PASS}[ PASSED ]{ENDC} Verify user check passed"
        print(audit_result)
        return True, audit_result


