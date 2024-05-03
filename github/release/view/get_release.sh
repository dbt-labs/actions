output=$((gh release view $TAG --json isDraft,targetCommitish --repo $REPO) 2>&1) || true

if [[ "$output" == "release not found" ]]; then
    echo "exists=false" >> $GITHUB_OUTPUT
else
    echo "exists=true" >> $GITHUB_OUTPUT
    echo "RELEASE=$output" >> $GITHUB_ENV
fi
