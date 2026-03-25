from azure.ai.projects.models import (
    BrowserAutomationPreviewTool,
    BrowserAutomationToolConnectionParameters,
    BrowserAutomationToolParameters,
    PromptAgentDefinition,
)

from ..config import AzureConfig

ac = AzureConfig()

pjcl = ac.project_client
opcl = pjcl.get_openai_client()
convo = opcl.conversations.create()

for conn in pjcl.connections.list():
    if conn.name == "playwright_workspace_tool":
        connection_id = conn.id


tool = BrowserAutomationPreviewTool(
    browser_automation_preview=BrowserAutomationToolParameters(
        connection=BrowserAutomationToolConnectionParameters(
            project_connection_id=connection_id,
        )
    )
)

agent_name = "TestPW"

agent = pjcl.agents.create_version(
    agent_name=agent_name,
    definition=PromptAgentDefinition(
        model="gpt-4o-mini",
        tools=[tool],
        instructions="You are a website testing system. Use the available tool and run the scripts. Generate the code in javascript and send them to the tool",
    ),
)

user_query = f"""go to 'https://aicamp.ai/login' and then run the below javascript
and return the response. Send this javascript as it is to the tool
{ac.pw_dom.js}
"""
# user_query = f"""{ac.pw_dom.js}"""
#
# user_query = """go to 'https://aicamp.ai/login' and then return all of the \
# interactable items in the html. Like a DOM"""

# user_query = """Your goal is to report the percent of Microsoft year-to-date stock price change.
# To do that, go to the website finance.yahoo.com.
# At the top of the page, you will find a search bar.
# Enter the value 'MSFT', to get information about the Microsoft stock price.
# At the top of the resulting page you will see a default chart of Microsoft stock price.
# Click on 'YTD' at the top of that chart, and report the percent value that shows up just below it.
# """
rspn = opcl.responses.create(
    conversation=convo.id,
    input=user_query,
    extra_body={
        "agent_reference": {
            "name": agent_name,
            "type": "agent_reference",
        },
    },
)
print(rspn.output_text)
