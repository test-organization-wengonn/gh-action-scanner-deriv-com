import os
import argparse
from pathlib import Path
from common.file import read_yaml
from workflow_audit.workflow_audit_1 import workflow_audit_1
from workflow_audit.workflow_audit_2 import workflow_audit_2
from workflow_audit.workflow_audit_3 import workflow_audit_3
from workflow_audit.workflow_audit_5 import workflow_audit_5
from workflow_audit.workflow_audit_6 import workflow_audit_6
from workflow_audit.workflow_audit_8 import workflow_audit_8

SKIP = '\033[93m'
ENDC = '\033[0m'


def main(yaml_paths, is_public):

    failed_actions = []

    for yaml_path in yaml_paths.split(','):
        print(f'\n/-------------------{yaml_path}-------------------/\n')
        yaml_workflow_content = read_yaml(yaml_path)

        if yaml_workflow_content == False:
            continue

        workflow_audit_2_status = True
        if is_public == 'True':
            # Check if public repo is using self-hosted runner
            workflow_audit_2_status, _ = workflow_audit_2(yaml_workflow_content)
        else:
            print(
            "[Workflow Audit 2] Checking Self hosted Runner in Public Repo")
            print(f" {SKIP}[ SKIPPED ]{ENDC} Check is not applicable as the workflow is not public")

        # Detect risky actions
        workflow_audit_5_status, _ = workflow_audit_5(yaml_workflow_content)

        # Check for risky contexts and vulnerable env 
        _workflow_audit_6 = workflow_audit_6(yaml_workflow_content)
        check_risky_contexts_status, _ = _workflow_audit_6.check_risky_contexts()
        check_vulnerable_env_status, _ =  _workflow_audit_6.check_vulnerable_env()


        workflow_audit_8_status = True
        if is_public == 'True':
            # Check if public workflows is using Verify User Reusable Actions
            workflow_audit_8_status, _ = workflow_audit_8(yaml_workflow_content)  
        else:
            print("[Workflow Audit 8] Checking Verify User Workflow on Public Workflows")
            print(f" {SKIP}[ SKIPPED ]{ENDC} Check is not applicable as the workflow is not public ")


        # Add to failed_actions if any audit fails
        audit_status = [
            workflow_audit_2_status,
            workflow_audit_5_status, 
            check_risky_contexts_status, 
            check_vulnerable_env_status, 
            workflow_audit_8_status
        ]

        if any(not status for status in audit_status):
            failed_actions.append(yaml_path)

    # exit 1 if failed_actions is not empty
    if failed_actions:
        print()
        print(f"The following actions has failed the audit:")
        for failed_action in failed_actions:
            print(f"    {failed_action}")
        exit(1)


if __name__ == "__main__":
    # Getting inputs from github action
    inputs_modified_workflows = os.environ["INPUT_MODIFIED_WORKFLOWS"]
    inputs_is_public = os.environ["INPUT_IS_PUBLIC"]

    main(inputs_modified_workflows, inputs_is_public)