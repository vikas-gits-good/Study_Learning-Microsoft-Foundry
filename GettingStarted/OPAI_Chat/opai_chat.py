import os

from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
from dotenv import load_dotenv

load_dotenv()


AZURE_KEY_VAULT_URI = os.getenv("AZURE_KEY_VAULT_URI")

kvc = SecretClient(
    vault_url=AZURE_KEY_VAULT_URI,
    credential=DefaultAzureCredential(),
)

AZURE_SERVICE_ENDPOINT = kvc.get_secret("AZURE-SERVICE-ENDPOINT-EXPT-TEST").value
AZURE_API_KEY = kvc.get_secret("AZURE-API-KEY-EXPT-TEST").value
AZURE_OPAI_MODEL = "gpt-4o-mini"  # "gpt-5.3-chat" #


ai_proj_clnt = AIProjectClient(
    endpoint=AZURE_SERVICE_ENDPOINT,
    credential=DefaultAzureCredential(),
)

opai_client = ai_proj_clnt.get_openai_client()

rspn = opai_client.responses.create(
    model=AZURE_OPAI_MODEL,
    instructions="You are a helpful ai assistant",
    input="Tell me about Microsoft Foundry",
)

print(rspn.output_text)
