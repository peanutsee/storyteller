from dataclasses import dataclass
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langgraph.graph.state import CompiledStateGraph
from src.core.prompts.prompts import storyteller_prompt
from src.core.models.models import StoryTellerResponseFormat
from src.core.tools.db_tool import tools
from src.core.database.db_client import DBClient


@dataclass
class DBContext:
    db_client: DBClient


class StoryTeller:
    def __init__(self, db_client):
        self.db_client = db_client

    def storyteller_agent(self) -> CompiledStateGraph:
        """Create storyteller agent."""
        model = ChatOpenAI(model="gpt-4o-mini")

        return create_agent(
            model=model,
            tools=tools,
            system_prompt=storyteller_prompt,
            response_format=StoryTellerResponseFormat,
            context_schema=DBContext,
        )
