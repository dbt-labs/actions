# Python Package Info Actions

A [GitHub Action](https://github.com/features/actions) that fetches release info from [PyPI](https://pypi.org/)'s API.

Example usage:

```yaml
name: Example Workflow for Python Package Info Action
on: push
jobs:
  parse:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Get Package Info
        id: package-info
        uses: dbt-labs/actions/py-package-info
        with:
          package: "dbt-snowflake"

      - name: Use Package Info
        run: |
          echo name: ${{ steps.package-info.outputs.name }}
          echo version: ${{ steps.package-info.outputs.version }}
          echo homepage: ${{ steps.package-info.outputs.homepage }}
          echo summary: ${{ steps.package-info.outputs.summary }}
          echo author: ${{ steps.package-info.outputs.author }}
          echo author-email: ${{ steps.package-info.outputs.author-email }}
          echo source-url: ${{ steps.package-info.outputs.source-url }}
          echo source-checksum: ${{ steps.package-info.outputs.source-checksum }}
          echo source-checksum-type: ${{ steps.package-info.outputs.source-checksum-type }}
```

### Inputs

| Property | Required | Description                           |
| -------- | -------- | ------------------------------------- |
| package  | yes      | Name of package to fetch from PyPI    |
| version  | no       | Version of package to fetch from PyPI |

### Outputs (with `dbt-snowflake` as an example input)

| Property             | Example                                                     | Description                               |
| -------------------- | ----------------------------------------------------------- | ----------------------------------------- |
| name                 | `dbt-snowflake`                                             | Package name                              |
| version              | `1.0.0`                                                     | Package version                           |
| homepage             | `https://github.com/dbt-labs/dbt-snowflake`                 | Package homepage                          |
| summary              | `The Snowflake adapter plugin for dbt`                      | Package summary                           |
| author               | `dbt Labs`                                                  | Package author                            |
| author-email         | `info@dbtlabs.com`                                          | Package author email                      |
| source-url           | `https://files.pythonhosted..../dbt-snowflake-1.0.0.tar.gz` | Package source distribution url           |
| source-checksum      | `a263274d6af430edf.....7ec8b1c82cb30b25e42be9a1c`           | Package source distribution checksum      |
| source-checksum-type | `sha256`                                                    | Package source distribution checksum type |

### Development

- This action is tested by [this](../.github/workflows/py-package-info.yml) workflow.
- You can run this test workflow locally with [act](https://github.com/nektos/act) by running `act -W .github/workflows/py-package-info.yml`
  - Note: `act` does not handle the `continue-on-error` logic properly, so the invalid test case will fail locally.
