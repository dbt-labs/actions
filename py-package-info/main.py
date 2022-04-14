import codecs
import json
import os
import pkg_resources
import warnings
from contextlib import closing
from dataclasses import dataclass
from typing import Optional
from urllib.request import urlopen
from hashlib import sha256
import logging


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


def lookup_package(name, version=None):
    pkg_data = None
    with closing(urlopen("https://pypi.io/pypi/{}/json".format(name))) as f:
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
                        break
        if artifact is None:
            warnings.warn("Could not find an exact version match for "
                          "{} version {}; using newest instead".
                          format(name, version), PackageVersionNotFoundWarning)

    if artifact is None:  # no version given or exact match not found
        for url in pkg_data['urls']:
            if url['packagetype'] == 'sdist':
                artifact = url
                break

    if artifact:
        d['url'] = artifact['url']
        d['version'] = version
        if 'digests' in artifact and 'sha256' in artifact['digests']:
            logging.debug("Using provided checksum for %s", name)
            d['checksum'] = artifact['digests']['sha256']
        else:
            logging.debug("Fetching sdist to compute checksum for %s", name)
            with closing(urlopen(artifact['url'])) as f:
                d['checksum'] = sha256(f.read()).hexdigest()
            logging.debug("Done fetching %s", name)
    else:  # no sdist found
        d['url'] = ''
        d['checksum'] = ''
        warnings.warn("No sdist found for %s" % name)
    d['checksum_type'] = 'sha256'
    return d


def main():
    package = os.environ["INPUT_PACKAGE"]
    version = os.environ["INPUT_VERSION"]

    package_info = PackageInfo(**lookup_package(package, version=version))

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

    print(f"::set-output name=name::{package_info.name}")
    print(f"::set-output name=version::{package_info.version}")
    print(f"::set-output name=homepage::{package_info.homepage}")
    print(f"::set-output name=summary::{package_info.summary}")
    print(f"::set-output name=author::{package_info.author}")
    print(f"::set-output name=author-email::{package_info.author_email}")
    print(f"::set-output name=source-url::{package_info.url}")
    print(f"::set-output name=source-checksum::{package_info.checksum}")
    print(f"::set-output name=source-checksum-type::{package_info.checksum_type}")  # noqa


if __name__ == "__main__":
    main()
