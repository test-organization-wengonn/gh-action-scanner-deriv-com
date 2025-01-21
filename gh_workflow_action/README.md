# Github Action PR Scanner 
1. Review changes made to Github Action File on PR


## Audit Checks
2. Workflow Audit 2 - Checking Self hosted Runner in Public Repo
3. Workflow Audit 5 - Checking if risky actions is being used
4. Workflow Audit 6.1 - Checking if risky contexts is being used
5. Workflow Audit 6.2 - Checking if vulnerable envs is being used
6. Workflow Audit 8 - Checking Verify User Workflow on Public Workflows

## Usage
```yaml
name: Github Action Audit
on:
  pull_request:
    branches:
      - main
      - master

jobs:
  github_action_audit:
    runs-on: ubuntu-latest
    
    permissions:
      contents: read

    env:
      GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }} # this is needed for gh cli

    steps:
      # Checking if repo is public. If it's not, dependency review will be skipped.
      - name: Check if repo is public
        run: |
          response=$(gh api -H "Accept: application/vnd.github+json" -H "X-GitHub-Api-Version: 2022-11-28" repos/${{ github.repository}} | jq -r '.visibility')
          if [ "$response" == "public" ]; then
            echo "Repository is Public."
            echo 'is_public=true' >> $GITHUB_ENV
          fi

      - name: Checkout
        uses: actions/checkout@v3
        with:
          fetch-depth: 2
      - name: Get modified filenames
        id: pr-diff
        run: |
          modified_workflows="$(git diff --name-only HEAD^1 HEAD | grep -E '^\.github/workflows' | tr '\n' ',' | sed 's+,$++g')"
          echo "modified_workflows=${modified_workflows}" >> $GITHUB_ENV
          echo "pr_diff=${modified_workflows}" >> $GITHUB_OUTPUT

      - name: github action scanner
        if: ${{ steps.pr-diff.outputs.pr_diff != '' }}
        uses: regentmakets/security-scanner/gh_workflow_action@master
        with:
          is_public: ${{ env.is_public }}
          modified_workflows: ${{ env.modified_workflows }}

```

## Fix/Mitigation 
### Workflow Audit 2 - Checking Self hosted Runner in Public Repo
1. Ensure that public repositories is not using self-hosted runners
2. Avoid the use of Self Hosted Runner for Public facing repos as this opens up additional attack surface. 
3. Reference - [Github Documentation](https://docs.github.com/en/actions/security-for-github-actions/security-guides/security-hardening-for-github-actions#hardening-for-self-hosted-runners)

### Workflow Audit 5 - Checking if risky actions is being used
1. Checks if the following actions are being used with `actions/checkout` head sha :
    - `pull_request_target`
    - `workflow_run`
2. These actions comes with some risks if not used properly and allows excessive privileges by default 
3. References:
    - [Keeping your GitHub Actions and workflows secure Part 1: Preventing pwn requests](https://securitylab.github.com/resources/github-actions-preventing-pwn-requests/)
    - [pull_request_target Github Documentation](https://docs.github.com/en/actions/writing-workflows/choosing-when-your-workflow-runs/events-that-trigger-workflows#pull_request_target:~:text=the%20pull_request_target%20event.-,Warning,-For%20workflows%20that)
    - [workflow_run Github Documentation](https://docs.github.com/en/actions/writing-workflows/choosing-when-your-workflow-runs/events-that-trigger-workflows#workflow_run:~:text=The%20workflow%20started%20by%20the%20workflow_run%20event%20is%20able%20to%20access%20secrets%20and%20write%20tokens%2C%20even%20if%20the%20previous%20workflow%20was%20not.%20This%20is%20useful%20in%20cases%20where%20the%20previous%20workflow%20is%20intentionally%20not%20privileged%2C%20but%20you%20need%20to%20take%20a%20privileged%20action%20in%20a%20later%20workflow.)

### Workflow Audit 6.1 - Checking if risky contexts is being used
1. Checks if the mentioned contexts are being used improperly under `run`:
2. Mentioned contexts should be declared as Github Action Environment variable 
3. Improper usage of Github Action Contexts could lead to code injection 
4. Reference - [Github Documentation](https://docs.github.com/en/actions/security-for-github-actions/security-guides/security-hardening-for-github-actions#understanding-the-risk-of-script-injections)
5. Example:
    ```yaml
    patch_job_3:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@b4ffde65f46336ab88eb53be808477a3936bae11
    - env:
        ENVTITLE: ${{ github.event.issue.title }}  # Declaring github action context as env variable

    run: |

        # Vulnerable way of using github action context
        echo "ISSUE DESCRIPTION: ${{ github.event.issue.title }}"

        # Correct way of using github action context
        echo "ISSUE TITLE: $ENVTITLE"
    ```

6. Vulnerable Github Action Contexts:
    ```
    github\.head_ref,
    github\.event\.comment\.body,
    github\.event\.discussion\.body,
    github\.event\.discussion\.title,
    github\.event\.head_commit\.author\.email,
    github\.event\.head_commit\.author\.name,
    github\.event\.head_commit\.committer\.email,
    github\.event\.head_commit\.committer\.name,
    github\.event\.head_commit\.message,
    github\.event\.issue\.body,
    github\.event\.issue\.title,
    github\.event\.pages\..*\.page_name,
    github\.event\.pages\..*\.title,
    github\.event\.pull_request\.body,
    github\.event\.pull_request\.head\.label,
    github\.event\.pull_request\.head\.ref,
    github\.event\.pull_request\.head\.repo\.default_branch,
    github\.event\.pull_request\.head\.repo\.description,
    github\.event\.pull_request\.head\.repo\.homepage,
    github\.event\.pull_request\.title,
    github\.event\.review\.body,
    github\.event\.workflow_run\.display_title,
    github\.event\.workflow_run\.head_branch,
    github\.event\.workflow_run\.head_commit\.author\.email,
    github\.event\.workflow_run\.head_commit\.author\.name,
    github\.event\.workflow_run\.head_commit\.committer\.email,
    github\.event\.workflow_run\.head_commit\.committer\.name,
    github\.event\.workflow_run\.head_commit\.message,
    github\.event\.workflow_run\.head_repository\.description,
    inputs\..*
    ```
### Workflow Audit 6.2 - Checking if vulnerable envs is being used
1. Checks if the Github Action environment variable are being used improperly under `run`:
2. Env variable should be call `$SOMEVAR` instead of `${{ SOMEVAR }}`
3. Improper usage of Github Action Contexts could lead to code injection 
4. Reference - [Github CodeQL Documentation](https://codeql.github.com/codeql-query-help/javascript/js-actions-command-injection/#:~:text=The%20following%20example%20uses%20an%20environment%20variable%2C%20but%20still%20allows%20the%20injection%20because%20of%20the%20use%20of%20expression%20syntax%3A)
5. Example:
    ```yaml
    patch_job_3:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@b4ffde65f46336ab88eb53be808477a3936bae11
    - env:
        ENVDESCRIPTION: ${{github.event.issue.body}}

    run: |

        # Vulnerable way of using github env variable
        echo "ISSUE DESCRIPTION: ${{ env.ENVDESCRIPTION }}"

        # Correct way of using github env variable
        echo "ISSUE DESCRIPTION: $ENVDESCRIPTION"       
    ```

### Workflow Audit 8 - Checking Verify User Workflow on Public Workflows
1. Check if public workflows that checkouts pull request has [verify user action](https://github.com/deriv-com/shared-actions/blob/master/.github/actions/verify_user_in_organization/action.yml) at the start of the job:
    - `actions/checkout`
      - `github.event.pull_request.head.sha`
      - `github.event.workflow_run.head_sha`
2. This ensures that only users is being validated within the GitHub organization before proceeding with the other steps within the job.
3. Example - [Example Workflow](https://github.com/deriv-com/p2p/blob/master/.github/workflows/build-and-deploy-test.yml):
    ```yaml
    jobs:
      build_to_cloudflare_pages:
        runs-on: ubuntu-latest
        steps:
          - name: Verify user
            uses: 'deriv-com/shared-actions/.github/actions/verify_user_in_organization@v1'
            with:
                username: ${{ github.event.pull_request.user.login }}
                token: ${{ secrets.PERSONAL_ACCESS_TOKEN }}

          - name: Checkout to branch
            uses: actions/checkout@v3
            with:
                ref: ${{ github.event.pull_request.head.sha }}
    ```


