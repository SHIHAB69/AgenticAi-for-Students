Agentic AI - Daffodil University Multi-Agent System

Overview

Agentic AI is an intelligent multi-agent system built specifically for Daffodil International University (DIU) students. It features multiple AI-driven agents that assist users with academic inquiries, admission procedures, campus information, email automation, routine updates, and document OCR processing. The system is built using GROQ API, PhiData agents framework, and Streamlit for an interactive UI.

Features

1. Multi-Agent System

Academic Agent: Provides academic-related information such as course details, exam schedules, and policies.

Admission Agent: Assists with the admission process, eligibility criteria, deadlines, and financial aid.

Campus Agent: Offers information about campus facilities, events, and student services.

Email Agent: Reads unread emails and generates automatic replies with a single click.

Routine Agent: Fetches updated class schedules from diuroutine.com and provides the latest routine image.

OCR Agent: Extracts text from user-uploaded images and summarizes it using AI.

2. Automated Email Handling

Reads incoming unread emails.

Automatically generates responses using AI.

Sends replies with a single click.

3. Class Routine Fetching

Retrieves the latest class routine image based on batch and section.

Displays the routine in the UI.

4. Interactive UI with Streamlit

Users can interact with different agents through a chatbot-style interface.

Streamlined query handling with chat history preservation.

Installation Guide

Prerequisites

Python 3.8+

pip (Python Package Installer)

Virtual environment (recommended)

Step 1: Clone the Repository

git clone https://github.com/your-repo/agentic-ai.git
cd agentic-ai

Step 2: Set Up a Virtual Environment (Recommended)

python -m venv env
source env/bin/activate  # On macOS/Linux
env\Scripts\activate  # On Windows

Step 3: Install Dependencies

pip install -r requirements.txt

API Setup

This project uses the GROQ API for AI-powered responses. You need an API key from GROQ to proceed.

Step 4: Configure Environment Variables

Create a .env file in the root directory and add the following:

GROQ_API_KEY="your_groq_api_key_here"
SENDER_EMAIL="your_email@example.com"
SENDER_PASSKEY="your_email_passkey"

Running the Application

Start the Streamlit UI

streamlit run chatbot.py

Run the Routine Agent

streamlit run routine.py

Run the Email Agent

streamlit run email.py

Technology Stack

GROQ API - For AI-powered chat and automation.

PhiData - For managing multi-agent interactions.

Streamlit - For building the interactive user interface.

SQLite - For storing conversation history.

IMAP & SMTP - For email automation.

OCR (Optical Character Recognition) - For extracting text from images.

References & Official Documentation

GROQ API Documentation

PhiData Official Documentation

Streamlit Official Documentation

Future Enhancements

Add more intelligent agents for student counseling and career guidance.

Implement voice-based query support.

Integrate push notifications for real-time updates.

🚀 Built for DIU students to make their university experience smoother!

You can customize it for your Uni Students
