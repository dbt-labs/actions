// idk what this does
package main

// imports
import (
	"fmt"
	"log"
	"sync"

	gh "github.com/cli/go-gh"
	"github.com/cli/go-gh/pkg/api"
	"github.com/shurcooL/graphql"

	"golang.org/x/exp/slices"
)

// constants
const ORG = "dbt-labs" // GitHub organization for dbt Labs
const TEAM = "core"    // GitHub team for Core
const PROJECT_NUM = 22 // Core triage project
const NUM_ITEMS = 100  // 100 is the maxed allowed by GitHub GraphQL

// constants but vars
var EXCLUDE_REPOS = []string{"core-team", "schemas.getdbt.com"}  // may cause errors
var EXTRA_REPOS = []string{"dbt-starter-project", "jaffle_shop"} // additional monitoring
var ISSUE_LABELS = []string{                                     // add issues with any one of these labels
	"triage",
	"bug",
	"good_first_issue",
	"awaiting_response",
	"more_information_needed",
	"Refinement",
	"support_rotation",
	"help_wanted",
	"spike",
	"python_models",
	"Team:Language",
	"Team:Execution",
	"Team:Adapters",
}
var PR_LABELS = []string{"ready_for_review"} // add prs with any one of these labels

// types -- must be a subset of the corresponding GitHub GraphQL object
type Issue struct {
	Title  string
	Number int
	Id     string
	Url    string
}
type PR struct {
	Title  string
	Number int
	State  string
	Id     string
	Url    string
}

// main function
func main() {

	// ensure threads finish with a WaitGroup
	wg := new(sync.WaitGroup)

	// keep track of items that are already added to avoid processing more than once
	processedIssues := map[string]Issue{}
	processedPRs := map[string]PR{}

	// create GitHub REST client
	rest_client, err := gh.RESTClient(nil)
	if err != nil {
		log.Fatal(err)
	}

	// create GitHub GraphQL client
	gql_client, err := gh.GQLClient(nil)
	if err != nil {
		log.Fatal(err)
	}

	// get project id
	project_id := getProjectId(gql_client)
	log.Println("project_id:", project_id)

	// get list of Core GitHub repos
	repos := getInternalRepos(rest_client)

	// for each repo
	for _, repo := range repos {
		log.Println("repo:", repo)

		// wait for this goroutine to finish, please
		// get prs
		prs := getPRs(gql_client, repo)

		// for each pr
		for _, pr := range prs {
			if _, in := processedPRs[pr.Id]; !in {
				// don't process this PR again
				processedPRs[pr.Id] = pr

				// wait for this goroutine to finish, please
				wg.Add(1)
				go func(pr PR) {
					defer wg.Done()
					defer log.Println("\tprocessed pr:", pr.Number, pr.Title)
					log.Println("\tprocessing pr:", pr.Number, pr.Title)
					addItemToProject(gql_client, project_id, pr.Id)
				}(pr)

			}
		}

		// for each issue label
		for _, label := range ISSUE_LABELS {
			log.Println("\tlabel:", label)

			// get issues
			issues := getIssues(gql_client, repo, label)

			// for each issue
			for _, issue := range issues {
				if _, in := processedIssues[issue.Id]; !in {
					// don't process this issue again
					processedIssues[issue.Id] = issue

					// wait for this goroutine to finish, please
					wg.Add(1)
					go func(issue Issue) {
						defer wg.Done()
						defer log.Println("\tprocessed issue:", issue.Number, issue.Title)
						log.Println("\tprocessing issue:", issue.Number, issue.Title)
						addItemToProject(gql_client, project_id, issue.Id)
					}(issue)
				}
			}
		}
	}

	// wait for all threads to finish
	wg.Wait()
}

// other functions
func addItemToProject(c api.GQLClient, project_id, item string) {

	// struct representing the GraphQL mutation
	var mutation struct {
		AddProjectV2ItemById struct {
			Item struct {
				Id string
			}
		} `graphql:"addProjectV2ItemById(input: {projectId: $project_id contentId: $item})"`
	}

	// setup mutation variables
	variables := map[string]interface{}{
		"project_id": graphql.ID(project_id),
		"item":       graphql.ID(item),
	}

	// execute mutation, adding the item to the project
	err := c.Mutate("AddItemToProject", &mutation, variables)
	if err != nil {
		log.Fatal(err)
	}
}

func getProjectId(c api.GQLClient) (project_id string) {

	// struct representing the GraphQL query
	var query struct {
		Organization struct {
			ProjectV2 struct {
				Id string
			} `graphql:"projectV2(number: $project_number)"`
		} `graphql:"organization(login: $owner)"`
	}

	// setup query variables
	variables := map[string]interface{}{
		"owner":          graphql.String(ORG),
		"project_number": graphql.Int(PROJECT_NUM),
	}

	// execute query
	err := c.Query("ProjectId", &query, variables)
	if err != nil {
		log.Fatal(err)
	}

	// extract the project id
	project_id = query.Organization.ProjectV2.Id

	return
}

func getIssues(c api.GQLClient, repo, label string) (issues []Issue) {

	// struct representing the GraphQL query
	var query struct {
		Repository struct {
			Issues struct {
				Nodes []Issue
			} `graphql:"issues(last:$num_items states:OPEN filterBy: {labels: [$label]})"`
		} `graphql:"repository(owner: $owner, name: $repo)"`
	}

	// setup query variables
	variables := map[string]interface{}{
		"num_items": graphql.Int(NUM_ITEMS),
		"owner":     graphql.String(ORG),
		"repo":      graphql.String(repo),
		"label":     graphql.String(label),
	}

	// execute query
	err := c.Query("Issues", &query, variables)
	if err != nil {
		log.Fatal(err)
	}

	// extract the issues
	issues = query.Repository.Issues.Nodes

	return
}

func getPRs(c api.GQLClient, repo string) (prs []PR) {

	// struct representing the GraphQL query
	var query struct {
		Repository struct {
			PRs struct {
				Nodes []PR
			} `graphql:"pullRequests(last:$num_items states:OPEN)"`
		} `graphql:"repository(owner: $owner, name: $repo)"`
	}

	// setup query variables
	variables := map[string]interface{}{
		"num_items": graphql.Int(NUM_ITEMS),
		"owner":     graphql.String(ORG),
		"repo":      graphql.String(repo),
	}

	// execute query
	err := c.Query("PRs", &query, variables)
	if err != nil {
		log.Fatal(err)
	}

	// extract the PRs
	prs = query.Repository.PRs.Nodes

	return
}

func getInternalRepos(c api.RESTClient) (repos []string) {

	// construct REST endpoint
	endpoint := fmt.Sprintf("orgs/%s/teams/%s/repos", ORG, TEAM)

	// get list of repos from the endpoint
	response := new([]struct{ Name string })
	err := c.Get(endpoint, &response)
	if err != nil {
		log.Fatal(err)
	}

	// filter out excluded repos
	for _, repo := range *response {
		if !slices.Contains(EXCLUDE_REPOS, repo.Name) {
			repos = append(repos, repo.Name)
		}
	}

	// add extra repos
	for _, repo := range EXTRA_REPOS {
		if !slices.Contains(repos, repo) && !slices.Contains(EXCLUDE_REPOS, repo) {
			repos = append(repos, repo)
		}
	}

	return
}

func getInternalUsers(c api.RESTClient) (users []string) {

	// construct REST endpoint
	endpoint := fmt.Sprintf("orgs/%s/teams/%s/members", ORG, TEAM)

	// get list of users from the endpoint
	response := new([]struct{ Login string })
	err := c.Get(endpoint, &response)
	if err != nil {
		log.Fatal(err)
	}

	// simplify
	for _, user := range *response {
		users = append(users, user.Login)
	}

	return
}
