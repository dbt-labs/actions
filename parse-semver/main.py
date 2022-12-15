import os
from packaging.version import parse, Version

# The pattern is: "{name}={value}" >> $GITHUB_OUTPUT
def setOutput(name, value):
  print(f""""{name}={value}" >> $GITHUB_OUTPUT""");

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

    setOutput("version", parsed_version.public);
    setOutput("base-version", parsed_version.base_version);
    setOutput("major", parsed_version.major);
    setOutput("minor", parsed_version.minor);
    setOutput("patch", parsed_version.micro);
    setOutput("pre-release-type", pre_release_type);
    setOutput("pre-release-version", pre_release_version);
    setOutput("pre-release", pre_release);
    setOutput("is-pre-release", is_pre_release_truthy);

if __name__ == "__main__":
    main()
