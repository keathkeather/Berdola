import streamlit as st
from langchain_community.utilities import SQLDatabase
import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import create_sql_query_chain
from langchain_community.tools.sql_database.tool import QuerySQLDataBaseTool
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from operator import itemgetter
import asyncio

st.set_page_config(page_title="Berdola", page_icon="berdola.png")
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;700&display=swap');
    .big-font {
        font-family: Poppins, sans-serif;
        color: #f4f4f4;
        font-size: 36px;
        font-weight: bold;
        text-align: center;
        margin-top: 20px;
        margin-bottom: -20px;
    }
    .other-big {
        font-family: Poppins, sans-serif;
        color: #f4f4f4;
        font-size: 42px;
        font-weight: bold;
        margin-bottom: -10px;
    }
    .stTextInput input {
        background-color: #eeeeee;
            color: #1F1A30;
    }
    .stTextInput input::placeholder {
        color: #1F1A30;
    }
    .stTextInput label {
        color: #787582;
        justify-content: center;
        margin-bottom: 10px;
        font-family: Poppins, sans-serif; 
    }
    .stColumn {
        position: absolute;
        bottom: 0;
        margin-bottom: 20px;  /* Adjust the margin as needed */
    }
    .Result {
        font-family: Poppins;
        color: #BBBBBB;
        background-color: #1F1A30;
        width: 100%;
        padding: 20px;
        justify-content: center;
        margin-top: 20px;
        border-radius: 10px;
            font-size: 14px;
    }
    .img-circle {
        border-radius: 50%;
    }
    .Success {
        color: #3EC181;
        background-color: rgba(6, 129, 61, 0.2);
        border-radius: 5px;
        height: 40px;
        width: 100%;
        padding: 10px;
        align-items: center;
        display: flex;  /* Add this line */
        border: 1px solid #3EC181;
        
    }
    .Error {
        color: #ED5556;
        background-color: rgba(212, 60, 61, 0.3);
        border-radius: 5px;
        width: 100%;
        padding: 10px;
        align-items: center;
        display: flex;  /* Add this line */
        border: 1px solid #ED5556;  
    }
            .Warning {
        color: #F5AC54;
        background-color: rgba(255, 186, 104, 0.3);
        border-radius: 5px;
        width: 100%;
        padding: 10px;
        align-items: center;
        display: flex;  /* Add this line */
        border: 1px solid #F5AC54;
        
    }
    </style>
    """, unsafe_allow_html=True)

# Set Google API key if not already set
if "GOOGLE_API_KEY" not in os.environ:
    os.environ["GOOGLE_API_KEY"] = "AIzaSyA27oLqSp1kPNvyq_UJGlKlPP_FeJGZOi4"

# Initialize database session state
if 'db' not in st.session_state:
    st.session_state['db'] = None

def run_query(db_uri):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        # Connect to the database
        llm = ChatGoogleGenerativeAI(model="gemini-pro")
        chain = create_sql_query_chain(llm, db)
        response = chain.invoke({"question": "How many artists are there"})
        response = response.replace("```sql", "").replace("```", "")
        return response
    finally:
        loop.close()

# App title
st.markdown(f'<p class="other-big">Hey Buddy! I\'m <span style="color:#A350FF">Berdola.</span>🫧</p>', unsafe_allow_html=True)
st.markdown(f'<p style="font-family:Poppins; color:#6E726E; width: 550px;  ">Ready to explore your <span style="color:#A350FF">database</span>? Go ahead and ask me anything! I\'m here to help make querying a breeze. 🤖🍀</p>', unsafe_allow_html=True)

# Image
st.sidebar.markdown(
    """
    <style>
    .img-circle {
        border-radius: 50%;
        width: 70%;
        display: block;
        margin: auto;
        margin-top: -30px;
    }
    </style>
    <img class='img-circle' src='https://ipfs.pixura.io/ipfs/QmQDZJqTQXJvjjhkBSkYkcnE8L7QkRTH6P6LMbMcuMa1UF' />
    """,
    unsafe_allow_html=True,
)

# Sidebar title
st.sidebar.markdown(f'<p class="big-font">BERDOLA</p>', unsafe_allow_html=True)
st.sidebar.markdown(f'<p style="font-family:Poppins; color:#787582; text-align: center; margin-bottom: 50px">Your <span style="color:#A350FF">SQL Query</span> Buddy</p>', unsafe_allow_html=True)

# Database Connection
db_uri = st.sidebar.text_input('Enter your MySQL database URI', placeholder="Enter here...")
response_placeholder = st.sidebar.empty()
col1, col2, col3 = st.sidebar.columns([1.5,2,1])
# Create a placeholder for the response messages

if col2.button('Connect', type="primary"):
    if db_uri:
        try:
            # Connect to the database
            dbURI = "mysql+mysqlconnector:" + db_uri
            print(dbURI)
            db = SQLDatabase.from_uri(dbURI)
            st.session_state['db'] = db
            response_placeholder.markdown('<p class="Success"> Connected to the database</p>', unsafe_allow_html=True)
        except Exception as e:
            response_placeholder.markdown(f'<p class="Error">An error occurred: {e}</p>', unsafe_allow_html=True)
    else:
        response_placeholder.markdown('<p class="Warning">Please enter a database URI</p>', unsafe_allow_html=True)

#Copyright char
st.sidebar.markdown(f'<p style="font-family:Poppins; color:#787582; text-align: center; margin-top: 80px; font-size:12px;">© 2024 Berdola. All rights reserved.</p>', unsafe_allow_html=True)
# Initialize result
result = None

# Main area for running the query
if st.session_state['db'] is not None:
    # Layout with input field and button
    input_col, button_col = st.columns([5, 1])
    with input_col:
        input_query = st.text_input('', placeholder='Enter your query here, bud!')
    with button_col:
        st.write("")  # Create some space to push the button to the bottom
        st.write("")  # Create some space to push the button to the bottom
        if st.button('Run Query', type="primary"):
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                def clean_sql_query(query):
                    return query.replace("```sql", "").replace("```", "")
                
                llm = ChatGoogleGenerativeAI(model="gemini-pro")
                execute_query = QuerySQLDataBaseTool(db=st.session_state['db'])
                write_query = create_sql_query_chain(llm, st.session_state['db'])
                chain = write_query | execute_query
    
                answer_prompt = PromptTemplate.from_template(
                    """Given the following user question, corresponding SQL query, and SQL result, answer the user question.
    
                    Question: {question}
                    SQL Query: {query}
                    SQL Result: {result}
                    Answer: """
                )
    
                clean_query = RunnableLambda(clean_sql_query)
                answer = answer_prompt | llm | StrOutputParser()
                chain = (
                    RunnablePassthrough.assign(query=write_query).assign(
                        result=itemgetter("query") | clean_query | execute_query
                    )
                    | answer
                )
    
                result = chain.invoke({"question": input_query})
            except Exception as e:
                result = f'<p class="Error">An error occurred: {e}</p>'
            finally:
                loop.close()
                
# Display the result
if result is not None:
    st.markdown(f'<p class="Result">{result}</p>', unsafe_allow_html=True)