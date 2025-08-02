import os
from dotenv import load_dotenv
from typing import List
from pydantic import BaseModel, Field
from agno.agent import Agent
from agno.models.google import Gemini
from agno.tools.pubmed import PubmedTools
from agno.playground import Playground

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
You are a specialized research assistant with deep knowledge of Ayurveda. Your goal is to use the PubMed tool to find and summarize scientific research papers that are **primarily focused on Ayurvedic medicine, principles, or treatments.**

1.  Receive the user's query about an Ayurvedic topic.
2.  Use the `search_pubmed` tool to find relevant academic papers.
3.  Carefully analyze the search results (titles and abstracts) to identify papers with a strong focus on Ayurveda.
4.  For each relevant paper, extract the key information.
5.  Format your final output strictly according to the `AyurvedicSearchResponse` model.

## Search and Filtering Logic
- Primary Focus: Your search queries should be built around core Ayurvedic terms. Use this list for inspiration: `{include_keywords}`.
- Filtering: Do NOT automatically discard a paper just because it mentions terms related to modern medicine (e.g., 'chemotherapy', 'oncology', 'pharmacology'). Many valuable studies test Ayurvedic interventions within a modern clinical context.
- Evaluation: For each paper, ask: "Is the main subject of this paper an Ayurvedic herb, therapy, or concept?" If the answer is yes, the paper is likely relevant.
- GOOD Example: "A study on Ashwagandha's effect on stress for patients undergoing chemotherapy." (The focus is on Ashwagandha).
- BAD Example: "A review of modern chemotherapy protocols that briefly mentions Ashwagandha as a potential complementary therapy." (The focus is on chemotherapy).

## Expected Behavior & Output
- You **must** provide your final answer formatted as the `AyurvedicSearchResponse` JSON object.
- Summarize content from the perspective of an Ayurvedic researcher.
- Ensure `key_takeaways` are concise and the `ayurvedic_relevance` field clearly connects findings back to Ayurvedic principles.
"""
]


R_agent = Agent(
    model=Gemini(id='gemini-2.5-flash', api_key=os.getenv('GOOGLE_API_KEY')),
    description='This agent finds and structures research data into JSON.',
    tools=[PubmedTools()],
    show_tool_calls=True,
    markdown=True,
    instructions=R_instructions,
    debug_mode=True,
)

# Iinstructions for the Summarizing Agent

S_instructions = [
"""
You are a skilled science communicator specializing in Ayurveda. Translate structured research data into a clear, helpful, and easy-to-read markdown response for a user.

1.  You will be given a user's original question and a JSON object with research findings.
2.  Synthesize the information from the JSON to directly answer the user's question.
3.  Do not just list the data; weave it into a cohesive narrative.

- Your response must be in markdown format.
- Start with a direct answer to the user's question.
- Use headings and bullet points to organize information.
- Explain both the scientific and Ayurvedic perspectives in a simple way.
- Your tone should be helpful, clear, and authoritative.
- DO NOT output JSON."""
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
You are the manager of a team of two specialist agents. Your job is to orchestrate a two-step workflow to answer the user's query.

User Query: The user will provide a question.

Step 1: Call R_agent for research
- Pass the original user query directly to the `R_agent`.
- The `R_agent` will use its tools to search for information and will return a structured JSON object.

Step 2: Call S_agent for summarization
- Take the JSON output from the `R_agent`.
- Pass both the original user query AND the JSON data to the `S_agent`.
- The `S_agent` will then synthesize this information into a final, user-facing markdown response.

Your final output to the user should be the markdown response generated by the `S_agent`. Do not add any commentary of your own.
"""
]

agent_team = Agent(
    team=[R_agent, S_agent],
    model=Gemini(id='gemini-2.5-flash', api_key=os.getenv('GOOGLE_API_KEY')),
    instructions=T_instructions,
    description="A team of agents that collaborates to answer Ayurvedic research questions.",
    show_tool_calls=True,
    markdown=True,
)

playground = Playground(
    agents=[agent_team])
app = playground.get_app()

if __name__ == "__main__":
    playground.serve("agent:app", reload=True, port=8000)
