# Parse Semver Action

A [GitHub Action](https://github.com/features/actions) for parsing a semver string into a parts and return if the version is a pre-release. This action uses the Python [`packaging`](https://packaging.pypa.io/en/latest/) library for parsing version string. Version strings can be prefixed be `v` (ex. `v1.4.2`).

Example usage:

```yaml
name: Example Workflow for Parse Semver Action
on: push
jobs:
  parse:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Parse Semver
        id: parse-valid
        uses: dbt-labs/actions/parse-semver
        with:
          version: "1.2.3rc4"

      - name: Use Parsed Output
        run: |
          echo version: ${{ steps.parse-valid.outputs.version }}
          echo base-version: ${{ steps.parse-valid.outputs.base-version }}
          echo major: ${{ steps.parse-valid.outputs.major }}
          echo minor: ${{ steps.parse-valid.outputs.minor }}
          echo patch: ${{ steps.parse-valid.outputs.patch }}
          echo pre-release: ${{ steps.parse-valid.outputs.pre-release }}
          echo pre-release-version: ${{ steps.parse-valid.outputs.pre-release-version }}
          echo pre-release-type: ${{ steps.parse-valid.outputs.pre-release-type }}
          echo is-pre-release: ${{ steps.parse-valid.outputs.is-pre-release }}
```

### Inputs

| Property | Default | Description            |
| -------- | ------- | ---------------------- |
| version  |         | Semver string to parse |

### Outputs (with `1.2.3rc4` as an example input)

| Property            | Example    | Description                                     |
| ------------------- | ---------- | ----------------------------------------------- |
| version             | `1.2.3rc4` | Parsed version                                  |
| base-version        | `1.2.3`    | Base version                                    |
| major               | `1`        | Major version                                   |
| minor               | `2`        | Major version                                   |
| patch               | `3`        | Patch version                                   |
| pre-release         | `rc4`      | Entire pre-release version                      |
| pre-release-version | `4`        | Version part of pre-release                     |
| pre-release-type    | `rc`       | Type of pre-release                             |
| is-pre-release      | `1`        | Determines if version is a pre-release (1 \| 0) |

### Development

- This action is tested by [this](../.github/workflows/parse-semver.yml) workflow.
- You can run this test workflow locally with [act](https://github.com/nektos/act) by running `act -W .github/workflows/parse-semver.yml`
  - Note: `act` does not handle the `continue-on-error` logic properly, so the invalid test case will fail locally.
