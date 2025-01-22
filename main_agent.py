import json
import httpx
from rich.console import Console
from rich.panel import Panel
from rich.json import JSON
from rich.layout import Layout
from rich.align import Align
from rich.spinner import Spinner
from bs4 import BeautifulSoup
from phi.agent import Agent
from phi.model.groq import Groq
from phi.tools.duckduckgo import DuckDuckGo
from phi.storage.agent.sqlite import SqlAgentStorage
from dotenv import load_dotenv
import time
from cachetools import cached, TTLCache
import speech_recognition as sr
# Load environment variables
load_dotenv()
SESSION_ID = "xxxx-xxxx-xxxx-xxxx"
MAX_HISTORY_LENGTH = 15

# Console setup for rich output
console = Console()

# Set up a cache with a time-to-live (TTL) of 10 minutes
cache = TTLCache(maxsize=100, ttl=600)

# Function to fetch club information
@cached(cache)
def get_club_information() -> str:
    try:
        response = httpx.get('https://clubs.daffodilvarsity.edu.bd/')
        response.raise_for_status()
    except httpx.RequestError as e:
        return "An error occurred while fetching club information. Please try again later."
    except httpx.HTTPStatusError as e:
        return "Failed to retrieve club data. Please check the website for updates."

    soup = BeautifulSoup(response.content, 'html.parser')
    clubs_data = []
    club_cards = soup.find_all('div', class_='club-card')
    for card in club_cards:
        club_name = card.find('h3').text.strip() if card.find('h3') else "Unknown Club Name"
        club_description = card.find('p').text.strip() if card.find('p') else "No description available"
        clubs_data.append(f"{club_name}: {club_description}")
    return "\n".join(clubs_data)


# Function to fetch DIU latest news
@cached(cache)
def get_diu_latest_news() -> str:
    try:
        response = httpx.get('https://daffodilvarsity.edu.bd/')
        response.raise_for_status()
    except httpx.RequestError as e:
        return "An error occurred while fetching DIU news. Please try again later."
    except httpx.HTTPStatusError as e:
        return "Failed to retrieve DIU news. Please check the website for updates."

    soup = BeautifulSoup(response.content, 'html.parser')
    news_data = []
    news_items = soup.find_all('div', class_='news-item')
    for item in news_items[:5]:  # Limit to 5 latest news items
        title = item.find('h3').text.strip() if item.find('h3') else "No title"
        link = item.find('a')['href'] if item.find('a') else "No link"
        news_data.append(f"{title} (More info: {link})")
    return "\n".join(news_data)


# Setup DIUbot agents
club_agent = Agent(
    name="DIUbot",
    tools=[get_club_information],
    role="You provide up-to-date information about clubs at Daffodil International University. Respond only with relevant club details in a friendly tone.",
    show_tool_calls=False,
    markdown=True,
    model=Groq(id="llama3-70b-8192"),
)

news_agent = Agent(
    name="DIUbot",
    tools=[get_diu_latest_news],
    role="You provide the latest news from Daffodil International University. Respond only with concise news headlines and links.",
    show_tool_calls=False,
    markdown=True,
    model=Groq(id="llama3-70b-8192"),
)

search_agent = Agent(
    name="DIUbot",
    tools=[DuckDuckGo()],
    role="You assist with finding information relevant to Daffodil International University. Respond concisely and include only necessary details.",
    instructions=["Do not reveal tool usage or backend processes."],
    show_tool_calls=False,
    markdown=True,
    model=Groq(id="llama3-70b-8192"),
)

# Multi-agent setup
multi_ai_agent = Agent(
    team=[club_agent, news_agent, search_agent],
    model=Groq(id="llama3-70b-8192"),
    storage=SqlAgentStorage(table_name="agent_sessions", db_file="tmp/agent_storage.db"),
    add_history_to_messages=True,
    num_history_responses=5,
    instructions=[
        "You are DIUbot, an AI assistant for Daffodil International University.",
        "Always provide concise, accurate, and clear responses.",
        "Avoid repeating the user's question or revealing backend processes.",
    ],
    markdown=True,
)


# Function for voice input
def listen_to_voice_command() -> str:
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        console.print(Panel("🎤 Listening for a voice command...", style="bold green"))
        try:
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)
            command = recognizer.recognize_google(audio)
            console.print(f"[bold cyan]You said:[/bold cyan] {command}")
            return command
        except sr.UnknownValueError:
            console.print("[bold yellow]Sorry, I could not understand the audio.[/bold yellow]")
            return ""
        except sr.RequestError as e:
            console.print(f"[bold red]Error with the speech recognition service: {e}[/bold red]")
            return ""


# Main handler
if __name__ == "__main__":
    while True:
        console.print(Panel("Choose Input Method", style="bold blue"))
        console.print("1. [bold yellow]Text input[/bold yellow]\n2. [bold green]Voice input[/bold green]\n0. [bold red]Exit[/bold red]")
        choice = input("Enter your choice: ").strip()

        if choice == "1":
            command = input("Enter your command: ").strip()
        elif choice == "2":
            command = listen_to_voice_command()
        elif choice == "0":
            console.print(Panel("Exiting the application. Goodbye! 👋", style="bold green"))
            break
        else:
            console.print(Panel("Invalid choice. Please select 1, 2, or 0.", style="bold red"))
            continue

        if command:
            console.print(Panel("[bold green]Processing your command...[/bold green]", style="bold cyan"))
            try:
                spinner = Spinner("dots", text="Processing...")
                with console.status(spinner):
                    response = multi_ai_agent.run(command)
                console.print(Panel(f"💬 [bold cyan]DIUbot's Response:[/bold cyan]\n\n{response}", style="bold green"))
            except Exception as e:
                console.print(Panel(f"[bold red]An error occurred:[/bold red] {e}", style="bold red"))
