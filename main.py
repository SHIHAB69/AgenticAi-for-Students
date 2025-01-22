import json
import httpx
from rich.console import Console 
from rich.panel import Panel
from rich.json import JSON 
from bs4 import BeautifulSoup
from phi.agent import Agent
from phi.model.groq import Groq
from phi.tools.googlesearch import GoogleSearch 
from phi.tools.duckduckgo import DuckDuckGo
from phi.storage.agent.sqlite import SqlAgentStorage
from dotenv import load_dotenv
import time

# Load environment variables
load_dotenv()
SESSION_ID = "xxxx-xxxx-xxxx-xxxx"
MAX_HISTORY_LENGTH = 15 

# DuckDuckGo agent
duck_agent = Agent(
    name="Web Agent",
    role="You are an agentic AI and will behave like that. You are made by Team DIU. All the prompts you'll receive should provide output according to Daffodil International University. Always remember this information.",
    tools=[DuckDuckGo()],
    instructions=["Always include sources"],
    show_tool_calls=True,
    markdown=True,
    model=Groq(id="llama-3.3-70b-versatile"),
)

# Google search agent
google_agent = Agent(
    name="Web Agent",
    role="You are an agentic AI and will behave like that. You are made by Team DIU. All the prompts you'll receive should provide output according to Daffodil International University. Always remember this information.",
    tools=[GoogleSearch()],
    instructions=["Always include sources"],
    show_tool_calls=True,
    markdown=True,
    model=Groq(id="llama-3.3-70b-versatile"),
)

# Club agent
def get_club_information() -> str:
    """Use this function to get information about clubs from Daffodil International University.

    Returns:
        str: JSON string of club information.
    """

    # Fetch the data from the website
    response = httpx.get('https://clubs.daffodilvarsity.edu.bd/')
    
    if response.status_code != 200:
        return json.dumps({"error": "Failed to fetch data from the website."})

    # Parse the response content
    soup = BeautifulSoup(response.content, 'html.parser')
    clubs_data = []

    # Assuming each club info is within a div with class 'club-card'
    club_cards = soup.find_all('div', class_='club-card')
    
    for card in club_cards:
        club_name = card.find('h3').text.strip()  # Adjust tag and class based on actual HTML
        club_description = card.find('p').text.strip()  # Adjust tag and class based on actual HTML
        
        # If there are additional details, extract them here as well
        club_info = {
            'name': club_name,
            'description': club_description
        }
        
        clubs_data.append(club_info)

    return json.dumps(clubs_data, indent=2)

club_agent = Agent(
    tools=[get_club_information],
    show_tool_calls=True,
    markdown=True,
    model=Groq(id="llama-3.3-70b-versatile")
)

# Handle DuckDuckGo rate limit
def safe_duckduckgo_search(query: str) -> str:
    try:
        results = DuckDuckGo().search(query)
        return json.dumps(results, indent=2)
    except Exception as e:
        if "Ratelimit" in str(e):
            time.sleep(5)  # Wait for 5 seconds before retrying
            return safe_duckduckgo_search(query)
        else:
            return json.dumps({"error": str(e)})

# Multi-agent setup
multi_ai_agent = Agent(
    team=[duck_agent, google_agent, club_agent],
    model=Groq(id="llama-3.3-70b-specdec"),
    storage=SqlAgentStorage(table_name="agent_sessions", db_file="tmp/agent_storage.db"),
    add_history_to_messages=True,
    num_history_responses=5,
    instructions=[
        "You are an agentic AI created for Daffodil International University.",
        "Answer all queries concisely and provide meaningful information.",
        "Do not repeat the user's question; instead, generate a thoughtful response."
    ],
    markdown=True, 
)

console = Console() 
conversation_history = []

def print_chat_history(agent):
    console.print( 
         Panel( 
             JSON(json.dumps([m.model_dump(include={"role", "content"}) for m in agent.memory.messages]), indent=4),
             title=f"Chat History for session_id: {agent.session_id}",
             expand=True, 
             )
        )
def handle_user_query(user_query): 
    conversation_history.append(user_query) 
    if len(conversation_history) > MAX_HISTORY_LENGTH:
        conversation_history.pop(0)
    if user_query.startswith("/exit"): 
        print("Conversation End.")
        return False 
    elif user_query.startswith("/clear"):
        conversation_history.clear() 
        print("Conversation history cleared.")
        return True 
    elif user_query.startswith("/history"): 
        print("Conversation History:")
        for i, query in enumerate(conversation_history):
            print(f"{i+1}. {query}")
            return True
    else:
        multi_ai_agent.print_response(user_query)
        return True
while True: 
    user_query = input("You: ")
    if not handle_user_query(user_query):
        break
