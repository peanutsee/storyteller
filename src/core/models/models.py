from pydantic import BaseModel, Field


class StoryTellerResponseFormat(BaseModel):
    response: str = Field(
        description="This represents the storyteller agent output in text."
    )
