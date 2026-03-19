from azure.ai.projects.models import PromptAgentDefinition

from ..config import AzureConfig

ac = AzureConfig()

pjcl = ac.project_client

agent_name = "batman-agent"
batman_agent = pjcl.agents.create_version(
    agent_name=agent_name,
    definition=PromptAgentDefinition(
        model="gpt-4o-mini",
        instructions="You are batman. Speak like him",
        temperature=0.8,
    ),
)

opai_client = pjcl.get_openai_client()
conv = opai_client.conversations.create()

while True:
    user_ip = str(input("You: "))
    if user_ip.lower() in ["quit", "exit"]:
        break
    else:
        response = opai_client.responses.create(
            conversation=conv.id,
            extra_body={
                "agent_reference": {
                    "name": agent_name,
                    "type": "agent_reference",
                }
            },
            input=user_ip,
        )
        print(response.output_text)
