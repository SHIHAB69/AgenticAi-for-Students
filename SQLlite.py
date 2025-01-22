import json 
from rich.console import Console 
from rich.panel import Panel 
from rich.json import JSON 
from phi.model.groq import Groq 
from phi.tools.duckduckgo import DuckDuckGo 
from phi.agent import Agent 
from dotenv import load_dotenv 
from phi.storage.agent.sqlite import SqlAgentStorage
load_dotenv() 
ASSISTANT_NAME = "EduBot"
SESSION_ID = "xxxx-xxxx-xxxx-xxxx"
MAX_HISTORY_LENGTH = 15 
agent = Agent( 
    model=Groq(id="llama-3.3-70b-specdec"),
    storage=SqlAgentStorage(table_name="agent_sessions", db_file="tmp/agent_storage.db"), 
    tools=[DuckDuckGo()], 
    instructions=["first askthe name then Always search web and give a detailed information with human understanding for user"],
    add_history_to_messages=True,
    num_history_responses=5,
    session_id=SESSION_ID,
    description=f"You are {ASSISTANT_NAME}, a helpful assistant that always responds in a polite, upbeat and positive manner. You are assisting user with their queries.",)
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
        agent.print_response(user_query)
        return True
while True: 
    user_query = input("You: ")
    if not handle_user_query(user_query):
        break 
