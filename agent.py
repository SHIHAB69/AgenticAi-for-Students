import json
import httpx
from bs4 import BeautifulSoup
from phi.agent import Agent
from phi.model.groq import Groq
from phi.tools.googlesearch import GoogleSearch
from phi.tools.duckduckgo import DuckDuckGo
from cachetools import cached, TTLCache

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
    model=Groq(id="llama3-70b-8192"),
)

# Google search agent
google_agent = Agent(
    name="Web Agent",
    role="You are an agentic AI and will behave like that. You are made by Team DIU. All the prompts you'll receive should provide output according to Daffodil International University. Always remember this information.",
    tools=[GoogleSearch()],
    instructions=["Always include sources"],
    show_tool_calls=True,
    markdown=True,
    model=Groq(id="llama3-70b-8192"),
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
    model=Groq(id="llama3-70b-8192")
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

# Official website data agent
def get_diu_latest_news() -> str:
    """Fetches the latest news from the DIU official website.

    Returns:
        str: JSON string of the latest news.
    """
    try:
        response = httpx.get('https://daffodilvarsity.edu.bd/')
        response.raise_for_status()
    except httpx.RequestError as e:
        return json.dumps({"error": f"An error occurred while requesting data: {e}"})
    except httpx.HTTPStatusError as e:
        return json.dumps({"error": f"Non-success status code received: {e.response.status_code}"})

    # Parse the response content
    soup = BeautifulSoup(response.content, 'html.parser')
    news_data = []

    # Assuming each news item is within a div with class 'news-item'
    news_items = soup.find_all('div', class_='news-item')
    
    for item in news_items:
        title = item.find('h3').text.strip() if item.find('h3') else "No title"
        link = item.find('a')['href'] if item.find('a') else "No link"
        date = item.find('span', class_='news-date').text.strip() if item.find('span', class_='news-date') else "No date"

        news_info = {
            'title': title,
            'link': link,
            'date': date
        }
        
        news_data.append(news_info)

    return json.dumps(news_data, indent=2)

# DIU news agent setup
diu_news = Agent(
    name="DIU News Agent",
    tools=[get_diu_latest_news],
    instructions=["Provide the latest news from the official website of Daffodil International University when you're asked.", "Provide short answer for this agent"],
    show_tool_calls=True,
    markdown=True,
    model=Groq(id="llama3-70b-8192")
)