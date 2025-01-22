import json
import httpx
from bs4 import BeautifulSoup
from phi.agent import Agent
from phi.model.groq import Groq
from phi.tools.googlesearch import GoogleSearch 
from phi.tools.duckduckgo import DuckDuckGo
from dotenv import load_dotenv
import openai
import os
import time

# Load environment variables
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

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
    instructions=["You are an agentic AI of Daffodil International University.", "Always provide information based on Daffodil International University data."],
    markdown=True, 
)

multi_ai_agent.print_response("How to join Data Science club? ", stream=True)
