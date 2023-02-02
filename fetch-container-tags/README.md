# Fetch Container Tags

A [GitHub Action](https://github.com/features/actions) for fetching container tags from [GitHub packages](https://ghcr.io).

Example usage:

```yaml
name: Example Workflow for Fetch Container Tags
on: push
jobs:
  fetch-latest-tags:
    runs-on: ubuntu-latest
    
    outputs:
      latest-tags: ${{ steps.fetch-latest-tags.outputs.container-tags }}
    
    steps:
      - uses: actions/checkout@v2
      
      - name: "Fetch dbt-postgres Container Tags"
        id: get-latest-tags
        uses: dbt-labs/actions/fetch-container-tags
        with:
          package_name: "dbt-postgres"
          organization: "dbt-labs"
          pat: ${{ secrets.GITHUB_TOKEN }}
          regex: "latest$"
          perform_match_method: "search"
          retries: 3

      - name: "Display Container Tags"
        run: |
          echo container latest tags: ${{ steps.fetch-latest-tags.outputs.container-tags }}
    
  dynamic-matrix:
    runs-on: ubuntu-latest
    needs: fetch-latest-tags

    strategy:
      fail-fast: false
      matrix:
        tag: ${{ fromJSON(needs.fetch-latest-tags.outputs.latest-tags) }}
    
    steps:
      - name: "Display Tag Name"
        run: |
          echo container tag: ${{ matrix.tag }}
```

### Inputs

| Property             | Required | Default        | Description                                                   |
| -------------------- | -------- | -------------- | ------------------------------------------------------------- |
| package_name         | yes      | -              | Container name                                                |
| organization         | yes      | -              | Organization that owns the package                            |
| pat                  | yes      | -              | PAT for fetch request                                         |
| regex                | no       | `empty string` | Filter container tags                                         |
| perform_match_method | no       | `match`        | Select which method use to filter tags (search/match/findall) |
| retries              | no       | `3`            | Retries for fetch request                                     |

### Outputs

| Property       | Example                                                              | Description            |
| -------------- | -------------------------------------------------------------------- | ---------------------- |
| container-tags | `['1.2.latest', 'latest', '1.3.latest', '1.1.latest', '1.0.latest']` | List of container tags |
