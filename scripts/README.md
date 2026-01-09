# scripts

A directory for automation scripts used in actions/workflows.

|Directory/Script|Description|
|-|-|
|[core-triage](core-triage)|Python script(s) for automating the ["Core triage" project](https://github.com/orgs/dbt-labs/projects/22) by calling GitHub APIs.|
|[filter_branches.py](filter_branches.py)|Branch filtering logic for dynamic release branch testing. Filters *.latest branches to select 1.7.latest (baseline) + last 2 minor versions.|
