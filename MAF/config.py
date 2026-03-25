import os

from agent_framework.azure import AzureOpenAIResponsesClient
from azure.ai.projects import AIProjectClient
from azure.identity import AzureCliCredential, DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
from dotenv import load_dotenv


def _get_credential():
    auth_mode = os.getenv("AZURE_AUTH_MODE", "cli").strip().lower()
    if auth_mode == "default":
        return DefaultAzureCredential()
    return AzureCliCredential()


class _get_dom_js:
    def __init__(self):
        base_dir = os.path.dirname(__file__)
        file_path_old = os.path.join(base_dir, "Test/exe.js")
        file_path_new = os.path.join(base_dir, "Test/new_dom_2.js")

        with open(file_path_old, "r", encoding="utf-8") as f:
            self.js_old = f.read()

        with open(file_path_new, "r", encoding="utf-8") as f:
            self.js_new = f.read()


class _secret_manager:
    def __init__(self):
        load_dotenv()
        _kvc = SecretClient(
            vault_url=os.getenv("AZURE_KEY_VAULT_URI", ""),
            credential=_get_credential(),
        )
        self.azure_service_endpoint = _kvc.get_secret(
            "AZURE-SERVICE-ENDPOINT-EXPT-TEST"
        ).value
        self.azure_service_api_key = _kvc.get_secret("AZURE-API-KEY-EXPT-TEST").value
        self.ai_srch_conn_name = _kvc.get_secret("AI-SEARCH-CONNECTION-NAME").value
        self.ai_srch_conn_url = _kvc.get_secret("AI-SEARCH-CONNECTION-URL").value
        self.ai_srch_indx_name = _kvc.get_secret("AI-SEARCH-INDEX-NAME").value
        self.pw_browser_url = _kvc.get_secret("PW-BRW-URL").value
        self.pw_agent_token = _kvc.get_secret("PW-AGT-TOKEN").value


class AzureConfig:
    def __init__(self):
        self.secrets = _secret_manager()
        self.project_client = AIProjectClient(
            endpoint=self.secrets.azure_service_endpoint,
            credential=_get_credential(),
        )
        self.pw_dom = _get_dom_js()


_get_dom_js()
