import codecs
import json
import os
import pkg_resources
from contextlib import closing
from dataclasses import dataclass
from typing import Optional
from urllib.request import urlopen
from hashlib import sha256


class PackageVersionNotFoundWarning(UserWarning):
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


def setOutput(name, value):
  os.system(f"""echo "{name}={value}" >> $GITHUB_OUTPUT""");


def lookup_package(name, version=None, check_test_index=None):
    pkg_data = None
    
    package_index_url = "https://pypi.io/pypi/{}/json";
    if check_test_index:
        package_index_url = "https://test.pypi.org/pypi/{}/json"

    with closing(urlopen(package_index_url.format(name))) as f:
        reader = codecs.getreader("utf-8")
        pkg_data = json.load(reader(f))
    if pkg_data is None:
        raise RuntimeError(f"no package data for: {name}")
    d = {}
    d['name'] = pkg_data['info']['name']
    d['version'] = pkg_data['info'].get('version', '')
    d['homepage'] = pkg_data['info'].get('home_page', '')
    d['summary'] = pkg_data['info'].get('summary', '')
    d['author'] = pkg_data['info'].get('author', '')
    d['author_email'] = pkg_data['info'].get('author_email', '')
    artifact = None
    if version:
        for pypi_version in pkg_data['releases']:
            if pkg_resources.safe_version(pypi_version) == version:
                for version_artifact in pkg_data['releases'][pypi_version]:
                    if version_artifact['packagetype'] == 'sdist':
                        artifact = version_artifact
                        d['version'] = version
                        break
        if artifact is None:
            print("::warning::Could not find an exact version match for "
                  f"{name} version {version}; using newest instead")

    if artifact is None:  # no version given or exact match not found
        for url in pkg_data['urls']:
            if url['packagetype'] == 'sdist':
                artifact = url
                break

    if artifact:
        d['url'] = artifact['url']
        if 'digests' in artifact and 'sha256' in artifact['digests']:
            print(f"::debug::Using provided checksum for {name}")
            d['checksum'] = artifact['digests']['sha256']
        else:
            print(f"::debug::Fetching sdist to compute checksum for {name}")
            with closing(urlopen(artifact['url'])) as f:
                d['checksum'] = sha256(f.read()).hexdigest()
            print(f"::debug::Done fetching {name}")
    else:  # no sdist found
        d['url'] = ''
        d['checksum'] = ''
        print("::warning::No sdist found for {name}")
    d['checksum_type'] = 'sha256'
    return d


def main():
    package = os.environ["INPUT_PACKAGE"]
    version = os.environ["INPUT_VERSION"]
    check_test_index = os.environ["INPUT_CHECK-TEST-INDEX"]

    package_info = PackageInfo(**lookup_package(package, version=version, check_test_index=check_test_index))

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

    setOutput("name", package_info.name)
    setOutput("version", package_info.version)
    setOutput("homepage", package_info.homepage)
    setOutput("summary", package_info.summary)
    setOutput("author", package_info.author)
    setOutput("author-email", package_info.author_email)
    setOutput("source-url", package_info.url)
    setOutput("source-checksum", package_info.checksum)
    setOutput("source-checksum-type", package_info.checksum_type)  # noqa


if __name__ == "__main__":
    main()
