# Ayurveda Research Agent using Agno

An intelligent AI Agent that searches Ayurvedic research papers from **PubMed** and summarizes the results. Powered by **Google Gemini** via Agno's framework, the agent leverages PubMed tools with custom logic for relevance, filtering, and structured output.

---
## Demo
<img width="1918" height="822" alt="Image" src="https://github.com/user-attachments/assets/2d89c0d6-2512-4d4a-b88f-89d47df659af" />
<img width="1912" height="853" alt="Image" src="https://github.com/user-attachments/assets/855af7d3-0e2f-4217-b161-cc24bca4f26a" />
<img width="1914" height="822" alt="Image" src="https://github.com/user-attachments/assets/0ede7d9c-398d-44c2-a076-7b9621fbaf5b" />
<img width="1913" height="679" alt="Image" src="https://github.com/user-attachments/assets/171d64b3-c8f8-4d8a-a0b1-5600ce16ade5" />

## Project Overview

This agent allows users to query PubMed in **natural language** (e.g., “Is Ashwagandha effective for anxiety?”), and returns papers relevant to Ayurveda.

### Core Features

- PubMed search using Agno’s `PubmedTools`
- Ayurveda-focused filtering logic
- Summarization of research papers
- Debug mode to show tool usage & reasoning
- Agent-UI frontend

---

## Purpose

My aim is to build a focused, transparent, and user-friendly research assistant that provides **evidence-based insights from PubMed research papers** for traditional Ayurvedic medicine topics.

---

## How to Run the Agent Locally

### 1. Clone the Repository

```
git clone https://github.com/your-username/ayurveda-research-agent.git
cd ayurveda-research-agent
```
### 2. Set Up Python Environment
Create and activate a virtual environment:
```
python -m venv venv
venv\Scripts\activate
```
### 3. Install Dependencies
```
pip install -r requirements.txt
```
## API Key Setup
### 4. Create .env File
In the project root directory, create a .env file like the .example.env file:
```
GOOGLE_API_KEY=your_gemini_api_key_here
```

## Setting up the Agent-UI
To setup the Agent's UI, run the following command in your terminal:
```
npx create-agent-ui@latest
```
Enter y to create a new project, install dependencies, then run the agent-ui using:
```
cd agent-ui && npm run dev
```
Open `http://localhost:3000` to view the Agent UI, but remember to connect to the local agent.
## Connecting the Ayurveda agent
The Agent UI needs to connect to a playground server, which you can do by locally running the agent file using
```
python Agent.py
```
## The Interface
Head to `http://localhost:3000/`
You’ll be prompted to enter a natural language query.
Example:
```
> I have digestive issues after meals - what can help?
```
The agent will:
* Search PubMed
* Filter Ayurvedic results
* Summarize and return key findings

## 📂 Folder Structure
```
📂 Folder/
├── Agent.py              
├── .env                 
├── README.md            
├── requirements.txt      
```
## Built with:
* Agno SDK
* Google Gemini
* PubMed API

## Troubleshooting
503 Gemini Model Error?
This can happen when Gemini API is overloaded. Retry after a few minutes, or switch to OpenAI's GPT-4 temporarily.
