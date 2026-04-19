# Storyteller - Personal Portfolio AI Assistant

I am bored so I built this on Sunday.

<video src="assets/demo.mov" controls="controls" width="100%"></video>

Anyway, Storyteller is an AI-powered personal portfolio assistant that leverages LangGraph and LangChain to dynamically query a local SQLite database. It features a modern, vibe-coded Streamlit Dashboard designed to visually explore financial data schemas and converse with an intelligent agent regarding simulated portfolio exposures.

## Features

- **💬 Agentic Chat Interface**: Interact with a `gpt-4o-mini` LangGraph agent that thinks step-by-step and leverages integrated tools to fetch matching portfolio or stock exposure information.
- **🗄️ Database Preview**: Uses `pandas` to query SQLite `PRAGMA` metadata, effortlessly displaying the underlying schema for both the `portfolio` and `exposure` tables directly in the Streamlit UI.
- **🤖 Auto-Seeded Database**: The system will automatically instantiate and seed `storyteller.db` with 10 fictional portfolios holding randomized shares in SP500 tickers.

## Setup & Installation

This project uses `uv` for lightning-fast package management.

1. **Clone the repository:**

   ```bash
   git clone <repository_url>
   cd storyteller
   ```

2. **Setup your environment variables:**
   Ensure you have a valid OpenAI API key to power the agent. Create a `.env` file in the root of the project:

   ```bash
   # Add your key to .env:
   OPENAI_API_KEY="sk-..."
   ```

3. **Install dependencies:**
   Using `uv`, you can easily sync up the environment configurations from the lockfile:
   ```bash
   uv sync
   ```

## Running the Application

To fire up the dashboard, launch Streamlit via `uv`:

```bash
uv run streamlit run main.py
```

This will run the web app locally. It'll also automatically construct and populate the mock SQLite database if one is not detected!
