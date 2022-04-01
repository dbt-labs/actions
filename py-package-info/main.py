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
    with closing(urlopen("https://pypi.io/pypi/{}/json".format(name))) as f:
        reader = codecs.getreader("utf-8")
        pkg_data = json.load(reader(f))
    d = {}
    d['name'] = pkg_data['info']['name']
    d['version'] = pkg_data['info'].get('version', '')
    d['homepage'] = pkg_data['info'].get('home_page', '')
    d['summary'] = pkg_data['info'].get('summary', '')
    d['author'] = pkg_data['info'].get('author', '')
    d['author_email'] = pkg_data['info'].get('author_email', '')
    artefact = None
    if version:
        for pypi_version in pkg_data['releases']:
            if pkg_resources.safe_version(pypi_version) == version:
                for version_artefact in pkg_data['releases'][pypi_version]:
                    if version_artefact['packagetype'] == 'sdist':
                        artefact = version_artefact
                        break
        if artefact is None:
            warnings.warn("Could not find an exact version match for "
                          "{} version {}; using newest instead".
                          format(name, version), PackageVersionNotFoundWarning)

    if artefact is None:  # no version given or exact match not found
        for url in pkg_data['urls']:
            if url['packagetype'] == 'sdist':
                artefact = url
                break

    if artefact:
        d['url'] = artefact['url']
        if 'digests' in artefact and 'sha256' in artefact['digests']:
            logging.debug("Using provided checksum for %s", name)
            d['checksum'] = artefact['digests']['sha256']
        else:
            logging.debug("Fetching sdist to compute checksum for %s", name)
            with closing(urlopen(artefact['url'])) as f:
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
