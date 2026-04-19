from dotenv import load_dotenv
from rich import print as rprint

from src.core.database.db_client import DBClient
from src.services.agent import StoryTeller
from langchain.messages import AIMessage, HumanMessage

load_dotenv()


def main():
    # 0. Create DBClient
    db_client = DBClient()
    db_client.connect()
    db_client.create_tables()

    # Make the initialization logs stand out a bit
    if not db_client.has_data():
        rprint("[bold yellow]⚠ Database is empty. Seeding mock data...[/bold yellow]")
        db_client.seed_mock_data()
    else:
        rprint(
            "[bold green]✓ Database already contains data. Skipping mock data seeding.[/bold green]"
        )

    # 1. Create Agent
    agent = StoryTeller(db_client=db_client).storyteller_agent()

    # 2. Run Agent
    config = {"configurable": {"db_client": db_client, "thread_id": "user-session-123"}}

    rprint("\n[bold underline]Starting Chat Session[/bold underline]\n")

    for chunk in agent.stream(
        {
            "messages": [
                {"role": "user", "content": "Tell me about Mock Owner 1's portfolio"}
            ]
        },
        stream_mode="values",
        config=config,
    ):
        latest_message = chunk["messages"][-1]

        if latest_message.content:
            if isinstance(latest_message, HumanMessage):
                rprint(f"[bold cyan]User:[/bold cyan] {latest_message.content}")

            elif isinstance(latest_message, AIMessage):
                rprint(f"[bold green]Agent:[/bold green] {latest_message.content}")

        elif latest_message.tool_calls:
            tool_names = [tc["name"] for tc in latest_message.tool_calls]
            rprint(f"[bold magenta]🛠  Calling tools:[/bold magenta] {tool_names}")


if __name__ == "__main__":
    main()
