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
# core team name
CORE_TEAM = "core"
# repos determined by querying the team
# exclude some repos (generally internal) that will cause failure
# include some extra repos not in the team
EXCLUDE_REPOS = ["core-team", "schemas.getdbt.com"]
EXTRA_REPOS = ["dbt-starter-project", "jaffle_shop"]
# issues added by label individually; lots of duplication here
ISSUE_LABELS = [
    "triage",
    "bug",
    "good_first_issue",
    "awaiting_response",
    "support_rotation",
    "help_wanted",
    "spike",
    "python_models",
    "Team:Language",
    "Team:Execution",
    "Team:Adapters",
]
# prs added by label individually TODO: unused, add label filtering
PR_LABELS = ["ready_for_review"]
# GitHub TOKEN environment variable name TODO: make this input? hardcoded to match GH action
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


def get_core_repos(team: str) -> list:
    """
    Get a list of Core repos.
    ---
    Inputs: team (str)
    Outputs: core_repos (list of str)
    """
    # add the repos names owned by the team
    team_repos_url = f"{gh_api_url}/orgs/{ORG}/teams/{team}/repos"
    r = process_request(team_repos_url, headers=headers)
    core_repos = [repo["name"] for repo in r if repo["name"] not in EXCLUDE_REPOS]
    core_repos.extend(EXTRA_REPOS)

    return sorted(list(set(core_repos)))


def get_core_members(team: str) -> list:
    """
    Get a list of Core members' GitHub logins (usernames).
    ---
    Inputs: team (str)
    Outputs: core_members (list of str)
    """
    # add the GH logins of team members
    team_members_url = f"{gh_api_url}/orgs/{ORG}/teams/{team}/members"
    r = process_request(team_members_url, headers=headers)
    core_members = [login["login"] for login in r]

    return sorted(core_members)


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


def get_prs(repo: str, num_items: int) -> list[dict]:
    """
    Get a list of prs for the given repo and label.
    ---
    Inputs: repo (str), num_items (int)
    Outputs: prs (list of dict)
    """
    # replace variables in query string and filter down to the issues' edges
    prs = process_request(
        gh_graphql_url,
        headers=headers,
        json={
            "query": prs_query.replace("$org", f'"{ORG}"')
            .replace("$repo", f'"{repo}"')
            .replace("$num_items", f"{num_items}")
        },
    )["data"]["repository"]["pullRequests"]["edges"]
    return prs


def add_items_to_project(project_id: str, items: list[dict]) -> None:
    """
    Adds GitHub items (issues or PRs) to a project by project_id and a list of item edges.
    ---
    Inputs: project_id (str), items (list of dict)
    Outputs: None
    """
    for item in items:
        print(item)
        process_request(
            gh_graphql_url,
            headers=headers,
            json={
                "query": add_item_to_project_mutation.replace(
                    "$project_id", f'"{project_id}"'
                ).replace("$item_id", f'"{item["node"]["id"]}"')
            },
        )


def main(
    project_num: int,
    core_team: str,
    issue_labels: list[str],
    pr_labels: list[str],
    num_items: int,
):
    """
    Main script function.
    All inputs have defaults.
    ---
    Inputs: project_num (int), core_teams (str), issue_labels (list of str), pr_labels (list of str), num_items (int)
    Outputs: None
    """
    # get project id
    project_id = get_project_id(project_num)
    print(f"Project ID: {project_id}...\n")
    # get core members
    core_members = get_core_members(core_team)
    print(f"Core members: {core_members}...\n")
    # get core repos
    core_repos = get_core_repos(core_team)
    print(f"Core repos: {core_repos}...\n")
    # for each repo
    for repo in core_repos:
        print(f"Processing repository: {repo}...\n")
        # for each issue label
        for issue_label in issue_labels:
            print(f"Processing issue label: {issue_label}...\n")
            # get the list of issues for the repo and label
            issues = get_issues(repo, issue_label, num_items)
            # add issues to the project
            add_items_to_project(project_id, issues)

        # TODO: add back label filtering
        # get the list of PRs for the repo and label
        prs = get_prs(repo, num_items)
        # add PRs to the project
        add_items_to_project(project_id, prs)


# run script
if __name__ == "__main__":
    main(PROJECT_NUM, CORE_TEAM, ISSUE_LABELS, PR_LABELS, NUM_ITEMS)
