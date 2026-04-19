from langchain.tools import tool, ToolRuntime


@tool
def retrieve_portfolio_information_tool(username: str, runtime: ToolRuntime) -> str:
    """Retrieve Portfolio Information Tool.

    Use this tool to query the database and retrieve general portfolio information
    given the user name.
    """
    db_client = runtime.config["configurable"].get("db_client")
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
    db_client = runtime.config["configurable"].get("db_client")
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


tools = [retrieve_portfolio_exposures_tool, retrieve_portfolio_information_tool]
