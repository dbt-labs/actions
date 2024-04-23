# set the core members for changie to skip in annotations
CHANGIE_CORE_TEAM=$CORE_TEAM_MEMBERS

# this is a pre-release
if [[ $IS_PRE_RELEASE -eq 1 ]]; then
    changie batch $BASE_VERSION --move-dir '$BASE_VERSION' --prerelease $PRE_RELEASE

# this is a final release with associated pre-releases
elif [[ -d ".changes/$BASE_VERSION" ]]; then
    changie batch $BASE_VERSION --include '$BASE_VERSION' --remove-prereleases

# this is a final release with no associated pre-releases
else
    changie batch $BASE_VERSION
fi

changie merge
