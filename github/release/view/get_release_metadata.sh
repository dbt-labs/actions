# RELEASE is from get_release.sh
sha=$(jq -r '.targetCommitish' <<< "$RELEASE")
echo "sha=$sha" >> $GITHUB_OUTPUT

is-draft=$(jq -r '.isDraft' <<< "$RELEASE")
if [[ $is-draft == true ]]; then
    echo "is-draft=true" >> $GITHUB_OUTPUT
else
    echo "is-draft=false" >> $GITHUB_OUTPUT
fi
