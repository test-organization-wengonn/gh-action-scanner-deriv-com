
import re

PASS = '\033[92m'
FAIL = '\033[91m'
ENDC = '\033[0m'

# Add risky actions to the lists  
risky_actions = [ 
    'pull_request_target',
    'workflow_run'
]

def workflow_audit_5(yaml_workflow_content):
    '''
        Detect risky actions 
          - Check if mentioned risky action is being used
          - Check if `github.event.pull_request.head.sha` or `github.event.workflow_run.head_sha` is being used along with it
    '''
    print(f"[Workflow Audit 5] Checking if risky actions is being used")

    # Python interprets YAML "on" key as "True" 
    actions = yaml_workflow_content.get(True)

    detected_actions = []

    if actions:
        if type(actions) == list:
            for action in actions:
                if action in risky_actions:
                    if _is_vuln_action(action,yaml_workflow_content):
                        detected_actions.append(action)
        elif type(actions) == dict:
            for action in actions:
                if action in risky_actions:
                    if _is_vuln_action(action,yaml_workflow_content):
                        detected_actions.append(action)

    if len(detected_actions) <= 0:
        audit_result = f" {PASS}[ PASSED ]{ENDC} No risky actions detected"
        print(audit_result)
        return True, audit_result
    
    audit_result = f" {FAIL}[ FAILED ]{ENDC} Risky actions detected:" + ', '.join(detected_actions)
    print(audit_result)
    return False, audit_result

def _is_vuln_action(action, yaml_workflow_content):
        '''
            Check if actions/checkout and ref with head.sha are used
        '''
        
        if action == "pull_request_target":
            vuln_ref = "github.event.pull_request.head.sha"
        else:
            vuln_ref = "github.event.workflow_run.head_sha"

        if "jobs" in yaml_workflow_content:
            for job_data in yaml_workflow_content["jobs"].values():
                if "steps" in job_data:
                    for step_data in job_data["steps"]:
                        if "uses" in step_data and "with" in step_data and "ref" in step_data["with"]:
                            if re.search("actions/checkout",step_data["uses"]) and re.search(vuln_ref,step_data["with"]["ref"]):
                                return True
        return False
