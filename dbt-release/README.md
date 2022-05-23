### Prepare, Build, & Release dbt core and core adjacent packages

1. Commit version bump and generate changie changelog for release
2. Build release artifacts and upload to AWS
3. Release to GitHub
4. Release to PyPI


The intention is this action would be called in a workflow in `dbt-core` (and eventually all adapters).


#### Future Enhancements
1. Add Homebrew release as 5th step
2. Once this is hooked up in all adapters and Homebrew release is added, link them all together and add the docker release at the end to have a single button release for all core products