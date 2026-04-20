from dataclasses import dataclass
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langgraph.graph.state import CompiledStateGraph
from src.core.prompts.prompts import storyteller_prompt
from src.core.models.models import StoryTellerResponseFormat
from src.core.tools.db_tool import tools
from langchain.agents.middleware import SummarizationMiddleware
from src.core.models.models import DBContext
from src.middleware.middleware import check_user_intent

class StoryTeller:
    def __init__(self):
        pass 

    def storyteller_agent(self) -> CompiledStateGraph:
        """Create storyteller agent."""
        model = ChatOpenAI(model="gpt-4o-mini")

        return create_agent(
            model=model,
            tools=tools,
            system_prompt=storyteller_prompt,
            response_format=StoryTellerResponseFormat,
            context_schema=DBContext,
            middleware=[
                SummarizationMiddleware(
                    model="gpt-4o-mini",
                    trigger=("tokens", 5000),
                    keep=("messages", 20)
                ),
                check_user_intent
            ]
        )
        
