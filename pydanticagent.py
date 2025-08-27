import os
from dotenv import load_dotenv
from typing import List, Optional
from pydantic import BaseModel, Field
from agno.agent import Agent
from agno.models.google import Gemini
from agno.tools.pubmed import PubmedTools

import streamlit as st

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

# Enhanced instructions for the Agent
consolidated_instructions = [
f"""
You are an expert Ayurvedic research specialist with deep knowledge of both traditional Ayurveda and modern scientific research. Your task is to search PubMed comprehensively, structure the findings according to the AyurvedicSearchResponse model, and then transform that data into a comprehensive markdown report.

# WORKFLOW: TWO-PHASE PROCESS

## PHASE 1: RESEARCH COLLECTION & STRUCTURING

CRITICAL: YOU MUST ALWAYS USE THE search_pubmed TOOL FOR EVERY QUERY. Never provide generic responses without searching.

SEARCH STRATEGY:
1. Analyze the user's query to identify:
   - Specific Ayurvedic herbs, formulations, or practices mentioned
   - Health conditions or therapeutic areas
   - Any specific research aspects (efficacy, safety, mechanisms)

2. Construct comprehensive search queries using these guidelines:
   - Use both common names AND scientific names (e.g., "ashwagandha OR withania somnifera"), use ayurvedic_keywords dictionary for reference
   - Include relevant synonyms and related terms
   - Use multiple search iterations with different keyword combinations
   - Search for at least 20-50 papers initially to ensure comprehensive coverage

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

STRUCTURED OUTPUT REQUIREMENTS:
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

## PHASE 2: COMPREHENSIVE MARKDOWN REPORT

Transform the structured research data into a comprehensive, practical, and engaging markdown report.

ANALYSIS REQUIREMENTS:
1. Thoroughly analyze the research data from Phase 1
2. Identify key themes and patterns across studies
3. Synthesize findings to provide practical insightsx   
4. Highlight both strengths and limitations of the research
5. Connect modern findings with traditional Ayurvedic principles

REPORT STRUCTURE:

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

FINAL OUTPUT FORMAT

Your complete response should contain:

1. First, present the structured JSON data in the AyurvedicSearchResponse format
2. Then, provide the comprehensive markdown report based on that data

# QUALITY CONTROL REQUIREMENTS

- Verify that actual PubMed searches were performed
- Ensure responses contain specific, detailed research findings
- Check that summaries are comprehensive (not just 2-4 bullet points)
- Validate that traditional Ayurvedic principles are properly connected to modern research
- Ensure final output directly addresses the user's question
- Contains detailed research findings with quantitative data
- Provides practical clinical insights
- Is comprehensive and well-structured
- Connects traditional and modern perspectives

If no relevant papers are found after thorough searching, explain your search strategy and return papers as empty list in the JSON format, then provide an explanation in the markdown report.
"""
]


ayurvedic_assistant = Agent(
    name="Ayurvedic Research Assistant",
    model=Gemini(id='gemini-2.5-pro', api_key=os.getenv('GOOGLE_API_KEY')),
    description='A comprehensive assistant that searches PubMed, synthesizes Ayurvedic research, and generates detailed reports.',
    tools=[PubmedTools(results_expanded=True)],
    instructions=consolidated_instructions,
    show_tool_calls=True,
    markdown=True,
    debug_mode=True
)

# Streamlit
st.set_page_config(
    page_title="Ayurvedic Research Assistant", 
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🌿 Ayurvedic Research Assistant")
st.markdown("*Evidence-based insights from traditional Ayurvedic medicine*")

# Sidebar with example queries and tips
with st.sidebar:
    st.header("💡 Example Queries")
    example_queries = [
        "What does research say about ashwagandha for anxiety?",
        "Clinical evidence for triphala in digestive health",
        "Turmeric and curcumin research for inflammation",
        "Panchakarma effectiveness in modern studies",
        "Safety profile of brahmi in cognitive enhancement",
        "Comparative studies of Ayurvedic vs conventional diabetes treatments"
    ]
    
    for query in example_queries:
        if st.button(query, key=f"example_{hash(query)}"):
            st.session_state.query = query

    st.header("🔍 Search Tips")
    st.markdown("""
    - Be specific about herbs, conditions, or practices
    - Ask about safety, efficacy, or mechanisms
    - Include context like "clinical trials" or "systematic review"
    - Mention specific populations (elderly, children, etc.)
    """)

# Main interface
query = st.text_input(
    "Ask me about Ayurvedic research:", 
    value=st.session_state.get('query', ''),
    placeholder="e.g., What does research say about ashwagandha for stress and anxiety?"
)

col1, col2 = st.columns([1, 4])
with col1:
    search_button = st.button("🔍 Search Research", type="primary")
with col2:
    if st.button("🔄 Clear"):
        st.session_state.query = ""
        st.rerun()

if search_button and query.strip():
    with st.spinner("🔍 Searching PubMed, analyzing papers, and compiling your report..."):
        try:
            status_text = st.empty()
            status_text.text("Executing a multi-step research and analysis process...")
            
            response = ayurvedic_assistant.run(query)
            
            status_text.text("Research analysis complete!")
            
            if hasattr(response, 'content') and response.content:
                st.markdown("---")
                st.markdown(response.content)
            else:
                st.warning("I couldn't find specific research on this topic. Please try rephrasing your query or asking about a different Ayurvedic topic.")
                
        except Exception as e:
            st.error(f"An error occurred while searching: {str(e)}")
            st.info("Please try rephrasing your query or check your internet connection.")

st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; font-size: 0.8em;'>
<p>This tool searches PubMed for peer-reviewed research on Ayurvedic medicine. Results are for educational purposes only and should not replace professional medical advice.</p>
</div>
""", unsafe_allow_html=True)

# # Uncomment for testing
# response = agent_team.run("Tell me about ashwagandha research for anxiety and stress.")
# print(response.content)
