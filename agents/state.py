from typing import Annotated, TypedDict
from langchain_core.messages import BaseMessage

class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], "Messages in the conversation"]
    transcript: Annotated[str, "Original transcript"]
    notes: Annotated[str, "Generated notes"]
    feedback: Annotated[str | None, "User feedback"]
    target_language: Annotated[str, "Target language"]
    note_type: Annotated[str, "Type of notes"]
    status: Annotated[str, "Current status of the workflow"] 