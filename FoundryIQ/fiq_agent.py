from azure.ai.projects.models import MCPTool, PromptAgentDefinition

from .config import AzureConfig

ac = AzureConfig()

KB_NAME = ac.secrets.fiq_kb_name
AI_SEARCH_CONN_NAME = ac.secrets.ai_srch_conn_name
AI_SEARCH_CONN_ENDP = ac.secrets.ai_srch_conn_url

mcp_ep = (
    f"{AI_SEARCH_CONN_ENDP}/knowledgebases/{KB_NAME}/mcp?api-version=2025-11-01-preview"
)

pjcl = ac.project_client
opcl = pjcl.get_openai_client()
conn_id = ""
for conn in pjcl.connections.list():
    if conn.name == AI_SEARCH_CONN_NAME:
        conn_id = conn.id
        break

mcp_kb_tool = MCPTool(
    server_label=KB_NAME,
    server_url=mcp_ep,
    require_approval="never",
    allowed_tools=["knowledge_base_retrieve"],
    project_connection_id=AI_SEARCH_CONN_NAME,
)

sys_pmt = """
You are a helpful assistant that must use the knowledge base to answer all the questions from user. You must never answer from your own knowledge under any circumstances.
At the end of your answer provide a list of all the document urls used as grounding sources.

If you cannot find the answer in the provided knowledge base you must respond with - I don't know.
"""

agent_name = "kb-code-agent"

agent = pjcl.agents.create_version(
    agent_name=agent_name,
    definition=PromptAgentDefinition(
        model="gpt-4o-mini",
        instructions=sys_pmt,
        tools=[mcp_kb_tool],
    ),
)

convo = opcl.conversations.create()

user_queries = [
    "Combine the CEIM Impact Flux Score with the Well-Being Pillars Framework to propose a proprietary CarbonOps metric that quantifies how employee well-being influences ESG impact severity. Define the formula, list inputs required from SES metadata, and generate a sample score calculation.",
    "Using the CarbonOps Global Remote Work tiers and the CEIM System Boundary Confidence concept, evaluate how a fully distributed team (RW-3) affects CarbonOps regulatory readiness. Provide a quantified readiness score and justify it using SES validation stages.",
    "List all proprietary CarbonOps scoring elements (from CEIM, SES, and Well-Being documents) and classify them into: (1) metrics, (2) validation factors, (3) behavioral indicators. Explain how these categories interact during an AI-driven ESG assessment",
]

rspn = opcl.responses.create(
    conversation=convo.id,
    extra_body={
        "agent_reference": {
            "name": agent_name,
            "type": "agent_reference",
        },
    },
    input=user_queries[1],
)
print(rspn.output_text)
