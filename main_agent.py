from phi.agent import Agent
from phi.model.groq import Groq
from dotenv import load_dotenv
from phi.tools.duckduckgo import DuckDuckGo
from phi.tools.yfinance import YFinanceTools

load_dotenv()
agent = Agent(
    name="Web Agent",
    role = "You are a agentic AI and will behave like that, and you made by Team DIU , always remeber this informaiton",
    tools=[DuckDuckGo()],
    instructions=["Always include sources"],
    show_tool_calls=True,
    markdown=True,
    model=Groq(id="llama-3.3-70b-versatile"),
)

agent.print_response("Today’s routine swe department swe batch")

