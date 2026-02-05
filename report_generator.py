"""
report_generator.py
Generates the specific MBFC-style prose report using LLM synthesis.
"""

from langchain_openai import ChatOpenAI
from schemas import ComprehensiveReportData

class ReportGenerator:
    def __init__(self, model: str = "gpt-4o", temperature: float = 0.4):
        self.llm = ChatOpenAI(model=model, temperature=temperature)

    def generate(self, data: ComprehensiveReportData) -> str:
        """
        Synthesizes the ComprehensiveReportData into the specific MBFC prose format.
        """
        
        # Prepare context for the prompt
        context_str = data.model_dump_json()
        
        prompt = f"""
You are a senior editor for Media Bias/Fact Check (MBFC). Write a comprehensive report for the news outlet "{data.outlet_name}" based on the provided analysis data.

Use the exact structure and tone of MBFC reports. 

INPUT DATA:
{context_str}

STRUCTURE & REQUIREMENTS:

1. **Header**: The Bias Rating description block.
   - If bias is Left/Left-Center: "These sources are moderately to strongly biased toward liberal causes..."
   - If bias is Right/Right-Center: "These sources are moderately to strongly biased toward conservative causes..."
   - If Center: "These sources have minimal bias..."
   
2. **Overall Summary**: A bolded paragraph summarizing the rating.
   - Format: "Overall, we rate {data.outlet_name} [Bias Label]... We also rate them [Factuality Label]..."
   - Include the reasoning (e.g., "due to strong editorial positions on climate change" or "based on a clean fact check record").

3. **Detailed Report**: A list of metrics.
   - Bias Rating: {data.bias_label.upper()} ({data.bias_score})
   - Factual Reporting: {data.factuality_label.upper()} ({data.factuality_score})
   - Country: [Use Headquarters info]
   - Media Type: {data.media_type}
   - Traffic/Popularity: {data.traffic_tier}
   - Credibility Rating: {data.credibility_label.upper()}

4. **History**: 
   - Narrative paragraph about founding, ownership, and key milestones based on the history/ownership data provided.

5. **Funded by / Ownership**:
   - Who owns it? Where is it based? How is it funded? mention transparency.

6. **Analysis / Bias**:
   - This is the main body. Discuss the editorial stance.
   - Cite specific policy positions found in the data (e.g., "In reviewing articles, we found they support...").
   - Mention word choice/loaded language findings.
   - Mention external critiques found in the 'external_analyses' data.

7. **Failed Fact Checks**:
   - List them as bullet points if they exist in the data.
   - If none, state: "A search of IFCN fact checkers revealed no failed fact checks in the last 5 years."

TONE: Objective, professional, journalistic, but decisive about the bias rating.
        """

        messages = [
            {"role": "system", "content": "You are an expert media analyst writing a report for Media Bias/Fact Check."},
            {"role": "user", "content": prompt}
        ]

        response = self.llm.invoke(messages)
        return response.content