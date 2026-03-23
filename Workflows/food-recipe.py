import os

from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential

from .config import AzureConfig

ac = AzureConfig()

pjcl = ac.project_client
WORKFLOW_NAME = "Food-Recipe-Generator"
user_query = "give me a recipe with eggs"

with pjcl:
    openai_client = pjcl.get_openai_client()

    # Create a conversation (stateful thread)
    conversation = openai_client.conversations.create()
    print(f"Created conversation (id: {conversation.id})")

    # Stream the response using a context manager (no enum needed)
    with openai_client.responses.stream(
        model="gpt-4o-mini",
        conversation=conversation.id,
        extra_body={
            "agent_reference": {
                "name": WORKFLOW_NAME,
                "type": "agent_reference",
            },
        },
        input=user_query,
        metadata={"x-ms-debug-mode-enabled": "1"},
    ) as stream:
        for event in stream:
            # Text streaming (token by token)
            if event.type == "response.output_text.delta":
                print(event.delta, end="", flush=True)

            # Full text block done
            elif event.type == "response.output_text.done":
                print()  # newline after streamed text

            # New output item added (workflow_action, message, etc.)
            elif event.type == "response.output_item.added":
                item = getattr(event, "item", None)
                if item and getattr(item, "type", None) == "workflow_action":
                    print(f"\n*** Actor '{item.action_id}' started ***")

            # Output item completed
            elif event.type == "response.output_item.done":
                item = getattr(event, "item", None)
                if item and getattr(item, "type", None) == "workflow_action":
                    print(
                        f"Workflow item '{item.action_id}' is '{item.status}' "
                        f"(previous: '{item.previous_action_id}')"
                    )

            # Stream finished
            elif event.type == "response.done":
                print("\n[Stream complete]")

            # Catch-all for unknown events
            else:
                print(f"[Event] {event.type}")

    # Clean up
    openai_client.conversations.delete(conversation_id=conversation.id)
    print("Conversation deleted")
