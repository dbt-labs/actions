# Filter Release Branches Action

Filters release branches to include only actively supported versions for testing.

## What it does

This action implements dynamic branch selection for release testing:

1. **Always includes baseline**: `1.7.latest` (minimum supported version)
2. **Includes last 2 minor versions**: Automatically selects the two most recent minor versions
3. **Optionally includes main**: Can add the `main` branch to the output

## Why?

- **No manual maintenance**: No need to update regex patterns when versions reach EOL
- **Automatic adaptation**: As new versions are released and old branches removed, testing automatically adjusts
- **Resource efficient**: Only tests actively supported versions, reducing CI usage

## Inputs

### `branches`
**Required**  
List of branches to filter. Accepts both JSON format (`["1.7.latest", "1.8.latest"]`) and Python list format (`['1.7.latest', '1.8.latest']`).

### `include_main`
**Optional** (default: `"true"`)  
Whether to include the `main` branch in the output. Set to `"false"` to exclude.

## Outputs

### `filtered-branches`
JSON array of filtered branch names, ready for use in a matrix strategy.

## Example Usage

```yaml
jobs:
  filter-branches:
    runs-on: ubuntu-latest
    outputs:
      branches: ${{ steps.filter.outputs.filtered-branches }}
    
    steps:
      - name: Get all branches
        uses: dbt-labs/actions/fetch-repo-branches@main
        id: fetch
        with:
          repo_name: my-repo
          organization: my-org
          pat: ${{ secrets.GITHUB_TOKEN }}
          fetch_protected_branches_only: true
          regex: '.*\.latest$'
          perform_match_method: "match"
      
      - name: Filter to supported versions
        uses: dbt-labs/actions/filter-release-branches@main
        id: filter
        with:
          branches: ${{ steps.fetch.outputs.repo-branches }}
          include_main: 'true'
  
  test:
    needs: filter-branches
    strategy:
      matrix:
        branch: ${{ fromJSON(needs.filter-branches.outputs.branches) }}
    steps:
      - uses: actions/checkout@v4
        with:
          ref: ${{ matrix.branch }}
      # ... run tests
```

## Filtering Logic

**Example 1**: Multiple versions exist
```
Input:  ['1.7.latest', '1.8.latest', '1.9.latest', '1.10.latest', '1.11.latest']
Output: ["1.7.latest", "1.10.latest", "1.11.latest", "main"]
```
→ Baseline (1.7) + last 2 versions (1.10, 1.11) + main

**Example 2**: Baseline is recent
```
Input:  ['1.6.latest', '1.7.latest', '1.8.latest']
Output: ["1.7.latest", "1.8.latest", "main"]
```
→ Baseline is one of the last 2, so only these versions

**Example 3**: After deprecation
```
Input:  ['1.7.latest', '1.10.latest', '1.11.latest']  # 1.8, 1.9 removed
Output: ["1.7.latest", "1.10.latest", "1.11.latest", "main"]
```
→ All remaining versions are tested (baseline + 2 others)

## Version Pattern

Branches must match the pattern `X.Y.latest` where X and Y are integers (e.g., `1.7.latest`, `2.0.latest`).

Invalid formats are skipped with a debug message.
