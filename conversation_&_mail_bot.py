import sqlite3
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from phi.agent import Agent
from phi.model.groq import Groq
from dotenv import load_dotenv
import imaplib
import email
from email.header import decode_header

# Load environment variables
load_dotenv()

# Initialize the agent
agent = Agent(model=Groq(id="llama-3.3-70b-versatile"))

# Database file path
DATABASE_FILE = 'conversation_database.db'

# Email configuration (you need to set these in your .env file)
sender_email = os.getenv("SENDER_EMAIL")
sender_name = os.getenv("SENDER_NAME")
sender_passkey = os.getenv("SENDER_PASSKEY")

# Initialize EmailTools with required configuration (for checking emails)
username = sender_email
password = sender_passkey  # Use the app password here

# Initialize the database
def initialize_database():
    """
    Initialize the SQLite database and ensure the conversations table has the correct schema.
    """
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()

    # Check if the table already exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='conversations'")
    if cursor.fetchone() is not None:
        # Check the schema of the existing table
        cursor.execute("PRAGMA table_info(conversations)")
        columns = [column[1] for column in cursor.fetchall()]
        if 'user_input' not in columns or 'agent_response' not in columns:
            print("Incorrect schema detected. Dropping and recreating the table...")
            cursor.execute("DROP TABLE conversations")
            conn.commit()

    # Create the table with the correct schema
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_input TEXT,
            agent_response TEXT
        )
    ''')
    conn.commit()
    conn.close()

def save_to_database(user_input, agent_response):
    """
    Save a conversation entry to the database.
    """
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute('INSERT INTO conversations (user_input, agent_response) VALUES (?, ?)', (user_input, agent_response))
    conn.commit()
    conn.close()

def fetch_all_conversations():
    """
    Fetch all conversations from the database.
    """
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute('SELECT user_input, agent_response FROM conversations')
    conversations = cursor.fetchall()
    conn.close()
    return conversations

def get_formatted_history(conversations):
    """
    Format conversation history for agent context.
    """
    return "\n".join([f"User: {user}\nAgent: {response}" for user, response in conversations])

def truncate_conversation_history(conversations, max_tokens=5000):
    """
    Truncate the conversation history to ensure it doesn't exceed the token limit.
    """
    truncated_history = []
    total_tokens = 0

    # Iterate through conversations in reverse (most recent first)
    for user_input, agent_response in reversed(conversations):
        # Estimate token count (1 token ~= 4 characters for simplicity)
        user_tokens = len(user_input) // 4
        agent_tokens = len(agent_response) // 4
        total_tokens += user_tokens + agent_tokens

        # Stop if adding this conversation would exceed the limit
        if total_tokens > max_tokens:
            break

        # Add the conversation to the truncated history
        truncated_history.append((user_input, agent_response))

    # Reverse back to original order
    truncated_history.reverse()
    return truncated_history

# SMTP Email sending function
def send_email_smtp(receiver_email, subject, body):
    """
    Send an email using SMTP.
    """
    sender_email = os.getenv("SENDER_EMAIL")
    sender_password = os.getenv("SENDER_PASSKEY")

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject

    # Add the email body
    msg.attach(MIMEText(body, 'plain'))

    try:
        # Set up the server and send the email
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, receiver_email, msg.as_string())
        server.close()
        print("Email sent successfully.")
    except Exception as e:
        print(f"Error sending email: {e}")

# IMAP Email fetching function
def check_incoming_email():
    """
    Check for new emails using IMAP.
    """
    try:
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login(username, password)
        mail.select("inbox")  # You can change "inbox" to any folder

        # Search for unseen emails
        status, messages = mail.search(None, 'UNSEEN')
        messages = messages[0].split()

        # Fetch the latest email
        if messages:
            for msg in messages[-1:]:
                _, msg_data = mail.fetch(msg, "(RFC822)")
                for response_part in msg_data:
                    if isinstance(response_part, tuple):
                        msg = email.message_from_bytes(response_part[1])
                        # Decode the email subject
                        subject, encoding = decode_header(msg["Subject"])[0]
                        if isinstance(subject, bytes):
                            subject = subject.decode(encoding if encoding else 'utf-8')
                        from_ = msg.get("From")
                        body = ""

                        if msg.is_multipart():
                            for part in msg.walk():
                                if part.get_content_type() == "text/plain":
                                    body = part.get_payload(decode=True).decode()
                        else:
                            body = msg.get_payload(decode=True).decode()

                        return {"subject": subject, "from": from_, "body": body}

        return None

    except imaplib.IMAP4.error as e:
        print(f"IMAP Authentication Error: {e}")
        print("Please check your email credentials and ensure IMAP is enabled in your Gmail settings.")
        return None
    except Exception as e:
        print(f"Error checking email: {e}")
        return None

# Initialize the database
initialize_database()

print("Agent is ready. Type 'quit' to exit, 'history' to view saved conversations, or 'check_mail' to check for incoming emails.")

while True:
    user_input = input("Enter your request: ").strip()
    
    if user_input.lower() == 'quit':
        print("Exiting the program. Goodbye!")
        break
    if user_input.lower() == 'history':
        all_conversations = fetch_all_conversations()
        print("\nConversation History:")
        for idx, (user, agent) in enumerate(all_conversations, 1):
            print(f"{idx}. User: {user}\n   Agent: {agent}")
        continue
    if user_input.lower() == 'check_mail':
        # Check for new email
        incoming_email = check_incoming_email()

        if incoming_email:
            print("New Email Received:")
            print(f"From: {incoming_email['from']}")
            print(f"Subject: {incoming_email['subject']}")
            print(f"Body: {incoming_email['body']}")

            # Generate agent's response based on the email body
            try:
                response = agent.run(f"User: {incoming_email['body']}\nAgent:")
                agent_response = response.messages[-1].content if hasattr(response, 'messages') else "No response generated."
            except Exception as e:
                print(f"Error generating agent response: {e}")
                continue

            # Save email content and response to the database
            save_to_database(incoming_email['body'], agent_response)

            # Respond to the email
            try:
                send_email_smtp(incoming_email['from'], f"Re: {incoming_email['subject']}", agent_response)
                print(f"Response sent to {incoming_email['from']}")
            except Exception as e:
                print(f"Error sending email response: {e}")
        else:
            print("No new emails found.")
        continue

    # Retrieve conversation history for context
    previous_conversations = fetch_all_conversations()
    
    # Truncate the conversation history to avoid exceeding token limits
    truncated_conversations = truncate_conversation_history(previous_conversations)
    conversation_context = get_formatted_history(truncated_conversations)
    
    # Generate agent response
    try:
        response = agent.run(conversation_context + f"\nUser: {user_input}\nAgent:")
        agent_response = response.messages[-1].content if hasattr(response, 'messages') else "No response generated."
    except Exception as e:
        print(f"Error generating agent response: {e}")
        continue

    # Save conversation to database
    save_to_database(user_input, agent_response)
    print(f"Agent's Response: {agent_response}")
