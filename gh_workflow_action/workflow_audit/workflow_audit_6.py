import re

PASS = '\033[92m'
FAIL = '\033[91m'
ENDC = '\033[0m'

class workflow_audit_6:
    def __init__(self, yaml_content):
        self.risky_contexts = [
            r"github\.head_ref",
            r"github\.event\.comment\.body",
            r"github\.event\.discussion\.body",
            r"github\.event\.discussion\.title",
            r"github\.event\.head_commit\.author\.email",
            r"github\.event\.head_commit\.author\.name",
            r"github\.event\.head_commit\.committer\.email",
            r"github\.event\.head_commit\.committer\.name",
            r"github\.event\.head_commit\.message",
            r"github\.event\.issue\.body",
            r"github\.event\.issue\.title",
            r"github\.event\.pages\..*\.page_name",
            r"github\.event\.pages\..*\.title",
            r"github\.event\.pull_request\.body",
            r"github\.event\.pull_request\.head\.label",
            r"github\.event\.pull_request\.head\.ref",
            r"github\.event\.pull_request\.head\.repo\.default_branch",
            r"github\.event\.pull_request\.head\.repo\.description",
            r"github\.event\.pull_request\.head\.repo\.homepage",
            r"github\.event\.pull_request\.title",
            r"github\.event\.review\.body",
            r"github\.event\.workflow_run\.display_title",
            r"github\.event\.workflow_run\.head_branch",
            r"github\.event\.workflow_run\.head_commit\.author\.email",
            r"github\.event\.workflow_run\.head_commit\.author\.name",
            r"github\.event\.workflow_run\.head_commit\.committer\.email",
            r"github\.event\.workflow_run\.head_commit\.committer\.name",
            r"github\.event\.workflow_run\.head_commit\.message",
            r"github\.event\.workflow_run\.head_repository\.description",
            r"inputs\..*"
        ]

        self.yaml_content = yaml_content

    def _extract_scripts_from_steps(self, steps):
        scripts = []

        for step in steps:
            # extract scripts
            script = step.get("run")
            if script:
                scripts.append(script)

        return scripts

    def _extract_script(self):
        '''
            Extract script from workflows and reusable workflows 'run'
            yaml format

            jobs:
                someRandomName:
                    steps:
                        run: <some commands>
        '''
        jobs = self.yaml_content.get("jobs")

        scripts = []

        # check if 'jobs' exist
        if jobs:
            # use to skip the random job name
            jobs = jobs.values()

            for job in jobs:
        
                steps = job.get("steps")
                if steps:
                    _scripts = self._extract_scripts_from_steps(steps)
                    scripts.extend(_scripts)

        '''
            Extract script from reusable actions 'run'
            yaml format

            runs:
                steps:
                    run: <some commands>
        '''
        runs = self.yaml_content.get("runs")    
        if runs:            
            steps = runs.get("steps")
            if steps:
                _scripts = self._extract_scripts_from_steps(steps)
                scripts.extend(_scripts)

        return scripts

    def check_risky_contexts(self):
        '''
            Check for risky (injectable) github contexts 
        '''

        print(
            f"[Workflow Audit 6.1] Checking if risky contexts is being used")

        scripts = self._extract_script()

        risky_context_count = 0
        detected_risky_contexts = []

        # No script/"run"
        if len(scripts) <= 0:
            audit_result = f" {PASS}[ PASSED ]{ENDC} No risky contexts detected"
            print(audit_result)
            return True, audit_result

        for script in scripts:
            for _risky_context in self.risky_contexts:
                if (re.search(_risky_context, script)):
                    # Removing \. from risky_contexts so that its easier to see
                    # in notifications and on dashboard.
                    _risky_context = _risky_context.replace("\\","").replace("..",".")
                    if _risky_context not in detected_risky_contexts:
                        detected_risky_contexts.append(_risky_context)
                        risky_context_count += 1

        if risky_context_count <= 0:
            audit_result = f" {PASS}[ PASSED ]{ENDC} No risky contexts detected"
            print(audit_result)
            return True, audit_result
        else:
            audit_result = f" {FAIL}[ FAILED ]{ENDC} Risky contexts detected: {', '.join(detected_risky_contexts)}"
            print(audit_result)
            return False, audit_result

    def check_vulnerable_env(self):
        '''
            Check for vulnerable 'env' usage
        '''

        print(
            f"[Workflow Audit 6.2] Checking if vulnerable envs is being used")

        scripts = self._extract_script()

        detected_vuln_envs = []     

        for script in scripts:            
            detected_vuln_envs_search = re.findall(r'[^.]env\..*}}', script)

            for valid in detected_vuln_envs_search:
                detected_vuln_envs.append(valid)
                
        if not detected_vuln_envs:
            audit_result = f" {PASS}[ PASSED ]{ENDC} No vulnerable envs detected"
            print(audit_result)
            return True, audit_result
        else:
            audit_result = f" {FAIL}[ FAILED ]{ENDC} Vulnerable envs detected: {', '.join(detected_vuln_envs)}"
            print(audit_result)
            return False, audit_result

