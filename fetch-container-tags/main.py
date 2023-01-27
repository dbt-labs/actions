import requests
import re
import os
import json
import time
from enum import Enum
from dataclasses import dataclass


@dataclass
class FetchRequestData:
    package_type: str
    package_name: str
    organization: str
    pat: str
    attempts_limit: int

    def get_request_url(self) -> str:
        url = f"https://api.github.com/orgs/{self.organization}/packages/{self.package_type}/{self.package_name}/versions"
        return url

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


def fetch_package_metadata(request_data: FetchRequestData):
    url: str = request_data.get_request_url()
    headers: dict = request_data.get_request_headers()

    for attempt in range(request_data.attempts_limit):
        print(
            f"::debug::Fetching package metadata - attempt {attempt + 1} / {request_data.attempts_limit}")
        try:
            response = requests.get(url=url, headers=headers)
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

    return response.json()


def get_tags_list(package_metadata) -> list:
    tags = []
    for key in package_metadata:
        tags += key.get('metadata', {}).get('container', {}).get('tags')
    return tags


def apply_regex_to_tags(regex: str, tags: list, perform_method: SupportedMatchMethod):
    regex = re.compile(regex)
    method: function = regex.match
    if (perform_method == SupportedMatchMethod.FINDALL):
        method = regex.match
    if (perform_method == SupportedMatchMethod.SEARCH):
        method = regex.search
    return list(filter(method, tags))


def main():
    package_name = os.environ["INPUT_PACKAGE_NAME"]
    package_type = "container"
    organization = os.environ["INPUT_ORGANIZATION"]
    pat = os.environ["INPUT_PAT"]
    attempts_limit = int(os.environ["INPUT_RETRIES"]) + 1
    regex = ""

    if os.environ.get('INPUT_REGEX') is not None:
        regex = os.environ["INPUT_REGEX"]

    perform_match_method_input = os.environ["INPUT_PERFORM_MATCH_METHOD"].upper(
    )
    perform_match_method = -1
    if hasattr(SupportedMatchMethod, perform_match_method_input):
        perform_match_method = SupportedMatchMethod[perform_match_method_input]
    else:
        raise RuntimeError("Error")

    request_data = FetchRequestData(
        package_type=package_type,
        package_name=package_name,
        organization=organization,
        pat=pat,
        attempts_limit=attempts_limit
    )

    request_response = fetch_package_metadata(request_data)
    container_tags = get_tags_list(request_response)

    if (regex != ""):
        container_tags = apply_regex_to_tags(
            regex, container_tags, perform_match_method)

    print(f"::debug::tag list: {json.dumps(container_tags)}")

    set_output("container-tags", json.dumps(container_tags))


if __name__ == "__main__":
    main()
