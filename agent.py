from agno.agent import Agent
from agno.models.google import Gemini
from agno.tools.pubmed import PubmedTools
from agno.playground import Playground

import os
from dotenv import load_dotenv 

load_dotenv() 

include_keywords = [
    "ayurveda", "ayurvedic", "triphala", "ashwagandha", "turmeric",
    "panchakarma", "dosha", "vata", "pitta", "kapha",
    "rasayana", "herbal remedy", "natural remedy", "brahmi", "tulsi"
]

exclude_keywords = [
    "antibiotic", "chemotherapy", "radiotherapy", "antiviral", "vaccine",
    "corticosteroids", "ibuprofen", "antidepressant", "metformin", "placebo-controlled",
    "oncology", "radiation", "pharmaceutical", "prescription drugs"
]

instructions = [
f"""
You are an ayurveda supporter. You only process Ayurveda-related results.
Use all the tools provided to you to search pubmed to find research papers related to Ayurveda.
Look for keywords like {include_keywords},
Ignore general and modern medicine content like {exclude_keywords}.
Provide a summary of the Ayurveda-related content found in the research papers.
Highlight key takeaways, research results, and practical relevance to Ayurveda."""
]

Ayurvedic_expert_agent = Agent(
    model=Gemini(id='gemini-2.5-flash', api_key=os.getenv('GOOGLE_API_KEY')),
    description='An agent that checks research papers on PubMed and answers questions.',
    tools=[PubmedTools(max_results=5)],
    show_tool_calls=True,         
    markdown=True,  
    instructions=instructions,
    debug_mode=True,
)

playground = Playground(
    agents=[Ayurvedic_expert_agent])
app = playground.get_app()

if __name__ == "__main__":
    playground.serve("agent:app", reload=True)
