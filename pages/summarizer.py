import streamlit as st
from PIL import Image
import pytesseract

# Set up Tesseract executable path if needed
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'  # Update this according to your Tesseract installation path

# Import necessary libraries for agents
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
def route_query(agent_name, query, history, extracted_text):
    agents = {
        "academic": academic_agent,
        "admission": admission_agent,
        "campus": campus_agent,
    }
    
    agent = agents.get(agent_name)
    if not agent:
        return f"Error: Agent '{agent_name}' not found."

    try:
        # Add the history and extracted text to the query
        full_query = "\n".join(history) + "\n" + extracted_text + "\n" + query
        response = agent.run(full_query)
        if hasattr(response, 'content'):
            return response.content
        else:
            return "Error: Unable to extract response content."
    except Exception as e:
        return f"Error: {e}"

st.set_page_config(
    page_title="OCR and Agent System",
    page_icon="🔍",
)

st.title("Daffodil University Multi-Agent System with OCR")

# Initialize chat history and OCR-extracted text
if "messages" not in st.session_state:
    st.session_state.messages = []
if "extracted_text" not in st.session_state:
    st.session_state.extracted_text = ""

# Image input
uploaded_file = st.file_uploader("Upload a text-based image", type=["png", "jpg", "jpeg"])

if uploaded_file is not None:
    # Display the uploaded image
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Image", use_container_width=True)

    # Perform OCR on the image
    extracted_text = pytesseract.image_to_string(image)

    # Store the extracted text in session state
    st.session_state.extracted_text = extracted_text

    # Display the extracted text
    st.subheader("Extracted Text")
    st.text(extracted_text)

# React to user input
if user_input := st.chat_input("Ask anything about Daffodil International University!"):
    # Display user message in chat message container
    st.chat_message("user").markdown(user_input)
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": user_input})

    # Process the user query based on selected agent
    agent_choice = "academic"  # For now, default to "academic"
    history = [msg["content"] for msg in st.session_state.messages if msg["role"] == "user"]
    response = route_query(agent_choice, user_input, history, st.session_state.extracted_text)

    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        st.markdown(response)
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})
