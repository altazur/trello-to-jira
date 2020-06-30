import os
import json
import urllib.request
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

trello_columns = trello_board.all_lists()
"""
for i, tlist in enumerate(trello_boards):
    print(str(i) + ". " + tlist.name)
trello_done_list = trello_boards[int(input("Which column is the completed column: "))]
print("Cool, we'll be using  '" + trello_done_list.name + "'.")
"""

print("Fetching Jira projects...")
jira_projects = jira.projects()
for i, project in enumerate(jira_projects):
    print(str(i) + ". " + project.name)

jira_project = jira_projects[int(input("Select which project you want to migrate to:"))]
print("Using Jira board: " + jira_project.key)

print("Starting migration..")
trello_cards = trello_board.all_cards()

# Sort cards by creation date, to match with card numbers, (card id is some hash)
trello_cards.sort(key=lambda x: x.card_created_date)

"""
completed_jira_transition = None
"""

for card in trello_cards:
    issue = {
        "project": {"key": jira_project.key},
        "summary": card.name,
        "description": card.desc,
        "issuetype": {"name": "Task"},
    }

    issue = jira.create_issue(issue)
    print(issue.key + " migrated.")

    # Search current card column name(status)
    card_status_name = None
    for column in trello_columns:
        if card.list_id == column.id:
            card_status_name = column.name
            break

    # Search jira status(transition) equivalent by name
    jira_transitions = jira.transitions(issue)
    jira_status = None
    for transition in jira_transitions:
        if transition['name'].lstrip("Move to ") == card_status_name: # lstrip("Move to") should be in case of automatic jira workflow creation after first import from jira to trello
            jira_status = transition

    if card_status_name is None: # It's not gonna happen btw
        print(f"Card column name not found for card {card.id}")

    if jira_status is None:
        jira_status = jira_transitions[0]
        print(f"Jira status equivalent not found. Issue {issue.id} will be moved to first jira project status {jira_status['name']}")

    jira.transition_issue(issue, jira_status["id"])
    print(issue.key + " moved to " + jira_status["name"])
    """
    if completed_jira_transition is None:
        transitions = jira.transitions(issue)
        for i, transition in enumerate(transitions):
            print(str(i) + ". " + transition["name"])
        completed_jira_transition = transitions[int(input("Please select the 'done' board in Jira: "))]
    """
    """
    if card.list_id == trello_done_list.id:
        jira.transition_issue(issue, completed_jira_transition["id"])
        print(issue.key + " moved to " + completed_jira_transition["name"])
    """

    # comment fields: text
    trello_comments = card.fetch_comments(force=True)
    if len(trello_comments) != 0:
        print("Found comments. Starting..")
        for comment in trello_comments:
            try:
                username = comment['memberCreator']['fullName']
            except KeyError:
                username = "deleted user"
            print('Creating comment by ' + username + ' on ' + issue.key)
            jira.add_comment(issue, f"{username}:\n{comment['data']['text']}")

    # attachment fields: url, name
    trello_attachments, attachments = card.fetch_attachments(force=True), []
    if len(trello_attachments) != 0:
        print("Found attachments. Downloading...")
        for attachment in trello_attachments:
            if os.path.exists('attachments/' + card.id) is False:
                os.mkdir('attachments/' + card.id)
            try:
                urllib.request.urlretrieve(attachment['url'], 'attachments/' + card.id + '/' + attachment["name"])
            except Exception:
                print("Failed to download attachment. Skipping")
            try:
                jira.add_attachment(issue, open('attachments/' + card.id + '/' + attachment["name"], 'rb'))
                print("Attached " + attachment["name"] + " to " + issue.key)
            except IOError:
                print("Failed to attach file. Skipping")
