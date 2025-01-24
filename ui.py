import streamlit as st
from playground import get_agent_response

st.title("Agentic AI - Daffodil International University")

# Input from the user
user_input = st.text_input("Enter your query:")

if st.button("Get Response"):
    if user_input:
        with st.spinner("Fetching response..."):
            try:
                # Call the function to get the response
                response_text = get_agent_response(user_input)
                st.markdown(response_text)
            except Exception as e:
                st.error(f"An error occurred: {e}")
    else:
        st.warning("Please enter a query.")
