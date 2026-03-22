from azure.ai.projects.models import PromptAgentDefinition
from azure.ai.textanalytics import TextAnalyticsClient
from azure.core.credentials import AzureKeyCredential

from .config import AzureConfig

ac = AzureConfig()

model_name = "gpt-4o-mini"
azure_lang_endpoint = ac.secrets.azure_lang_endpoint
azure_lang_api_key = ac.secrets.azure_lang_api_key

pjcl = ac.project_client
opcl = pjcl.get_openai_client()
tacl = TextAnalyticsClient(
    endpoint=azure_lang_endpoint,
    credential=AzureKeyCredential(key=azure_lang_api_key),
)


def redact(input: str):
    response = tacl.recognize_pii_entities(
        documents=[input],
        language="en",
    )
    result = [doc for doc in response if not doc.is_error]
    for doc in result:
        redacted_text = doc.redacted_text
        print(redacted_text)
        return redacted_text


agent_name = "travel-ass-agent"

agent = pjcl.agents.create_version(
    agent_name=agent_name,
    definition=PromptAgentDefinition(
        model=model_name,
        instructions="You are a travel assistant. Help users plan their trips.",
    ),
)

convo = opcl.conversations.create()
user_query = ""


while True:
    user_input = input("You: ")
    if user_input.lower() in ["quit", "exit"]:
        break
    else:
        rspn = opcl.responses.create(
            conversation=convo.id,
            extra_body={
                "agent_reference": {
                    "name": agent_name,
                    "type": "agent_reference",
                },
            },
            input=redact(user_input),
        )
        print(rspn.output_text)
