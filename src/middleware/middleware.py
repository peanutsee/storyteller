from src.core.models.models import AgentState, StoryTellerResponseFormat
from langchain.agents.middleware import before_agent
from src.core.models.models import InputValidationResponseFormat
from langchain_openai import ChatOpenAI
from src.core.prompts.prompts import intent_classification_prompt
from langchain_core.messages import AIMessage

@before_agent(can_jump_to=["end"])
def check_user_intent(state: AgentState, config: dict = None) -> dict | AIMessage | None:
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    structured_llm = llm.with_structured_output(InputValidationResponseFormat)
    
    messages = [intent_classification_prompt] + state["messages"]
    
    res: InputValidationResponseFormat = structured_llm.invoke(messages)
    
    if not res.is_related:
        return {
            "messages": [AIMessage(content=f"I'm sorry, I can only assist with questions regarding portfolios, exposures, or books of clients. {res.reasoning}")],
            "jump_to": "end"
        }
    
    return None
