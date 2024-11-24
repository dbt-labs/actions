if $IS_DRAFT; then
    draft="--draft=true"
else
    draft="--draft=false"
fi
echo "flag=$flag" >> $GITHUB_OUTPUT
