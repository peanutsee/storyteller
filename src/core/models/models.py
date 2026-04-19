from pydantic import BaseModel, Field


class StoryTellerResponseFormat(BaseModel):
    response: str = Field(
        description="This represents the storyteller agent output in text."
    )


class NL2SQLResponseFormat(BaseModel):
    query: str = Field(description="This represents the NL2SQL output.")
