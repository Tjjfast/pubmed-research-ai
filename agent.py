import os
from dotenv import load_dotenv
from typing import List, Optional
from pydantic import BaseModel, Field
from agno.agent import Agent
from agno.models.google import Gemini
from agno.tools.pubmed import PubmedTools
from agno.team import Team
# import streamlit as st
import json
from agno.playground import Playground
# Load environment variables from .env file
load_dotenv()

# Define the structure for a single research paper summary using pydantic.
class ResearchPaper(BaseModel):
    pubmed_id: str = Field(..., description="The PubMed ID of the research paper.")
    title: str = Field(..., description="The title of the research paper.")
    summary: str = Field(..., description="A detailed summary of the paper's abstract and methodology, focusing on its relevance to Ayurveda.")
    key_takeaways: List[str] = Field(..., description="5-8 specific bullet points highlighting the key findings, dosages, mechanisms, and clinical results.")
    ayurvedic_relevance: str = Field(..., description="Detailed explanation of how this research validates or challenges traditional Ayurvedic principles.")
    study_type: str = Field(..., description="Type of study (clinical trial, systematic review, in-vitro, animal study, etc.)")
    sample_size: Optional[str] = Field(None, description="Number of participants or sample size if mentioned")

# Define the overall response 
class AyurvedicSearchResponse(BaseModel):
    query_interpretation: str = Field(..., description="How you interpreted the user's query")
    search_strategy: str = Field(..., description="The search terms and strategy used")
    total_papers_found: int = Field(..., description="Total number of papers found")
    papers: List[ResearchPaper] = Field(..., description="A list of curated Ayurvedic research papers found on PubMed.")

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

# Enhanced instructions for the Research Agent
R_instructions = [
    f"""
You are an expert Ayurvedic research specialist with deep knowledge of both traditional Ayurveda and modern scientific research. Your primary task is to search PubMed comprehensively and return detailed, structured summaries of relevant research.

CRITICAL: YOU MUST ALWAYS USE THE search_pubmed TOOL FOR EVERY QUERY. Never provide generic responses without searching.

SEARCH STRATEGY:
1. Analyze the user's query to identify:
   - Specific Ayurvedic herbs, formulations, or practices mentioned
   - Health conditions or therapeutic areas
   - Any specific research aspects (efficacy, safety, mechanisms)

2. Construct comprehensive search queries using these guidelines:
   - Use both common names AND scientific names (e.g., "ashwagandha OR withania somnifera")
   - Include relevant synonyms and related terms
   - Use multiple search iterations with different keyword combinations
   - Search for at least 20-50 papers initially to ensure comprehensive coverage

3. Keyword reference (use as needed): {ayurvedic_keywords}

PAPER EVALUATION CRITERIA:
Include papers that:
- Study Ayurvedic herbs, formulations, or practices as primary interventions
- Investigate traditional Ayurvedic principles using modern research methods
- Examine mechanisms of action of Ayurvedic treatments
- Compare Ayurvedic treatments with conventional therapies
- Analyze safety and efficacy of Ayurvedic interventions

Exclude papers that:
- Only mention Ayurveda in passing without substantial investigation
- Focus primarily on non-Ayurvedic treatments with minimal Ayurvedic content
- Are purely theoretical without empirical data

DETAILED EXTRACTION REQUIREMENTS:
For each relevant paper, extract:
- Complete bibliographic information
- Study design and methodology
- Sample size and demographics
- Specific dosages, preparations, and protocols used
- Primary and secondary outcomes
- Statistical significance and effect sizes
- Safety data and adverse effects
- Mechanistic insights
- Clinical implications
- Limitations acknowledged by authors

OUTPUT REQUIREMENTS:
1. Provide query_interpretation explaining how you understood the request
2. Detail your search_strategy including specific terms used
3. Report total_papers_found from your search
4. For each paper, provide:
   - Comprehensive summary (150-200 words minimum)
   - 5-8 specific key_takeaways with quantitative data when available
   - Detailed ayurvedic_relevance connecting findings to traditional principles
   - Study type and sample size

QUALITY STANDARDS:
- Prioritize recent studies (last 10 years) but include landmark older studies
- Focus on human clinical trials and systematic reviews when available
- Include diverse study types (RCTs, observational studies, mechanistic studies)
- Ensure summaries are detailed and informative, not generic
- Provide specific, actionable insights

Return results in the exact AyurvedicSearchResponse JSON format. If no relevant papers are found after thorough searching, return papers as empty list but explain your search strategy.
"""
]
Research_agent = Agent(
    name="Research Agent",
    model=Gemini(id='gemini-2.5-pro', api_key=os.getenv('GOOGLE_API_KEY')),
    description='Expert Ayurvedic research agent that comprehensively searches and analyzes PubMed literature.',
    tools=[PubmedTools(results_expanded=True)],
    show_tool_calls=True,
    markdown=True,
    instructions=R_instructions,
    response_model=AyurvedicSearchResponse,
    parser_model=Gemini(id='gemini-2.5-flash-lite', api_key=os.getenv('GOOGLE_API_KEY')),    
    read_tool_call_history=True,
    debug_mode=True,
      # Allow multiple tool calls if needed
)

# Enhanced instructions for the Summarizing Agent
S_instructions = [
"""
You are an expert science communicator specializing in Ayurvedic research. Your task is to transform structured research data into comprehensive, practical, and engaging markdown reports.

ANALYSIS REQUIREMENTS:
1. Thoroughly analyze the research data provided
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

Communicator_agent = Agent(
    name="Science Communicator",
    model=Gemini(id='gemini-2.5-pro', api_key=os.getenv('GOOGLE_API_KEY')),  # Using Pro for better summarization
    description='Expert science communicator specializing in comprehensive Ayurvedic research synthesis.',
    markdown=True,
    instructions=S_instructions,
    debug_mode=True,
)

# Enhanced instructions for the Team Coordinator
T_instructions = [
"""
You are the coordinator of a specialized Ayurvedic research team. Your role is to ensure high-quality, comprehensive responses to user queries about Ayurvedic research.

WORKFLOW MANAGEMENT:
1. Receive and analyze the user's query for clarity and completeness
2. Pass the query to Research Agent with clear expectations for comprehensive searching
3. Validate that Research Agent has actually used the search tool and found relevant papers
4. If Research Agent returns empty results or generic responses, request a more thorough search
5. Pass both the original query and the structured research data to Communicator
6. Ensure Communicator provides a comprehensive, detailed summary

QUALITY CONTROL:
- Verify that actual PubMed searches were performed
- Ensure responses contain specific, detailed research findings
- Check that summaries are comprehensive (not just 2-4 bullet points)
- Validate that traditional Ayurvedic principles are properly connected to modern research

ERROR HANDLING:
- If Research Agent encounters search errors, request retry with alternative search terms
- If responses are too generic, request more specific and detailed analysis
- Ensure final output meets high standards for depth and practical utility

OUTPUT REQUIREMENTS:
Your final response should be the complete markdown summary from Communicator agent, ensuring it:
- Directly addresses the user's question
- Contains detailed research findings with quantitative data
- Provides practical clinical insights
- Is comprehensive and well-structured
- Connects traditional and modern perspectives

Do not include intermediate JSON outputs or technical details in the final response.
"""
]

agent_team = Team(
    members= [Research_agent, Communicator_agent],
    model=Gemini(id='gemini-2.5-pro', api_key=os.getenv('GOOGLE_API_KEY')),
    instructions=T_instructions,
    description="A specialized team that provides comprehensive, evidence-based answers to Ayurvedic research questions.",
    show_tool_calls=True,
    read_team_history=True,
    
    markdown=True,
)
playground = Playground(teams=[agent_team])
app = playground.get_app()
if __name__ == "__main__":
    playground.serve("pubmed_agent_test:app", reload=True)
# # Enhanced Streamlit Interface
# st.set_page_config(
#     page_title="Ayurvedic Research Assistant", 
#     layout="wide",
#     initial_sidebar_state="expanded"
# )

# st.title("🌿 Ayurvedic Research Assistant")
# st.markdown("*Evidence-based insights from traditional Ayurvedic medicine*")

# # Sidebar with example queries and tips
# with st.sidebar:
#     st.header("💡 Example Queries")
#     example_queries = [
#         "What does research say about ashwagandha for anxiety?",
#         "Clinical evidence for triphala in digestive health",
#         "Turmeric and curcumin research for inflammation",
#         "Panchakarma effectiveness in modern studies",
#         "Safety profile of brahmi in cognitive enhancement",
#         "Comparative studies of Ayurvedic vs conventional diabetes treatments"
#     ]
    
#     for query in example_queries:
#         if st.button(query, key=f"example_{hash(query)}"):
#             st.session_state.query = query

#     st.header("🔍 Search Tips")
#     st.markdown("""
#     - Be specific about herbs, conditions, or practices
#     - Ask about safety, efficacy, or mechanisms
#     - Include context like "clinical trials" or "systematic review"
#     - Mention specific populations (elderly, children, etc.)
#     """)

# # Main interface
# query = st.text_input(
#     "Ask me about Ayurvedic research:", 
#     value=st.session_state.get('query', ''),
#     placeholder="e.g., What does research say about ashwagandha for stress and anxiety?"
# )

# col1, col2 = st.columns([1, 4])
# with col1:
#     search_button = st.button("🔍 Search Research", type="primary")
# with col2:
#     if st.button("🔄 Clear"):
#         st.session_state.query = ""
#         st.rerun()

# if search_button and query.strip():
#     with st.spinner("🔍 Searching PubMed for relevant Ayurvedic research..."):
#         try:
#             # Add progress indicators
#             progress_bar = st.progress(0)
#             status_text = st.empty()
            
#             status_text.text("Analyzing your query...")
#             progress_bar.progress(20)
            
#             status_text.text("Searching PubMed database...")
#             progress_bar.progress(40)
            
#             status_text.text("Evaluating research papers...")
#             progress_bar.progress(60)
            
#             status_text.text("Synthesizing findings...")
#             progress_bar.progress(80)
            
#             response = agent_team.run(query)
            
#             progress_bar.progress(100)
#             status_text.text("Research analysis complete!")
            
#             # Clear progress indicators
#             progress_bar.empty()
#             status_text.empty()
            
#             # Display results
#             if hasattr(response, 'content') and response.content:
#                 st.markdown("---")
#                 st.markdown(response.content)
#             else:
#                 st.warning("I couldn't find specific research on this topic. Please try rephrasing your query or asking about a different Ayurvedic topic.")
                
#         except Exception as e:
#             st.error(f"An error occurred while searching: {str(e)}")
#             st.info("Please try rephrasing your query or check your internet connection.")

# # Footer with additional information
# st.markdown("---")
# st.markdown("""
# <div style='text-align: center; color: #666; font-size: 0.8em;'>
# <p>This tool searches PubMed for peer-reviewed research on Ayurvedic medicine. Results are for educational purposes only and should not replace professional medical advice.</p>
# </div>
# """, unsafe_allow_html=True)

# # Uncomment for testing
# # response = agent_team.run("Tell me about ashwagandha research for anxiety and stress.")
# # print(response.content)
