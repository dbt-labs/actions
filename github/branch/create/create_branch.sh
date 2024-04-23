BRANCH="$STUB/$(date +'%Y-%m-%d')/$GITHUB_RUN_ID"
echo "name=$BRANCH" >> $GITHUB_OUTPUT
git checkout -b $BRANCH
git push -u origin $BRANCH
