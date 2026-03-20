from azure.ai.projects.models import (
    AISearchIndexResource,
    AzureAISearchQueryType,
    AzureAISearchTool,
    AzureAISearchToolResource,
    PromptAgentDefinition,
)

from .config import AzureConfig

ac = AzureConfig()

pjcl = ac.project_client


opcl = pjcl.get_openai_client()

ai_srch_conn_id = ""

for conn in pjcl.connections.list():
    if conn.name == ac.secrets.ai_srch_conn_name:
        ai_srch_conn_id = conn.id
        break

mmr_tool = AzureAISearchTool(
    azure_ai_search=AzureAISearchToolResource(
        indexes=[
            AISearchIndexResource(
                project_connection_id=ai_srch_conn_id,
                index_name=ac.secrets.ai_srch_indx_name,
                query_type=AzureAISearchQueryType.VECTOR_SEMANTIC_HYBRID,
                top_k=3,
            )
        ]
    )
)

agent_name = "MMR-RAG-Agent"
agent = pjcl.agents.create_version(
    agent_name=agent_name,
    definition=PromptAgentDefinition(
        model="gpt-4o-mini",
        instructions="You are an agent that tells people about travelling places.",
        tools=[mmr_tool],
    ),
)


convo = opcl.conversations.create()

# user_query = "What the hotels offered in Las Vegas. Provide sources!"
user_query = "Tell me about the board members in margies travel"

rspn = opcl.responses.create(
    tool_choice="required",
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
