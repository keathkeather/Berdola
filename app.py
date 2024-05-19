import streamlit as st
from langchain_community.utilities import SQLDatabase
import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import create_sql_query_chain
from langchain_community.tools.sql_database.tool import QuerySQLDataBaseTool
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough,RunnableLambda
from operator import itemgetter
import asyncio

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


def queryWithAI(db,request):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
            llm = ChatGoogleGenerativeAI(model="gemini-pro")
            chain = create_sql_query_chain(llm, db)
            query = chain.invoke({"question": request})
            query = query.replace("```sql", "").replace("```", "")
            return db.run(query)
    finally:
        loop.close()
# Title of the app
st.title('QUERY WITH B-ERD (our sql query chatbot)')
st.image('https://scontent.fceb3-1.fna.fbcdn.net/v/t1.6435-9/87454319_2787791111347251_2582408314319011840_n.jpg?_nc_cat=110&ccb=1-7&_nc_sid=5f2048&_nc_eui2=AeGahkLc6lk4NMvqXItf1cGr3yU1FpFZEnDfJTUWkVkScCOCw-m7A60I9k-1VkkNPTtoYt6QNe3ZuqVfJrIZG7mB&_nc_ohc=vXLxAs3a7JIQ7kNvgFVFOkM&_nc_ht=scontent.fceb3-1.fna&oh=00_AYAd3yKF55zoV-juHvodSoBPa-eoYYKHJY7-hgsG2wxw3w&oe=66706778'
         , caption='Meet Berd.')

# Input for the database URI
db_uri = st.text_input('Enter your database URI')

# Button to run the query
if st.button('Connect to database'):
    if db_uri:
        try:
            # Connect to the database
            dbURI = "mysql+mysqlconnector:"+db_uri
            print(dbURI)
            db = SQLDatabase.from_uri(dbURI)

            st.session_state['db'] = SQLDatabase.from_uri(dbURI)
            st.write("Connected to the database")
        except Exception as e:
            st.write(f"An error occurred: {e}")
    else:
        st.write("Please enter a database URI")


Inputquery = st.text_input('chat with KET THE SQL QUERIERRRRR')

# Button to run the query
if st.session_state['db'] is not None:
    if st.button('Run Query'):
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            def clean_sql_query(query):
                return query.replace("```sql", "").replace("```", "")
            
            llm = ChatGoogleGenerativeAI(model="gemini-pro")
            execute_query = QuerySQLDataBaseTool(db=st.session_state['db'])
            write_query = create_sql_query_chain(llm, st.session_state['db'])
            chain = write_query | execute_query
            # chain.get_prompts()[0].pretty_print()
            answer_prompt = PromptTemplate.from_template(
                """Given the following user question, corresponding SQL query, and SQL result, answer the user question.

            Question: {question}
            SQL Query: {query}
            SQL Result: {result}
            Answer: """
            )

            clean_query = RunnableLambda(clean_sql_query)
            # chain.get_prompts()[0].pretty_print()
            answer = answer_prompt | llm | StrOutputParser()
            chain = (
                RunnablePassthrough.assign(query=write_query).assign(
                    result=itemgetter("query") | clean_query | execute_query
                )
                | answer
            )

            result = chain.invoke({"question": Inputquery})
            st.markdown(f'<p style="font-family:sans-serif; color:Green;">{result}</p>', unsafe_allow_html=True)
        except Exception as e:
            st.markdown(f'<p style="font-family:sans-serif; color:Red;">An error occurred: {e}</p>', unsafe_allow_html=True)
        finally:
            loop.close()