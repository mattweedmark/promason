import streamlit as st
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain.agents import create_sql_agent
from langchain_openai import ChatOpenAI # Or GoogleGenerativeAI

# --- 1. CONFIGURATION & UI SETUP ---
st.set_page_config(page_title="Lodge Ritual Assistant", page_icon="🏛️")
st.title("🏛️ Masonic Ritual Assistant")

# System Prompt from previous steps
SYSTEM_PROMPT = """
You are the Lodge Director of Ceremonies Assistant. You help manage ritual proficiency.
- EA = Entered Apprentice, FC = Fellow Craft, MM = Master Mason.
- Use the database to verify who is 'Proficient' before answering.
- If a brother is not listed for a part, suggest brothers who ARE proficient to mentor them.
- Be professional and fraternal.
"""

# --- 2. DATABASE CONNECTION ---
# Replace with your actual Supabase Connection String
# Format: postgresql://postgres:[PASSWORD]@[HOST]:5432/postgres
DB_URI = st.secrets["DB_URI"] 
db = SQLDatabase.from_uri(DB_URI)

# --- 3. INITIALIZE AI AGENT ---
llm = ChatOpenAI(model="gpt-4", temperature=0) # High reasoning for SQL
toolkit = SQLDatabaseToolkit(db=db, llm=llm)
agent_executor = create_sql_agent(
    llm=llm,
    toolkit=toolkit,
    verbose=True,
    handle_parsing_errors=True
)

# --- 4. CHAT INTERFACE ---
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "How can I help with the Trestleboard today, Brother?"}]

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Ex: Who is proficient in the 3rd degree tools?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        # The Agent combines your Prompt + User Question + Database Search
        full_query = f"{SYSTEM_PROMPT}\n\nUser Question: {prompt}"
        response = agent_executor.run(full_query)
        st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})