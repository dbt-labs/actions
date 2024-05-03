# Style Guide


## Context

We need a style guide for our actions repo. This structure provides the following benefits:
- developers can spend more time on solving the problem
- PR reviews are limited to discussing intent
- format related feedback can point to a collective style guide instead of personal preferences
- consumers know how to find what they're looking for
- developers know where to look when fixing something

## Options

This style guide is a collection of individual options. Instead of providing permutations of these options,
this ADR provides a section for an initial proposal for several style guide topics and a section
that contains the agreed upon formats. This ADR should be updated to remove reference to the initial
proposal prior to merging in order to avoid confusion.

As an alternative, each topic could be its own ADR. Reviewers may request this approach, which will require
breaking this ADR into several ADRs and associated PRs.

## Proposal

### Actions
- actions live at the repo root so that usage looks like `uses: dbt-labs/actions/<action-name>@<tag>`
- actions live in directories with the format `<platform/tool>/<resource>/<action>`, e.g.
    - `./hatch/environment/create`
    - `./pypi/release/view`
- actions have a generic scope with a focused context to support reusability
- actions perform a single task on a single object within the context of a platform/tool

### Workflows
- workflows need to live in `.github/workflows`
- we prefer actions to workflows
    - actions can be inserted into other actions and as part of workflows
    - actions can inherit environment variables

### Formatting
- job ids, step ids, and variables are in kebab case
- job names, step names, and description fields follow dbt docs standards (capitalize first word only)
- extra descriptors should be avoided unless required for disambiguation, e.g.
    - `version-number` -> `version`
    - `archive-name` -> `archive`
- yaml files use a four space tab
- scripts use environment variables in `env` instead of inline substitution like `${{ inputs.value }}`

### Tools
- formatter: `pretty-format-yaml` @ https://github.com/macisamuele/language-formatters-pre-commit-hooks
    - `yamlfmt` @ https://github.com/jumanjihouse/pre-commit-hook-yamlfmt
    - `yamlfmt` @ https://github.com/google/yamlfmt (requires Go)
- linter: `check-yaml` @ https://github.com/pre-commit/pre-commit-hooks
    - `yamllint` @ https://github.com/adrienverge/yamllint

Alternatives should support `pre-commit`: https://pre-commit.com/hooks.html

### Logging
- the first step of an action logs non-secret inputs as a debug log
- the last step of an action logs non-secret outputs as a debug log
- any step that changes state outside of the scope of the action has an associated info log
- any step that results in predictable failure (e.g. unit tests) has an associated error log
- any step that results in a predictable skip (e.g. version bump not needed) has an associated warning log
- log types are standardized as an action in this repo

### Docs
- all actions and workflows are discoverable in the repo `README.md`
- all workflows have a file docstring in the "what, why, when" format

### Versioning
- actions and workflows are not versioned individually; instead, the entire repo is versioned, similar to the `pre-commit` hooks repo
- tags should be used to communicate new functionality
- tagging should follow calver

## Decision

## Consequences
