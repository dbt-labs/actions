# Fetch Repo Branches

A [GitHub Action](https://github.com/features/actions) for fetching branches via GitHub API.

Example usage:

```yaml
name: Example Workflow for Fetch Repo Branches
on: push
jobs:
  parse:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: "Fetch ${{ inputs.package_name }} Protected Branches Metadata"
        uses: dbt-labs/actions/fetch-repo-branches
        id: get-latest-branches
        with:
          repo_name: "dbt-core"
          organization: "dbt-labs"
          pat: ${{ secrets.GITHUB_TOKEN }}
          fetch_protected_branches_only: true
          regex: "^1.*.latest"
          perform_match_method: "match"
          retries: 3

      - name: Display Latest Branches
        run: |
          echo container tags: ${{ steps.get-latest-branches.outputs.repo-branches }}
```

### Inputs

| Property                      | Required | Default        | Description                                                   |
| ----------------------------- | -------- | -------------- | ------------------------------------------------------------- |
| repo_name                     | yes      | -              | Repo name                                                     |
| organization                  | yes      | -              | Organization that owns repo                                   |
| pat                           | yes      | -              | PAT for fetch request                                         |
| fetch_protected_branches_only | no       | `false`        | Adjust request to fetch only protected branches               |
| regex                         | no       | `empty string` | Filter container tags                                         |
| perform_match_method          | no       | `match`        | Select which method use to filter tags (search/match/findall) |
| retries                       | no       | `3`            | Retries for fetch request                                     |

### Outputs

| Property       | Example                                                              | Description            |
| -------------- | -------------------------------------------------------------------- | ---------------------- |
| container-tags | `['1.0.latest', '1.1.latest', '1.2.latest', '1.3.latest', '1.4.latest']` | List of container tags |