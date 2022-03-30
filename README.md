# GitHub Actions and Workflows for maintaining dbt

A set of GitHub [Actions](https://docs.github.com/en/actions/creating-actions/about-custom-actions) and [Reusable Workflows](https://docs.github.com/en/actions/using-workflows/reusing-workflows) for automating common tasks related to developing, maintaining, and releasing dbt-core and database adapter plugins. See individual actions for more info and instructions on how to use.

### Actions

- [Parse Semver Action](parse-semver)
- [Python Package Info Action](py-package-info)

### Workflows

- [Jira Issue Transition](.github/workflows/jira-transition.yml)
- [Jira Label Mirroring](.github/workflows/jira-label.yml)
- [Jira Issue Creation](.github/workflows/jira-creation.yml)

## Releasing

Create and push a new tag with the format `v#.#.#`. The [release GHA](https://github.com/dbt-labs/actions/actions/workflows/release.yml) will create or update tags for the major and minor version (e.g. `v1`, `v1.1`). For example:

```
git tag v1.2.3
git push --tags
```

The [release GHA](https://github.com/dbt-labs/actions/actions/workflows/release.yml) will create or update the `v1` and `v1.2` tags to point to the same commit as `v1.2.3`.

## Development

- Each Action will have instructions for development.
- It is recommended to use [act](https://github.com/nektos/act) for testing locally where possible.
- Actions have a cooresponding workflow for automated testing.
- Here is [documentation](https://docs.github.com/en/actions/creating-actions) for creating custom actions.
