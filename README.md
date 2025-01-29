# **Agentic AI - Daffodil University Multi-Agent System**

## **🔹 Overview**
Agentic AI is an intelligent multi-agent system designed for **Daffodil International University (DIU)** students. It consists of multiple specialized agents to assist with various university-related queries, including:

- **Academic Agent:** Provides course details, schedules, and university policies.
- **Admission Agent:** Assists with admission processes, eligibility, and fee details.
- **Campus Agent:** Offers information about campus facilities and events.
- **Routine Agent:** Fetches the latest class routine from **diuroutine.com**.
- **Email Agent:** Reads and replies to unread emails automatically with a single click.
- **OCR Agent:** Extracts and summarizes text from images uploaded by users.

This system is built using **GROQ API**, **PhiData**, and **Streamlit** to create an interactive and efficient AI-powered assistant.

---

## **🔹 Features**
✅ **Multi-Agent System** - Dedicated agents for different university-related queries.  
✅ **Automated Email Handling** - Reads unread emails and provides AI-generated replies.  
✅ **Class Routine Fetcher** - Retrieves updated class schedules directly from **diuroutine.com**.  
✅ **OCR Processing** - Reads and summarizes text from uploaded images.  
✅ **Streamlit UI** - Provides an interactive chat-based interface.  

---

## **🔹 Installation Guide**

### **Step 1: Clone the Repository**
```sh
git clone https://github.com/SHIHAB69/agenticAI-main.git
cd AgenticAI
```

### **Step 2: Create a Virtual Environment (Optional but Recommended)**
```sh
python -m venv venv
source venv/bin/activate   # On macOS/Linux
venv\Scripts\activate      # On Windows
```

### **Step 3: Install Required Dependencies**
```sh
pip install -r requirements.txt
```

#### **🔹 Install GROQ API**
GROQ API is used as the AI model for all agents.
Follow the official documentation to set up your API key:  
🔗 [GROQ Official Docs](https://docs.groq.com/)

#### **🔹 Install PhiData (Agent Framework)**
```sh
pip install phi
```
🔗 [PhiData Documentation](https://phidata.ai/docs/)

#### **🔹 Install Streamlit (For UI)**
```sh
pip install streamlit
```
🔗 [Streamlit Official Docs](https://docs.streamlit.io/)

### **Step 4: Set Up Environment Variables**
Create a **.env** file in the root directory and add your credentials:
```ini
GROQ_API_KEY=your_groq_api_key
SENDER_EMAIL=your_email@example.com
SENDER_PASSKEY=your_email_app_password
```

### **Step 5: Run the Application**
```sh
streamlit run chatbot.py
```

---

## **🔹 Usage**
1. Open the **Streamlit UI** and enter your query.
2. Select the appropriate agent (**Academic, Admission, Campus, Email, Routine, OCR**).
3. View AI-generated responses and interact with the system.

---

## **🔹 Contributors**
💡 **Developed by:** Agentic Solution BD  
📍 **Affiliation:** **Data Science Club, Daffodil International University**

---

## **🔹 Future Enhancements**
🚀 Integration with WhatsApp for chatbot functionality.  
🚀 Improved natural language understanding (NLP) for better responses.  
🚀 Cloud-based database for conversation history storage.

---

## **🔹 License**
This project is open-source under the **MIT License**.

Feel free to contribute and improve **Agentic AI**! 🚀

