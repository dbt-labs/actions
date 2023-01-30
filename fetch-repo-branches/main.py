import requests
import re
import os
import json
import time
from enum import Enum
from dataclasses import dataclass


class ProvidedMatchMethodNotSupportedOrIncorrect(Exception):
    """The specified match method is not supported or incorrect"""
    pass


@dataclass
class FetchRequestData:
    repo_name: str
    organization: str
    protected_branches_only: bool
    pat: str
    attempts_limit: int

    def get_request_url(self) -> str:
        url = f"https://api.github.com/repos/{self.organization}/{self.repo_name}/branches"
        return url

    def get_request_parameters(self) -> dict:
        parameters = {
            "protected": self.protected_branches_only
        }
        return parameters

    def get_request_headers(self) -> dict:
        headers = {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {self.pat}",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        return headers


class SupportedMatchMethod(Enum):
    MATCH = 'match'
    SEARCH = 'search'
    FINDALL = 'findall'


def set_output(name, value):
    os.system(f"""echo "{name}={value}" >> $GITHUB_OUTPUT""")


def get_exponential_backoff_in_seconds(attempt_number: int) -> int:
    """
    Returns exponential back-off - depending on number of attempt.
    Considers that `attempt_number` starts from 0.
    Initial back-off - 4 second.
    """
    return pow(attempt_number + 2, 2)


def fetch_repo_branches(request_data: FetchRequestData):
    url: str = request_data.get_request_url()
    headers: dict = request_data.get_request_headers()
    parameters: dict = request_data.get_request_parameters()

    print(f"::debug::Start fetching package metadata")

    print(parameters)

    for attempt in range(request_data.attempts_limit):
        print(
            f"::debug::Fetching package metadata - attempt {attempt + 1} / {request_data.attempts_limit}")
        try:
            response = requests.get(
                url=url, params=parameters, headers=headers)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            if attempt == request_data.attempts_limit - 1:
                raise RuntimeError(f"{e}")

            if attempt < request_data.attempts_limit - 1:
                print(
                    f"Exception occurred: {type(e).__name__} - {e}. Retrying.")
                back_off = get_exponential_backoff_in_seconds(attempt)
                print(
                    f"::debug::Sleep for {back_off} seconds before next attempt")
                time.sleep(back_off)
                continue
        break

    print(f"::debug::Finish fetching metadata")

    return response.json()


def get_branches_list(package_metadata) -> list:
    tags = []
    for key in package_metadata:
        tags.append(key["name"])
    return tags


def apply_regex_to_list(regex: str, branches: list, perform_method: SupportedMatchMethod):
    regex = re.compile(regex)
    method: function = regex.match
    if (perform_method == SupportedMatchMethod.FINDALL):
        method = regex.match
    if (perform_method == SupportedMatchMethod.SEARCH):
        method = regex.search
    print(f"::debug::Applying regex {regex} via {perform_method}")
    return list(filter(method, branches))


def main():
    repo_name = os.environ["INPUT_REPO_NAME"]
    organization = os.environ["INPUT_ORGANIZATION"]
    pat = os.environ["INPUT_PAT"]
    protected_branches_only = os.environ["INPUT_FETCH_PROTECTED_BRANCHES_ONLY"] == "true"
    attempts_limit = int(os.environ["INPUT_RETRIES"]) + 1
    regex = ""
    perform_match_method_input = ""
    perform_match_method = -1

    if os.environ.get('INPUT_REGEX') is not None:
        regex = os.environ["INPUT_REGEX"]

    try:
        perform_match_method_input = os.environ["INPUT_PERFORM_MATCH_METHOD"].upper(
        )
        if hasattr(SupportedMatchMethod, perform_match_method_input):
            perform_match_method = SupportedMatchMethod[perform_match_method_input]
        else:
            raise ProvidedMatchMethodNotSupportedOrIncorrect(
                f"Match method {perform_match_method_input} is not supported or incorrect")
    except Exception as e:
        raise RuntimeError(f"{e}")

    request_data = FetchRequestData(
        repo_name=repo_name,
        organization=organization,
        pat=pat,
        protected_branches_only=protected_branches_only,
        attempts_limit=attempts_limit
    )

    request_response = fetch_repo_branches(request_data)
    branches = get_branches_list(request_response)

    if (regex != ""):
        branches = apply_regex_to_list(regex, branches, perform_match_method)

    print("::group::Parse Semver Outputs")
    print(f"repo-branches={branches}")
    print("::endgroup::")

    set_output("repo-branches", branches)


if __name__ == "__main__":
    main()
