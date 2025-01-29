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
import streamlit as st

# Load environment variables
load_dotenv()

# Initialize the agent
agent = Agent(model=Groq(id="llama-3.3-70b-versatile"))

# Database file path
DATABASE_FILE = 'conversation_database.db'

# Email configuration
sender_email = os.getenv("SENDER_EMAIL")
sender_name = os.getenv("SENDER_NAME")
sender_passkey = os.getenv("SENDER_PASSKEY")

# Initialize EmailTools with required configuration
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

    for user_input, agent_response in reversed(conversations):
        user_tokens = len(user_input) // 4
        agent_tokens = len(agent_response) // 4
        total_tokens += user_tokens + agent_tokens

        if total_tokens > max_tokens:
            break

        truncated_history.append((user_input, agent_response))

    truncated_history.reverse()
    return truncated_history

def send_email_smtp(receiver_email, subject, body):
    """
    Send an email using SMTP.
    """
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(sender_email, sender_passkey)
        server.sendmail(sender_email, receiver_email, msg.as_string())
        server.close()
        return "Email sent successfully."
    except Exception as e:
        return f"Error sending email: {e}"

def check_incoming_email():
    """
    Check for new emails using IMAP.
    """
    try:
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login(username, password)
        mail.select("inbox")
        status, messages = mail.search(None, 'UNSEEN')
        messages = messages[0].split()

        if messages:
            for msg in messages[-1:]:
                _, msg_data = mail.fetch(msg, "(RFC822)")
                for response_part in msg_data:
                    if isinstance(response_part, tuple):
                        msg = email.message_from_bytes(response_part[1])
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

    except Exception as e:
        return f"Error checking email: {e}"

# Initialize the database
initialize_database()

# Streamlit App
st.title("Email Agent with Conversation Management")

menu = st.sidebar.selectbox("Menu", ["Email Inbox", "Conversation History"])

if menu == "Email Inbox":
    st.header("Check Incoming Emails")

    if st.button("Check Email"):
        incoming_email = check_incoming_email()

        if incoming_email:
            st.write("**From:**", incoming_email['from'])
            st.write("**Subject:**", incoming_email['subject'])
            st.write("**Body:**", incoming_email['body'])

            try:
                response = agent.run(f"User: {incoming_email['body']}\nAgent:")
                agent_response = response.messages[-1].content if hasattr(response, 'messages') else "No response generated."
                save_to_database(incoming_email['body'], agent_response)
                email_status = send_email_smtp(incoming_email['from'], f"Re: {incoming_email['subject']}", agent_response)
                st.success(email_status)
            except Exception as e:
                st.error(f"Error: {e}")
        else:
            st.write("No new emails found.")

elif menu == "Conversation History":
    st.header("Conversation History")

    all_conversations = fetch_all_conversations()

    if all_conversations:
        for idx, (user, agent) in enumerate(all_conversations, 1):
            st.write(f"**{idx}. User:** {user}")
            st.write(f"**Agent:** {agent}")
    else:
        st.write("No conversation history found.")
