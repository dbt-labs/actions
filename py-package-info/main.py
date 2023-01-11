import codecs
import json
import os
import pkg_resources
import time
from contextlib import closing
from dataclasses import dataclass
from typing import Optional
from urllib.request import urlopen
from hashlib import sha256


class PackageVersionNotFoundWarning(UserWarning):
    pass


class PackageMetadataNotFoundInPyPIError(Exception):
    """The package index didn't return metadata for the specified package"""
    pass


class PackageVersionNotFoundInPyPIError(Exception):
    """The specified package version is not presented in the package index"""
    pass


@dataclass
class PackageInfo:
    name: str
    version: Optional[str]
    homepage: Optional[str]
    summary: Optional[str]
    author: Optional[str]
    author_email: Optional[str]
    url: Optional[str]
    checksum: Optional[str]
    checksum_type: Optional[str]


def set_output(name, value):
    os.system(f"""echo "{name}={value}" >> $GITHUB_OUTPUT""")


def get_exponential_backoff_in_seconds(attempt_number: int) -> int:
    """
    Returns exponential back-off - depending on number of attempt.
    Considers that `attempt_number` starts from 0.
    Initial back-off - 4 second.
    """
    return pow(attempt_number + 2, 2)


def fetch_package_data(name, package_index_url):
    metadata = None
    with closing(urlopen(package_index_url.format(name))) as f:
        print(
            f"::debug::Fetching metadata for {name} from {package_index_url.format(name)}")
        reader = codecs.getreader("utf-8")
        metadata = json.load(reader(f))
        print(f"::debug::Done fetching metadata")
    return metadata


def get_package_info(package_metadata):
    info = {}
    info['name'] = package_metadata['info']['name']
    info['version'] = package_metadata['info'].get('version', '')
    info['homepage'] = package_metadata['info'].get('home_page', '')
    info['summary'] = package_metadata['info'].get('summary', '')
    info['author'] = package_metadata['info'].get('author', '')
    info['author_email'] = package_metadata['info'].get('author_email', '')
    return info


def get_artifact_version(metadata, version):
    artifact = None
    for pypi_version in metadata['releases']:
        if pkg_resources.safe_version(pypi_version) == version:
            for version_artifact in metadata['releases'][pypi_version]:
                if version_artifact['packagetype'] == 'sdist':
                    artifact = version_artifact
                    break
    return artifact


def get_latest_artifact_url(metadata):
    artifact = None

    for url in metadata['urls']:
        if url['packagetype'] == 'sdist':
            artifact = url
            break

    return artifact


def get_artifact_checksum(artifact, package_info):
    checksum = None
    if 'digests' in artifact and 'sha256' in artifact['digests']:
        print(f"::debug::Using provided checksum for {package_info['name']}")
        checksum = artifact['digests']['sha256']
    else:
        print(
            f"::debug::Fetching sdist to compute checksum for {package_info['name']}")
        with closing(urlopen(artifact['url'])) as f:
            checksum = sha256(f.read()).hexdigest()
        print(f"::debug::Done fetching {package_info['name']}")
    return checksum


def lookup_package(name, check_test_index, version=None, attempts_limit=3):
    package_metadata = None
    package_info = {}
    artifact = None

    package_index_url = "https://pypi.io/pypi/{}/json"
    if check_test_index:
        package_index_url = "https://test.pypi.org/pypi/{}/json"

    print(f"::debug::Checking the following package index {package_index_url}")

    for attempt in range(attempts_limit):
        print(
            f"::debug::Fetching package metadata - attempt {attempt + 1} / {attempts_limit}")
        try:
            package_metadata = fetch_package_data(name, package_index_url)

            if package_metadata is None:
                raise PackageMetadataNotFoundInPyPIError(
                    f"Could not find package metadata for: {name}")
            package_info = get_package_info(package_metadata)

            if version:
                artifact = get_artifact_version(package_metadata, version)
                if artifact is None:
                    raise PackageVersionNotFoundInPyPIError("Could not find an exact version match for "
                                                            f"{name} version {version}")
                else:
                    package_info['version'] = version
        except Exception as e:
            print(f"Exception occurred: {type(e).__name__} - {e}. Retrying.")
            if attempt == attempts_limit - 1 and not isinstance(e, PackageVersionNotFoundInPyPIError):
                raise RuntimeError(f"{e}")
            back_off = get_exponential_backoff_in_seconds(attempt)
            print(f"::debug::Sleep for {back_off} seconds before next attempt")
            time.sleep(back_off)
            continue
        break

    if artifact is None:
        print("::warning::Could not find an exact version match for "
              f"{name} version {version} after {attempts_limit} attempts. Using newest version instead.")
        artifact = get_latest_artifact_url(package_metadata)

    if artifact:
        package_info['url'] = artifact['url']
        package_info['checksum'] = get_artifact_checksum(
            artifact, package_info)
    else:  # no sdist found
        package_info['url'] = ''
        package_info['checksum'] = ''
        print("::warning::No sdist found for {name}")
    package_info['checksum_type'] = 'sha256'
    return package_info


def main():
    package = os.environ["INPUT_PACKAGE"]
    version = os.environ["INPUT_VERSION"]
    check_test_index = os.environ["INPUT_CHECK-TEST-INDEX"] == "true"
    attempts_count = int(os.environ["INPUT_RETRIES"]) + 1

    package_info = PackageInfo(
        **lookup_package(package, check_test_index, version=version, attempts_limit=attempts_count))

    print("::group::Python Package Info Outputs")
    print(f"name={package_info.name}")
    print(f"version={package_info.version}")
    print(f"homepage={package_info.homepage}")
    print(f"summary={package_info.summary}")
    print(f"author={package_info.author}")
    print(f"author-email={package_info.author_email}")
    print(f"source-url={package_info.url}")
    print(f"source-checksum={package_info.checksum}")
    print(f"source-checksum-type={package_info.checksum_type}")
    print("::endgroup::")

    set_output("name", package_info.name)
    set_output("version", package_info.version)
    set_output("homepage", package_info.homepage)
    set_output("summary", package_info.summary)
    set_output("author", package_info.author)
    set_output("author-email", package_info.author_email)
    set_output("source-url", package_info.url)
    set_output("source-checksum", package_info.checksum)
    set_output("source-checksum-type", package_info.checksum_type)  # noqa


if __name__ == "__main__":
    main()
