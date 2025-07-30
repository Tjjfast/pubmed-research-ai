# 🧠 Ayurveda Research Agent using Agno

An intelligent AI Agent that searches research papers from **PubMed**, filters **Ayurveda-specific** content, and summarizes the results. Powered by **Google Gemini** via Agno's framework, the agent leverages PubMed tools with custom logic for relevance, filtering, and structured output.

---

## 📌 Project Overview

This agent allows users to query PubMed in **natural language** (e.g., “Is Ashwagandha effective for anxiety?”), but **only returns papers relevant to Ayurveda**. Modern or unrelated topics (like chemotherapy, antibiotics, etc.) are explicitly filtered out.

### 🔍 Core Features

- PubMed search using Agno’s `PubmedTools`
- Ayurveda-focused filtering logic
- Summarization of research papers
- Debug mode to show tool usage & reasoning
- CLI interface + optional Agent-UI frontend

---

## 🎯 Purpose

To build a focused, transparent, and user-friendly research assistant that provides **evidence-based insights from PubMed** for traditional Ayurvedic medicine topics.

---

## 🚀 How to Run the Agent Locally

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/ayurveda-research-agent.git
cd ayurveda-research-agent
2. Set Up Python Environment
Create and activate a virtual environment:

bash
Copy
Edit
python -m venv venv
source venv/bin/activate      # On Windows: venv\Scripts\activate
3. Install Dependencies
bash
Copy
Edit
pip install -r requirements.txt
If requirements.txt is not present, install manually:

bash
Copy
Edit
pip install agno-sdk python-dotenv
🔐 API Key Setup
4. Create .env File
In the project root directory, create a .env file:

env
Copy
Edit
GOOGLE_API_KEY=your_gemini_api_key_here
Make sure your API key has access to Gemini 1.5 (via Google AI Studio).

💻 Running the CLI Agent
To run the command-line interface version:

bash
Copy
Edit
python Agent.py
You’ll be prompted to enter a natural language query.

Example:

bash
Copy
Edit
> What are the benefits of Triphala in gut health?
The agent will:

Search PubMed

Filter Ayurvedic results

Summarize and return key findings

🌐 Optional: Run with Agent-UI (Frontend)
Agno provides an open-source Agent-UI to integrate your agent into a web interface.

To enable UI:
Uncomment the following lines in your Agent.py:

python
Copy
Edit
# playground = Playground(agents=[agent])
# app = playground.get_app()

# if __name__ == "__main__":
#     playground.serve("Agent:app", reload=True)
Run the agent with:

bash
Copy
Edit
python Agent.py
The app will start at http://localhost:8000

You’ll get:

A chat interface for user queries

Summarized research outputs

Debug reasoning logs (if enabled)

🧠 Agent Behavior Instructions
The agent uses the following rule set:

✅ Include papers mentioning Ayurveda, herbs, Panchakarma, etc.

❌ Exclude papers about modern or allopathic medicine (e.g., antibiotics).

🔍 Provide structured, markdown-friendly summaries.

🧩 Log reasoning steps and tool calls for transparency.

⚠️ Troubleshooting
503 Gemini Model Error?
This can happen when Gemini API is overloaded. Retry after a few minutes, or switch to OpenAI's GPT-4 temporarily.

No results returned?
Check that your query contains Ayurvedic terms. The agent filters out irrelevant medical content.

📂 Folder Structure
bash
Copy
Edit
.
├── Agent.py
├── .env
├── README.md
└── requirements.txt
📌 Credits
Built with:

Agno SDK

Google Gemini

PubMed API

Pydantic for structured outputs

🧪 Future Improvements
Plug in real PubMed API instead of Agno stub

Add Ayurvedic keyword whitelist from curated JSON

Multi-paper summarization with confidence scoring

Integrate with FastAPI backend and deploy to cloud

Feel free to fork, improve, or integrate into your research workflows!

yaml
Copy
Edit
