import os
from dotenv import load_dotenv
from typing import List
from pydantic import BaseModel, Field
from agno.agent import Agent
from agno.models.google import Gemini
from agno.tools.pubmed import PubmedTools
from agno.team import Team
import streamlit as st

# Load environment variables from .env file
load_dotenv()

# Define the structure for a single research paper summary using pydantic.
class ResearchPaper(BaseModel):
    pubmed_id: str = Field(..., description="The PubMed ID of the research paper.")
    title: str = Field(..., description="The title of the research paper.")
    summary: str = Field(..., description="A concise summary of the paper's abstract, focusing on its relevance to Ayurveda.")
    key_takeaways: List[str] = Field(..., description="A list of bullet points highlighting the key findings and results.")
    ayurvedic_relevance: str = Field(..., description="An explanation of the paper's practical relevance to Ayurvedic principles or practices.")

# Define the overall response 
class AyurvedicSearchResponse(BaseModel):
    papers: List[ResearchPaper] = Field(..., description="A list of curated Ayurvedic research papers found on PubMed.")

# Keywords for guiding the agent
include_keywords = [
    "ayurveda", "ayurvedic", "triphala", "ashwagandha", "turmeric",
    "panchakarma", "dosha", "vata", "pitta", "kapha",
    "rasayana", "herbal remedy", "natural remedy", "brahmi", "tulsi"
]

# Iinstructions for the Research Agent
R_instructions = [
    f"""
You are an expert Ayurvedic research agent. Your job is to search PubMed using the provided query, identify Ayurveda-relevant papers, and return structured summaries in a precise format.

Chain of Thought:
1. Understand the user's query and determine the Ayurvedic concept(s) or herbs involved.
2. Use the search_pubmed tool with a relevant keyword-based query.
3. For each paper returned:
   - Read the title and abstract carefully.
   - Ask yourself: "Is the core subject Ayurvedic in nature?"
   - If yes, extract useful information and summarize it.
   - If no, skip it.
4. Format each accepted paper using the `ResearchPaper` model.

Filtering Rules:
- Include papers that study Ayurvedic treatments (e.g., Ashwagandha, Triphala, Panchakarma).
- Do NOT exclude a paper just because it contains modern terms (e.g., "chemotherapy").
- Allow modern terms if the Ayurvedic element is the study's main focus.
- Use this Ayurvedic keyword guide (not strict): {include_keywords}

Few-Shot Format Example:
Return results in this exact JSON structure:

{{
  "papers": [
    {{
      "pubmed_id": "12345678",
      "title": "Effect of Triphala on Gut Health",
      "summary": "This study investigates the impact of Triphala on gut microbiota...",
      "key_takeaways": [
        "Triphala improved microbial diversity",
        "Reduced inflammation markers",
        "No major side effects reported"
      ],
      "ayurvedic_relevance": "Validates Triphala’s traditional use for digestive balancing in Ayurvedic practice."
    }}
  ]
}}

Output Format:
- Return only valid JSON matching the AyurvedicSearchResponse schema.
- Do not explain your reasoning in the output.
- If no relevant papers are found, return: {{ "papers": [] }}

Finally:
- Think carefully.
- Be selective and structured.
- Be accurate and concise.
"""
]


R_agent = Agent(
    model=Gemini(id='gemini-2.5-pro', api_key=os.getenv('GOOGLE_API_KEY')),
    description='This agent finds and structures research data into JSON.',
    tools=[PubmedTools()],
    show_tool_calls=True,
    markdown=True,
    instructions=R_instructions,
    response_model=AyurvedicSearchResponse,
    parser_model=Gemini(id='gemini-2.5-flash', api_key=os.getenv('GOOGLE_API_KEY')),    
    debug_mode=True,
)

# Iinstructions for the Summarizing Agent

S_instructions = [
"""
You are a science communicator and Ayurveda expert. Your task is to write a clear, helpful, markdown summary based on structured research data.

Step-by-Step Instructions:
1. Read the user's original question and the structured research data (JSON).
2. Understand the Ayurvedic topic being asked about.
3. Identify the most relevant insights across papers.
4. Write a user-friendly markdown response that:
   - Starts with a direct answer.
   - Groups findings with headings and bullet points.
   - Highlights Ayurvedic principles and modern findings clearly.
   - Avoids repeating raw data or JSON format.
"""
]

S_agent = Agent(
    model=Gemini(id='gemini-2.5-flash', api_key=os.getenv('GOOGLE_API_KEY')),
    description='This agent creates user-friendly markdown summaries from structured data.',
    markdown=True,
    instructions=S_instructions,
    debug_mode=True,
)

# Iinstructions for the Team Agent

T_instructions = [
"""
Your Role :
You are a coordinator that manages two specialist agents:  
- R_agent: Responsible for retrieving and structuring Ayurvedic research from PubMed.  
- S_agent: Responsible for converting structured research data into user-friendly markdown summaries.

Task Flow :
1. Receive a user's query related to Ayurveda.
2. Pass the raw query unchanged to the R_agent.
3. Wait for the R_agent to return a response in AyurvedicSearchResponse (JSON) format.
4. Verify that the JSON is structured (e.g., contains a papers list).
5. Pass both the original query and the JSON output to the S_agent.
6. Let S_agent synthesize and return a well-structured markdown answer.

Output Format :
Your final response should be only the markdown generated by the S_agent.  
- Do not add your own text, interpretation, or explanation.  
- Do not reformat the output.  
- Do not include intermediate results or JSON.

Example Workflow :
- Input: "Does Ashwagandha help with anxiety?"
- R_agent returns structured JSON of studies mentioning Ashwagandha.
- S_agent returns a summary in markdown format.
"""
]

agent_team = Team(
    members=[R_agent, S_agent],
    model=Gemini(id='gemini-2.5-flash', api_key=os.getenv('GOOGLE_API_KEY')),
    instructions=T_instructions,
    description="A team of agents that collaborates to answer Ayurvedic research questions.",
    show_tool_calls=True,
    markdown=True,
)

# Streamlit

st.set_page_config(page_title="Ayurvedic Research Agent", layout="wide")
st.title("Ayurvedic Research Assistant")

query = st.text_input("Ask me a question :", "")

if st.button("Search") and query.strip():
    with st.spinner("Searching PubMed for Ayurvedic research..."):
        try:
            response = agent_team.run(query).content
            st.markdown(response)
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")

# agent_team.print_response("Tell me about ulcerative colitis.")
