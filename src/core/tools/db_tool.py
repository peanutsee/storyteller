from langchain.tools import tool, ToolRuntime
from langchain_openai import ChatOpenAI
from src.core.models.models import NL2SQLResponseFormat
from langchain_core.messages import HumanMessage
from src.core.prompts.prompts import nl_to_sql_prompt


@tool
def retrieve_portfolio_information_tool(username: str, runtime: ToolRuntime) -> str:
    """Retrieve Portfolio Information Tool.

    Use this tool to query the database and retrieve general portfolio information
    given the user name.
    """
    db_client = runtime.context.db_client
    cursor = db_client.connection.cursor()

    cursor.execute("SELECT * FROM portfolio WHERE owner = ?", (username,))
    row = cursor.fetchone()

    if row:
        return f"Portfolio info for {username}:\n- ID: {row['id']}\n- Total Amount: ${row['total_amount']:.2f}\n- Last Updated: {row['last_updated']}"
    return f"No portfolio found for user: {username}"


@tool
def retrieve_portfolio_exposures_tool(username: str, runtime: ToolRuntime) -> str:
    """Retrieve Portfolio Exposure Tool.

    Use this tool to query the database and retrieve all related exposure
    information about the portfolio given the user name.
    """
    db_client = runtime.context.db_client
    cursor = db_client.connection.cursor()

    query = """
        SELECT e.ticker_symbol, e.quantity, e.avg_price
        FROM exposure e
        JOIN portfolio p ON p.id = e.portfolio_id
        WHERE p.owner = ?
    """
    cursor.execute(query, (username,))
    rows = cursor.fetchall()

    if not rows:
        return f"No exposures found for user: {username}"

    result = [f"Exposures for {username}:"]
    for r in rows:
        result.append(
            f"- {r['ticker_symbol']}: {r['quantity']:.2f} shares @ ${r['avg_price']:.2f}"
        )

    return "\n".join(result)


@tool
def nl_to_sql_tool(query: str, runtime: ToolRuntime) -> str:
    """Convert natural language to SQL.
    
    CRITICAL INSTRUCTION: ALWAYS use this tool for ANY aggregations, counting queries (e.g., 'How many clients/portfolios do I have?'), or broad database questions. 
    Pass the user's EXACT natural language question into the 'query' parameter. DO NOT use the retrieve_portfolio_information_tool unless the user gave a specific name.
    """
    db_client = runtime.config["configurable"].get("db_client")
    cursor = db_client.connection.cursor()

    model = ChatOpenAI(model="gpt-4o-mini")
    model_with_structured_outputs = model.with_structured_output(NL2SQLResponseFormat)

    messages = [
        nl_to_sql_prompt,
        HumanMessage(
            content=f"Convert this user query into a valid SQL syntax: {query}"
        ),
    ]

    response = model_with_structured_outputs.invoke(messages)

    if not response or not response.query:
        return "Could not generate a valid query."

    raw_query = response.query.strip()
    if raw_query == "NOT_POSSIBLE":
        return "The requested information cannot be found in the portfolio or exposure databases."

    if raw_query.startswith("```sql"):
        raw_query = raw_query[6:]
    if raw_query.startswith("```"):
        raw_query = raw_query[3:]
    if raw_query.endswith("```"):
        raw_query = raw_query[:-3]
        
    clean_query = raw_query.strip()

    # 3. Execute the clean query
    try:
        cursor.execute(clean_query)
        rows = cursor.fetchall()

        if not rows:
            return f"Query executed successfully, but returned no data. (Executed query: {clean_query})"

        result = []
        for r in rows:
            result.append("- " + str(dict(r)))

        return "\n".join(result)
        
    except Exception as e:
        # Returning the error helps you debug, and if you use an advanced agent, 
        # it can use this error to try and fix the query!
        return f"Database error executing SQL: {str(e)}\nAttempted Query: {clean_query}"


tools = [
    retrieve_portfolio_exposures_tool,
    retrieve_portfolio_information_tool,
    nl_to_sql_tool,
]
