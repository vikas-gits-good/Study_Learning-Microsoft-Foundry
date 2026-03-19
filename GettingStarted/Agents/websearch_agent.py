from azure.ai.projects.models import PromptAgentDefinition, WebSearchTool

from ..config import AzureConfig

az = AzureConfig()
pjcl = az.project_client
agent_name = "websearch-agent"
wbsr_agent = pjcl.agents.create_version(
    agent_name=agent_name,
    definition=PromptAgentDefinition(
        model="gpt-4o-mini",
        instructions="You are a helpful assistant with access to internet via a tool.",
        temperature=0.8,
        tools=[
            WebSearchTool(),
        ],
    ),
)


opai_client = pjcl.get_openai_client()
user_ip = "When is fifa in 2026?"

rspn = opai_client.responses.create(
    extra_body={
        "agent_reference": {
            "name": agent_name,
            "type": "agent_reference",
        }
    },
    input=user_ip,
)

print(rspn.output_text)
