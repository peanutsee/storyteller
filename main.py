import streamlit as st
import pandas as pd
import json
from dotenv import load_dotenv
from langchain_core.messages import AIMessage, HumanMessage

from src.core.database.db_client import DBClient
from src.services.agent import StoryTeller

load_dotenv()

# Initialize DB and Agent in session_state
if "db_client" not in st.session_state:
    st.session_state.db_client = DBClient()
    st.session_state.db_client.connect()
    st.session_state.db_client.create_tables()

    # Seed data if empty
    if not st.session_state.db_client.has_data():
        st.session_state.db_client.seed_mock_data()

if "agent" not in st.session_state:
    st.session_state.agent = StoryTeller(db_client=st.session_state.db_client).storyteller_agent()

if "messages" not in st.session_state:
    st.session_state.messages = []

# UI Setup
st.set_page_config(page_title="Storyteller AI", page_icon="💬", layout="wide")
st.title("Welcome to Storyteller AI")

tab1, tab2 = st.tabs(["💬 Chat", "🗄️ Database"])

with tab2:
    st.header("Database Explorer")
    cursor = st.session_state.db_client.connection.cursor()
    
    st.subheader("Portfolio Data")
    cursor.execute("SELECT * FROM portfolio")
    portfolio_data = cursor.fetchall()
    if portfolio_data:
        df_portfolio = pd.DataFrame([dict(row) for row in portfolio_data])
        st.dataframe(df_portfolio, hide_index=True, use_container_width=True)
    else:
        st.info("No data in Portfolio table.")

    st.subheader("Exposure Data")
    cursor.execute("SELECT * FROM exposure")
    exposure_data = cursor.fetchall()
    if exposure_data:
        df_exposure = pd.DataFrame([dict(row) for row in exposure_data])
        st.dataframe(df_exposure, hide_index=True, use_container_width=True)
    else:
        st.info("No data in Exposure table.")

with tab1:
    # Render existing messages
    for msg in st.session_state.messages:
        role = "user" if isinstance(msg, HumanMessage) else "assistant"
        with st.chat_message(role):
            st.markdown(msg.content)

    # Chat input
    if prompt := st.chat_input("Ask about portfolios (e.g. 'Tell me about Mock Owner 1's portfolio')"):
        # Append user message
        st.session_state.messages.append(HumanMessage(content=prompt))
        
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            status = st.status("Agent thinking...", expanded=True)
            
            config = {"configurable": {"db_client": st.session_state.db_client, "thread_id": "user-session-123"}}
            final_content = ""
            
            # Stream the graph updates
            for chunk in st.session_state.agent.stream(
                {"messages": st.session_state.messages},
                stream_mode="values",
                config=config,
            ):
                latest_message = chunk["messages"][-1]
                
                # Check if it's a tool call
                if hasattr(latest_message, "tool_calls") and latest_message.tool_calls:
                    tool_names = ", ".join([tc["name"] for tc in latest_message.tool_calls])
                    status.write(f"🛠️ Calling tools: {tool_names}")
                
                # Check if the AI actually replied with text
                if isinstance(latest_message, AIMessage) and latest_message.content:
                    raw_content = latest_message.content
                    if isinstance(raw_content, dict) and "response" in raw_content:
                        final_content = raw_content["response"]
                    elif isinstance(raw_content, str):
                        try:
                            parsed_content = json.loads(raw_content)
                            if isinstance(parsed_content, dict) and "response" in parsed_content:
                                final_content = parsed_content["response"]
                            else:
                                final_content = raw_content
                        except json.JSONDecodeError:
                            final_content = raw_content
                        except TypeError:
                            final_content = str(raw_content)
                    else:
                        final_content = str(raw_content)
            
            status.update(label="Finished thinking!", state="complete", expanded=False)
            
            st.markdown(final_content)
            st.session_state.messages.append(AIMessage(content=final_content))
