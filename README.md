# GitHub Actions and Workflows for maintaining dbt

A set of GitHub [Actions](https://docs.github.com/en/actions/creating-actions/about-custom-actions) and [Reusable Workflows](https://docs.github.com/en/actions/using-workflows/reusing-workflows) for automating common tasks related to developing, maintaining, and testing dbt-core, database adapter plugins, and other dbt-labs open source projects. 

Actions and workflows should be self documented.  See individual actions for more info and instructions on how to use.

### Actions

- [Parse Semver Action](parse-semver)
- [Python Package Info Action](py-package-info)
- [Fetch Repository branches](fetch-repo-branches)
- [Fetch COntainer Tags](fetch-container-tags)

### Workflows

- [Jira Issue Transition](.github/workflows/jira-transition.yml)
- [Jira Label Mirroring](.github/workflows/jira-label.yml)
- [Jira Issue Creation](.github/workflows/jira-creation.yml)
- [Changelog Existence Check](.github/workflows/changelog-existence.yml)
- [Generic Label Swapping](.github/workflows/swap-labels.yml)
- [Scheduled Installation Tests](.github/workflows/test-dbt-installation-main.yml)
- [Cut the `.latest` Branch for an rc1](.github/workflows/cut-release-branch.yml)

## Releasing

See each repository.  Parent workflows live in [dbt-labs/dbt-release](https://github.com/dbt-labs/dbt-release/)

## Development

- Each Action will have instructions for development.
- It is recommended to use [act](https://github.com/nektos/act) for testing locally where possible.
- Actions have a cooresponding workflow for automated testing.
- Here is [documentation](https://docs.github.com/en/actions/creating-actions) for creating custom actions.

## Debugging

You can enable debug logging for GHA by setting secret values for your repository. See [docs](https://docs.github.com/en/github-ae@latest/actions/monitoring-and-troubleshooting-workflows/enabling-debug-logging) for more info.

- Set `ACTIONS_RUNNER_DEBUG` to `true` to enable runner diagnostic logging.
- Set `ACTIONS_STEP_DEBUG` to `true` to enable run step debug logging.
