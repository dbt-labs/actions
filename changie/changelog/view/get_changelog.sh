path=".changes/$BASE_VERSION"
if [[ $IS_PRE_RELEASE -eq 1 ]]; then
    path+="-$PRE_RELEASE"
fi
path+=".md"
echo "path=$path" >> $GITHUB_OUTPUT

exists=false
if test -f $path; then
    exists=true
fi
echo "exists=exists">> $GITHUB_OUTPUT
