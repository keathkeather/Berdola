import streamlit as st
from langchain_community.utilities import SQLDatabase
import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import create_sql_query_chain
import asyncio

os.environ["GOOGLE_API_KEY"]
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
         , caption='Meet B-erd.')

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


query = st.text_input('chat with KET THE SQL QUERIERRRRR')

# Button to run the query
if st.session_state['db'] is not None:
    if st.button('Run Query'):
        try:
            # Run the query
            result = queryWithAI(st.session_state['db'],query)

            # Display the result
            st.markdown(f'<p style="font-family:sans-serif; color:Green;">{result}</p>', unsafe_allow_html=True)

        except Exception as e:
            st.write(f"An error occurred: {e}")