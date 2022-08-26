# imports
import os
import requests

# TODO: improve
from graphql_queries import *

# TODO: what is error handling?

# constants # TODO: move to a config file (or something) <= copilot suggested this last part
ORG = "dbt-labs"
PROJECT_NAME = "Core triage"
PROJECT_NUM = 22
# list of Core teams
CORE_TEAMS = ["core"]
# read newline separated list of projects from file
REPOS = [
    "dbt-core",
    "dbt-redshift",
    "dbt-bigquery",
    "dbt-snowflake",
    "dbt-rpc",
    #"dbt-server", # internal, causes failure
    "dbt-spark",
    #"dbt-starter-project", # not important (?)
    "dbt-utils",
    "homebrew-dbt",
]
# issues added by label individually; lots of duplication here
ISSUE_LABELS = [
    "triage",
    "bug",
    "good_first_issue",
    "help_wanted",
    "spike",
    "python_models",
    "Team:Language",
    "Team:Execution",
    "Team:Adapters",
]
# prs added by label individually
PR_LABELS = ["ready_for_review"]
# GitHub TOKEN environment variable name
TOKEN_VAR = "GH_TOKEN"
# Number of items per query -- max is 100 TODO: paging?
NUM_ITEMS = 100

# API stuff -- not uppercase because...
headers = {"Authorization": f"token {os.environ.get(TOKEN_VAR)}"}
gh_api_url = "https://api.github.com"
gh_graphql_url = f"{gh_api_url}/graphql"

# functions
def process_request(url: str, headers: dict, json: dict = None) -> dict:
    """
    Process a request to the GitHub API (GET or POST, based on json).
    ---
    Inputs: url, headers, json (optional)
    Outputs: response (dict)
    """
    if json:
        r = requests.post(url, headers=headers, json=json)
    else:
        r = requests.get(url, headers=headers)

    print(r.status_code)
    print(r.text)

    return r.json()


def get_core_members(teams: list[str]) -> list:
    """
    Get a list of Core members' GitHub logins (usernames).
    ---
    Inputs: teams (list of str)
    Outputs: core_members (list of str)
    """
    # initialize empty list
    core_members = []

    # for each core team, add its members
    for team in teams:
        team_member_url = f"{gh_api_url}/orgs/{ORG}/teams/{team}/members"
        r = process_request(team_member_url, headers=headers)

        team_members = [login["login"] for login in r]
        core_members.extend(team_members)

    return sorted(list(set(core_members)))


def get_project_id(project_num: int) -> str:
    """
    Get a project's ID from its number.
    ---
    Inputs: project_num (int)
    Outputs: project_id (str)
    """
    project_id = process_request(
        gh_graphql_url,
        headers=headers,
        json={
            "query": project_id_query.replace("$org", f'"{ORG}"').replace(
                "$project_num", f"{project_num}"
            )
        },
    )["data"]["organization"]["projectV2"]["id"]
    return project_id


def get_issues(repo: str, label: str, num_items: int) -> list[dict]:
    """
    Get a list of issues for the given repo and label.
    ---
    Inputs: repo (str), label (str), num_items (int)
    Outputs: issues (list of dict)
    """
    # replace variables in query string and filter down to the issues' edges
    issues = process_request(
        gh_graphql_url,
        headers=headers,
        json={
            "query": issues_query.replace("$org", f'"{ORG}"')
            .replace("$repo", f'"{repo}"')
            .replace("$num_items", f"{num_items}")
            .replace("$label", f'"{label}"')
        },
    )["data"]["repository"]["issues"]["edges"]
    return issues


def add_items_to_project(project_id: str, items: list[dict]) -> None:
    """
    Adds items to a project by project_id and a list of item edges.
    ---
    Inputs: project_id (str), items (list of dict)
    Outputs: None
    """
    for item in items:
        print(item)
        response = process_request(
            gh_graphql_url,
            headers=headers,
            json={
                "query": add_item_to_project_mutation.replace(
                    "$project_id", f'"{project_id}"'
                ).replace("$item_id", f'"{item["node"]["id"]}"')
            },
        )


def main(
    repos: list[str],
    project_num: int,
    core_teams: list[str],
    issue_labels: list[str],
    pr_labels: list[str],
    num_items: int,
):
    """
    Main script function.
    All inputs have defaults.
    ---
    Inputs: repos (list of str), project_num (int), core_teams (list of str), issue_labels (list of str), pr_labels (list of str), num_items (int)
    Outputs: None
    """
    # get project id
    project_id = get_project_id(project_num)
    print(f"Project ID: {project_id}")
    # get core members
    core_members = get_core_members(core_teams)
    print(f"Core members: {core_members}\n...")
    # for each repo
    for repo in repos:
        print(f"Processing repository: {repo}\n...")
        # for each issue label
        for issue_label in issue_labels:
            print(f"Processing issue label: {issue_label}\n...")
            # get the list of issues for the repo and label
            issues = get_issues(repo, issue_label, num_items)
            # add issues to the project
            add_items_to_project(project_id, issues)
        # for each pr label
        for pr_label in pr_labels:
            print(f"Processing PR label: {pr_label}\n...")
            # get the list of PRs for the repo and label
            prs = get_issues(repo, pr_label, num_items)
            # add PRs to the project
            add_items_to_project(project_id, prs)


# run script
if __name__ == "__main__":
    main(REPOS, PROJECT_NUM, CORE_TEAMS, ISSUE_LABELS, PR_LABELS, NUM_ITEMS)
