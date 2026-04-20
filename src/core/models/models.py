from src.core.database.db_client import DBClient
from pydantic import BaseModel, Field
from dataclasses import dataclass


class StoryTellerResponseFormat(BaseModel):
    response: str = Field(
        description="This represents the storyteller agent output in text."
    )


class NL2SQLResponseFormat(BaseModel):
    query: str = Field(description="This represents the NL2SQL output.")


@dataclass
class DBContext:
    db_client: DBClient