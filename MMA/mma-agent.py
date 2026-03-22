from azure.ai.documentintelligence.aio import DocumentIntelligenceClient
from azure.ai.documentintelligence.models import AnalyzeDocumentRequest, AnalyzeResult
from azure.ai.projects.models import CodeInterpreterTool, PromptAgentDefinition
from azure.ai.textanalytics import TextAnalyticsClient
from azure.core.credentials import AzureKeyCredential

from .config import AzureConfig

ac = AzureConfig()

azure_lang_endpoint = ac.secrets.azure_lang_endpoint
azure_lang_api_key = ac.secrets.azure_lang_api_key
doc_intel_api_endpoint = ac.secrets.doc_intel_endpoint
doc_intel_api_key = ac.secrets.doc_intel_api_key

model_name = "gpt-4o-mini"

pjcl = ac.project_client
opcl = pjcl.get_openai_client()
tacl = TextAnalyticsClient(
    endpoint=azure_lang_endpoint,
    credential=AzureKeyCredential(key=azure_lang_api_key),
)
dicl = DocumentIntelligenceClient(
    endpoint=doc_intel_api_endpoint,
    credential=AzureKeyCredential(key=doc_intel_api_key),
)


def redact(input: str):
    response = tacl.recognize_pii_entities(
        documents=[input],
        language="en",
    )
    result = [doc for doc in response if not doc.is_error]
    for doc in result:
        return doc.redacted_text


def analyse_invoide(url: str):
    rspn = ""
    poller = dicl.begin_analyze_document(
        model_id="prebuilt-invoice",
        body=AnalyzeDocumentRequest(url_source=url),
    )
    invoices = poller
