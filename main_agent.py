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
from cachetools import cached, TTLCache
from phi.playground import Playground, serve_playground_app

# Load environment variables
load_dotenv()
SESSION_ID = "xxxx-xxxx-xxxx-xxxx"
MAX_HISTORY_LENGTH = 15

# Set up a cache with a time-to-live (TTL) of 10 minutes
cache = TTLCache(maxsize=100, ttl=600)

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

# Club agent function
@cached(cache)
def get_club_information() -> str:
    """Use this function to get information about clubs from Daffodil International University.

    Returns:
        str: JSON string of club information.
    """
    try:
        # Fetch the data from the website
        response = httpx.get('https://clubs.daffodilvarsity.edu.bd/')
        response.raise_for_status()  # Raise an error for bad status codes
    except httpx.RequestError as e:
        return json.dumps({"error": f"An error occurred while requesting data: {e}"})
    except httpx.HTTPStatusError as e:
        return json.dumps({"error": f"Non-success status code received: {e.response.status_code}"})

    # Parse the response content
    soup = BeautifulSoup(response.content, 'html.parser')
    clubs_data = []

    # Assuming each club info is within a div with class 'club-card'
    club_cards = soup.find_all('div', class_='club-card')
    
    for card in club_cards:
        club_name = card.find('h3').text.strip() if card.find('h3') else "Unknown Club Name"
        club_description = card.find('p').text.strip() if card.find('p') else "No description available"
        
        # If there are additional details, extract them here as well
        club_info = {
            'name': club_name,
            'description': club_description
        }
        
        clubs_data.append(club_info)

    return json.dumps(clubs_data, indent=2)

# Club agent setup
club_agent = Agent(
    name="Club Agent",
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

# Playground setup
app = Playground(agents=[multi_ai_agent]).get_app()

# Main function to serve the app on localhost
if __name__ == "__main__":
    serve_playground_app("playground:app", reload=True)
