if $IS_PRE_RELEASE; then
    echo "prerelease=--prerelease" >> $GITHUB_OUTPUT
fi

if $IS_DRAFT; then
    echo "draft=--draft" >> $GITHUB_OUTPUT
fi
