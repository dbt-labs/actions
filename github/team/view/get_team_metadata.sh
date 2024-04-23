
OUTPUT_FILE=output_$GITHUB_RUN_ID.json

gh api $ENDPOINT -H "$HEADER" > $OUTPUT_FILE

team_list=$(jq -r '.[].login' $OUTPUT_FILE)
team_list_single=$(echo $team_list | tr '\n' ' ')
echo "members=$team_list_single" >> $GITHUB_OUTPUT

rm $OUTPUT_FILE
