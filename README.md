# GitHub Actions and Workflows for maintaining dbt oss

A set of GitHub [Actions](https://docs.github.com/en/actions/creating-actions/about-custom-actions) and [Reusable Workflows](https://docs.github.com/en/actions/using-workflows/reusing-workflows) for automating common tasks related to developing, maintaining, and testing dbt-core, database adapter plugins, and other dbt-labs open source projects. 

Actions and workflows should be self documented.  See individual actions for more info and instructions on how to use.

### Actions

- [Parse Semver Action](parse-semver)
- [Python Package Info Action](py-package-info)
- [Fetch Repository branches](fetch-repo-branches)
- [Fetch COntainer Tags](fetch-container-tags)

### Workflows


- Changelog Handling
    - [Changelog Existence Check](.github/workflows/changelog-existence.yml)
- Scheduled Installation Tests
    - [Installation Tests](.github/workflows/test-dbt-installation-main.yml)
        - .github/workflows/test-dbt-installation-docker.yml
        - .github/workflows/test-dbt-installation-homebrew.yml
        - .github/workflows/test-dbt-installation-notify-job-statuses.yml
        - .github/workflows/test-dbt-installation-pip.yml
        - .github/workflows/test-dbt-installation-source.yml
    - [Release Branch Tests](.github/workflows/release-branch-tests.yml)
- [Cut the `.latest` Branch for an rc1](.github/workflows/cut-release-branch.yml)
- Generic Shared Workflows
    - [Label Swapping](.github/workflows/swap-labels.yml)
    - [Open Issue in Another repo](.github/workflows/open-issue-in-repo.yml )
    - [Scheduled Repository Cleanup After Releases](.github/workflows/repository-cleanup.yml )
    - [Stale Bot MAtrix](.github/workflows/stale-bot-matrix.yml )

- Jira Issue Syncing <deprecated>
    - .github/workflows/core-triage.yml
    - .github/workflows/cut-release-branch.yml
    - .github/workflows/jira-creation-actions.yml
    - .github/workflows/jira-creation.yml
    - .github/workflows/jira-label-actions.yml
    - .github/workflows/jira-label.yml
    - .github/workflows/jira-transition-actions.yml
    - .github/workflows/jira-transition.yml
- Version Bump <deprecated once `dbt-spark` moves off CircleCI>
    - .github/workflows/version-bump.yml
- Releasing <deprecated>
    - .github/workflows/release.yml 

## Releasing dbt-core and adapters

See each repository.  Parent workflows live in [dbt-labs/dbt-release](https://github.com/dbt-labs/dbt-release/)
