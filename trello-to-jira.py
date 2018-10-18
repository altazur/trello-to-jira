import os
from trello import TrelloClient
from dotenv import load_dotenv
from jira import JIRA
from pprint import pprint
import re

load_dotenv()
print("Script to migrate Trello tickets to Jira")
print("----------------------------------------")

# TODO: should get this from env?
jira = JIRA(os.getenv("JIRA_SERVER"), basic_auth=(os.getenv("JIRA_USERNAME"), os.getenv("JIRA_PASSWORD")))
tClient = TrelloClient(
    api_key=os.getenv("TRELLO_API_KEY"),
    api_secret=os.getenv("TRELLO_OAUTH_TOKEN")
)

# print("Fetching Trello boards...")
# all_boards = tClient.list_boards()
# for i, board in enumerate(all_boards):
#     print(str(i) + ". " + board.name)
# num = int(input("Select the board you'd like to migrate:"))
#
# if len(all_boards) <= num or num < 0:
#     print("Invalid board number. Try again.")
#     exit(0)
# trello_board = all_boards[num]
# print("Using " + trello_board.name)

print("Fetching Jira projects...")

jira_projects = jira.projects()
for i, project in enumerate(jira_projects):
    print(str(i) + ". " + project.name)

jira_project = int(input("Select which project you want to migrate to:"))

if len(jira_projects) <= jira_project or jira_project < 0:
    print("Invalid board number. Try again.")
    exit(0)

jira_project = jira_projects[jira_project]

print("Using Jira board: " + jira_project.key)

issue = {
    "project": {
        "key": jira_project.key
    },
    "summary": "Test Summary",
    "description": "Lorum ipsum",
    "issuetype": {
        "name": "Task"
    }
}
issue = jira.create_issue(issue)
pprint(vars(issue))
