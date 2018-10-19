import os
from trello import TrelloClient
from dotenv import load_dotenv
from jira import JIRA
from pprint import pprint

load_dotenv()
print("Script to migrate Trello tickets to Jira")
print("----------------------------------------")

print("Creating JIRA client..")
jira = JIRA(os.getenv("JIRA_SERVER"), basic_auth=(os.getenv("JIRA_USERNAME"), os.getenv("JIRA_PASSWORD")))

print("Creating Trello client..")
trello = TrelloClient(
    api_key=os.getenv("TRELLO_API_KEY"),
    api_secret=os.getenv("TRELLO_API_TOKEN")
)

print("Fetching Trello boards...")
all_boards = trello.list_boards()
for i, board in enumerate(all_boards):
    print(str(i) + ". " + board.name)
num = int(input("Select the board you'd like to migrate:"))

if len(all_boards) <= num or num < 0:
    print("Invalid board number. Try again.")
    exit(0)
trello_board = all_boards[num]
print("Using " + trello_board.name)

trello_boards = trello_board.all_lists()
for i, tlist in enumerate(trello_boards):
    print(str(i) + ". " + tlist.name)
trello_done_list = trello_boards[int(input("Which board is the completed board: "))]
print("Cool, we'll be using  '" + trello_done_list.name + "'.")

print("Fetching Jira projects...")
jira_projects = jira.projects()
for i, project in enumerate(jira_projects):
    print(str(i) + ". " + project.name)

jira_project = jira_projects[int(input("Select which project you want to migrate to:"))]
print("Using Jira board: " + jira_project.key)

print("Starting migration..")
trello_cards = trello_board.all_cards()

completed_jira_transition = None

for card in trello_cards:
    issue = {
        "project": {"key": jira_project.key},
        "summary": card.name,
        "description": card.description,
        "issuetype": {"name": "Task"}
    }
    issue = jira.create_issue(issue)
    if completed_jira_transition is None:
        transitions = jira.transitions(issue)
        for i, transition in transitions:
            print(str(i) + ". " + transition.name)
        completed_jira_transition = transitions[int(input("Please select the 'done' board in Jira: "))]

    # if card.list_id == trello_done_list.id:
    jira.transition_issue(issue, completed_jira_transition)

    exit()

    pprint(vars(issue))
