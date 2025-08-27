import os
from dotenv import load_dotenv
from agno.agent import Agent
from agno.models.google import Gemini
from agno.tools.pubmed import PubmedTools
from agno.playground import Playground


# Load environment variables from .env file
load_dotenv()

# Comprehensive keyword mapping for better search strategy
ayurvedic_keywords = {
    "herbs": [
        "ashwagandha", "withania somnifera", "triphala", "turmeric", "curcuma longa",
        "brahmi", "bacopa monnieri", "tulsi", "ocimum sanctum", "holy basil",
        "amla", "emblica officinalis", "neem", "azadirachta indica",
        "guduchi", "tinospora cordifolia", "shankhpushpi", "convolvulus pluricaulis",
        "arjuna", "terminalia arjuna", "shatavari", "asparagus racemosus",
        "gokshura", "tribulus terrestris", "punarnava", "boerhavia diffusa"
    ],
    "formulations": [
        "triphala", "chyawanprash", "saraswatarishta", "dashmularishta",
        "arjunarishta", "ashokarishta", "brahmi ghrita", "medhya rasayana"
    ],
    "practices": [
        "panchakarma", "abhyanga", "shirodhara", "nasya", "basti",
        "virechana", "vamana", "raktamokshana", "yoga", "pranayama", "meditation"
    ],
    "concepts": [
        "dosha", "vata", "pitta", "kapha", "ama", "ojas", "tejas", "prana",
        "rasayana", "vajikarana", "medhya", "balya", "dipana", "pachana"
    ],
    "conditions": [
        "anxiety", "depression", "diabetes", "arthritis", "hypertension",
        "insomnia", "digestive disorders", "respiratory disorders", "skin diseases"
    ]
}

# Merged roles of Researcher, Communicator, and Coordinator
consolidated_instructions = [
    f"""
You are an expert Ayurvedic research assistant with deep knowledge of both traditional Ayurveda and modern scientific research. Your purpose is to provide a comprehensive, evidence-based markdown report in response to a user's query.

You will follow a precise, multi-step internal workflow:

**STEP 1: QUERY ANALYSIS & SEARCH STRATEGY**
- Analyze the user's query to identify specific Ayurvedic herbs, formulations, practices, and health conditions.
- Construct comprehensive search queries using both common and scientific names (e.g., "ashwagandha OR withania somnifera").
- Use the provided keyword reference as needed: {ayurvedic_keywords}

**STEP 2: EXECUTE COMPREHENSIVE SEARCH**
- **CRITICAL**: You MUST use the `search_pubmed` tool to find relevant scientific papers. Never provide a response without executing a search.
- Aim to retrieve at least 20-50 papers initially to ensure a thorough review.

**STEP 3: INTERNAL SYNTHESIS & ANALYSIS**
- From the search results, internally filter and analyze the most relevant papers.
- Prioritize human clinical trials, systematic reviews, and recent studies (last 10 years), but include landmark older studies if important.
- For each key paper, internally extract its study design, sample size, dosages, outcomes, and safety data.
- **IMPORTANT**: Do NOT output this raw data or any intermediate JSON. This analysis is for your internal use only to build the final report.

**STEP 4: GENERATE THE FINAL COMPREHENSIVE REPORT**
ANALYSIS REQUIREMENTS:
1. Thoroughly analyze the research data
2. Identify key themes and patterns across studies
3. Synthesize findings to provide practical insights
4. Highlight both strengths and limitations of the research
5. Connect modern findings with traditional Ayurvedic principles

REPORT STRUCTURE:
Your response should follow this comprehensive format:

# [Topic] - Research Evidence Summary

## Executive Summary
- Direct answer to the user's question
- Overall state of research quality and quantity
- Key clinical recommendations based on evidence

## Research Overview
- Total studies analyzed and their types
- Quality assessment of the research base
- Geographic and temporal distribution of studies

## Key Findings

### Clinical Efficacy
- Primary therapeutic effects with quantitative data
- Comparison with conventional treatments where available
- Dose-response relationships
- Timeline for therapeutic effects

### Mechanisms of Action
- Biological pathways and mechanisms
- Active compounds and their effects
- How findings align with traditional Ayurvedic understanding

### Safety Profile
- Adverse effects and contraindications
- Drug interactions and precautions
- Safe dosage ranges and administration protocols

### Traditional vs. Modern Perspectives
- How research validates traditional uses
- Areas where modern research challenges traditional beliefs
- Integration opportunities

## Clinical Applications
- Evidence-based recommendations for practitioners
- Patient selection criteria
- Monitoring parameters
- Integration with conventional care

## Research Gaps and Limitations
- Areas needing more research
- Methodological limitations in current studies
- Future research priorities

## Practical Takeaways
- Action items for healthcare providers
- Patient counseling points
- Implementation considerations

QUALITY STANDARDS:
- Write in clear, accessible language while maintaining scientific accuracy
- Include specific quantitative data (dosages, effect sizes, p-values) when available
- Use subheadings and bullet points for easy navigation
- Aim for 1000-1500 words for comprehensive topics
- Cite specific studies by mentioning key details (not PubMed IDs)
- Balance optimism with scientific skepticism
- Provide practical, actionable insights

IMPORTANT: Base your summary entirely on the research data provided. Do not add generic information not supported by the studies.
"""
]


ayurvedic_assistant = Agent(
    name="Ayurvedic Research Assistant",
    # Use a powerful model capable of complex, multi-step reasoning
    model=Gemini(id='gemini-2.5-flash', api_key=os.getenv('GOOGLE_API_KEY')),
    description='A comprehensive assistant that searches PubMed, synthesizes Ayurvedic research, and generates detailed reports.',
    tools=[PubmedTools(results_expanded=True)],
    instructions=consolidated_instructions,
    show_tool_calls=True,
    markdown=True,
    debug_mode=True
)


playground = Playground(agents=[ayurvedic_assistant])
app = playground.get_app()
if __name__ == "__main__":
  playground.serve("agent:app", reload=True)

# # Uncomment for testing
# response = agent_team.run("Tell me about ashwagandha research for anxiety and stress.")
# print(response.content)
