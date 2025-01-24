# Import necessary libraries
try:
    from phi.agent import Agent
    from phi.model.groq import Groq
    from phi.storage.agent.sqlite import SqlAgentStorage
    from phi.playground import Playground, serve_playground_app
except ModuleNotFoundError as e:
    raise ModuleNotFoundError("The 'phi' library is not installed. Please install it by running 'pip install phi' and ensure your environment supports it.") from e

# Define agents for Daffodil International University
academic_agent = Agent(
    name="Academic Advisor",
    role="An agent dedicated to answering academic queries for Daffodil International University students.",
    model=Groq(id="llama3-70b-8192"),
    storage=SqlAgentStorage(db_file="agent_storage.db", table_name="academic_responses"),
    instructions=[
        "Provide accurate academic-related information, including course details, schedules, and exam dates.",
        "Assist students with university policies and procedures."
    ],
    markdown=True,
)

admission_agent = Agent(
    name="Admission Helper",
    role="An agent dedicated to assisting with admission-related queries.",
    model=Groq(id="llama3-70b-8192"),
    storage=SqlAgentStorage(db_file="agent_storage.db", table_name="admission_responses"),
    instructions=[
        "Guide users through the admission process, including eligibility criteria, deadlines, and required documents.",
        "Provide details about tuition fees, scholarships, and financial aid options."
    ],
    markdown=True,
)

campus_agent = Agent(
    name="Campus Guide",
    role="An agent providing information about campus facilities, events, and services.",
    model=Groq(id="llama3-70b-8192"),
    storage=SqlAgentStorage(db_file="agent_storage.db", table_name="campus_responses"),
    instructions=[
        "Answer queries related to campus facilities, including libraries, cafeterias, and labs.",
        "Provide updates about ongoing or upcoming campus events."
    ],
    markdown=True,
)

# Function to route queries to the appropriate agent
def route_query(agent_name, query):
    agents = {
        "academic": academic_agent,
        "admission": admission_agent,
        "campus": campus_agent,
    }
    
    agent = agents.get(agent_name)
    if not agent:
        return f"Error: Agent '{agent_name}' not found."

    try:
        response = agent.run(query)
        if hasattr(response, 'content'):
            return response.content
        else:
            return "Error: Unable to extract response content."
    except Exception as e:
        return f"Error: {e}"

# Streamlit App
import streamlit as st

def main():
    st.title("Daffodil University Multi-Agent System")
    st.write("This app interacts with multiple AI agents dedicated to different domains at Daffodil International University.")

    agent_choice = st.selectbox("Choose an agent:", ["academic", "admission", "campus"])
    user_input = st.text_input("Enter your query:")

    if st.button("Submit"):
        if user_input:
            with st.spinner("Processing your query..."):
                response = route_query(agent_choice, user_input)
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
