# Import necessary libraries
try:
    from phi.agent import Agent
    from phi.model.groq import Groq
    from phi.storage.agent.sqlite import SqlAgentStorage
    from phi.playground import Playground, serve_playground_app
except ModuleNotFoundError as e:
    raise ModuleNotFoundError("The 'phi' library is not installed. Please install it by running 'pip install phi' and ensure your environment supports it.") from e

# Define the Agent
agent = Agent(
    name="Daffodil Assistant",
    role="AI assistant for Daffodil International University",
    model=Groq(id="llama3-70b-8192"),  # Using the default model
    storage=SqlAgentStorage(db_file="daffodil_agent_storage.db", table_name="university_queries"),
    instructions=[
        "You are an AI assistant for Daffodil International University.",
        "Answer questions related to university courses, schedules, facilities, and general queries.",
        "Provide concise, accurate, and helpful responses."
    ],
    markdown=True,
)

# Function to process user queries
def process_query(query):
    """
    Handles user queries by interacting with the Agent.
    """
    try:
        # Run the query using the Agent
        response = agent.run(query)
        
        # Extract and return the content from the response
        if hasattr(response, 'content'):
            return response.content
        else:
            return "Error: Unable to extract response content."
    except Exception as e:
        return f"Error: {e}"

# Streamlit App
import streamlit as st

def main():
    """
    Main function for the Streamlit app.
    """
    st.title("Daffodil University Assistant")
    st.write("This app interacts with an AI agent dedicated to answering queries about Daffodil International University.")

    # Input field for the user query
    user_input = st.text_input("Enter your query (e.g., 'What are the available courses?'):")

    # Submit button to process the query
    if st.button("Submit"):
        if user_input:
            with st.spinner("Processing your query..."):
                response = process_query(user_input)
            st.write("### Response:")
            st.write(response)
        else:
            st.warning("Please enter a query.")

if __name__ == "__main__":
    try:
        main()
    except ModuleNotFoundError as e:
        st.error("The 'phi' library is not installed. Please ensure it is installed and accessible.")
    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")
