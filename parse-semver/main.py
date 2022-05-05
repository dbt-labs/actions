import os
from packaging.version import parse, Version


def main():
    input_version = os.environ["INPUT_VERSION"]
    parsed_version = parse(input_version)
    assert parsed_version.release, f"Not a valid version: {input_version}"
    assert isinstance(parsed_version, Version)

    # ('rc', 2) -> pre_release_type = rc, pre_release_version = 2
    pre_release_type, pre_release_version = (
        parsed_version.pre
        if parsed_version.pre else ('', '')
    )
    assert isinstance(pre_release_type, str),\
        f"Not a valid pre-release type (ex: rc, b): {pre_release_type}"

    pre_release = pre_release_type + str(pre_release_version)
    is_pre_release = parsed_version.pre is not None
    is_pre_release_truthy = 1 if is_pre_release else 0

    print("::group::Parse Semver Outputs")
    print(f"version={parsed_version.public}")
    print(f"base-version={parsed_version.base_version}")
    print(f"major={parsed_version.major}")
    print(f"minor={parsed_version.minor}")
    print(f"patch={parsed_version.micro}")
    print(f"pre-release-type={pre_release_type}")
    print(f"pre-release-version={pre_release_version}")
    print(f"pre-release={pre_release}")
    print(f"is-pre-release={is_pre_release_truthy}")
    print("::endgroup::")

    print(f"::set-output name=version::{parsed_version.public}")
    print(f"::set-output name=base-version::{parsed_version.base_version}")
    print(f"::set-output name=major::{parsed_version.major}")
    print(f"::set-output name=minor::{parsed_version.minor}")
    print(f"::set-output name=patch::{parsed_version.micro}")
    print(f"::set-output name=pre-release-type::{pre_release_type}")
    print(f"::set-output name=pre-release-version::{pre_release_version}")
    print(f"::set-output name=pre-release::{pre_release}")
    print(f"::set-output name=is-pre-release::{is_pre_release_truthy}")


if __name__ == "__main__":
    main()
