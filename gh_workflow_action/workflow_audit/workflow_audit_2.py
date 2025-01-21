PASS = '\033[92m'
FAIL = '\033[91m'
ENDC = '\033[0m'

def workflow_audit_2(yaml_workflow):
    '''
        Check if public repo is using self-hosted runner
    '''
    runs_on = []

    try:
        print(
            "[Workflow Audit 2] Checking Self hosted Runner in Public Repo")
        if 'jobs' in yaml_workflow:
            for job_data in yaml_workflow["jobs"].values():
                if "runs-on" in job_data:
                    runs_on = job_data["runs-on"]

        if 'self-hosted' in runs_on:
            self_hosted_runner = f' {FAIL}[ FAILED ]{ENDC} Self Hosted runner is used'
            print(self_hosted_runner)
            return False, self_hosted_runner
        else:
            self_hosted_runner = f' {PASS}[ PASSED ]{ENDC} Self Hosted runner is not used'
            print(self_hosted_runner)
            return True, self_hosted_runner
    except Exception as e:
        exception = f"Exception Occurred in workflow_audit_2: {e}"
        return False, exception
            
        
        