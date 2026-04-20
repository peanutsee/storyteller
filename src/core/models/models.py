from langchain_core import messages as lc_messages
from src.core.database.db_client import DBClient
from pydantic import BaseModel, Field
from dataclasses import dataclass
import operator

# --- AGENT STATE ---
class AgentState(BaseModel):
    messages: list[lc_messages.BaseMessage] = Field(default_factory=list, reducer=operator.add)

# --- RESPONSE FORMAT ---
class StoryTellerResponseFormat(BaseModel):
    response: str = Field(
        description="This represents the storyteller agent output in text."
    )

class NL2SQLResponseFormat(BaseModel):
    query: str = Field(description="This represents the NL2SQL output.")

class InputValidationResponseFormat(BaseModel):
    is_related: bool = Field(description="This represents whether the user's question is related to the portfolio/exposures or not.")
    reasoning: str = Field(description="This represents the reasoning behind the is_related flag.")

# --- DATA CLASS ---
@dataclass
class DBContext:
    db_client: DBClient