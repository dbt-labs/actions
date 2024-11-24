git config user.name "$USER"
git config user.email "$EMAIL"
git pull
git add .
git commit -m "$MESSAGE"
git push
echo "sha=$(git rev-parse HEAD)" >> $GITHUB_OUTPUT
