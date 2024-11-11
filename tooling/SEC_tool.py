import requests
from sec_api import QueryApi
from langchain_openai import ChatOpenAI
import re

class SECApiTool:
    def __init__(self):
        self.api_key = "POLYGONAPIKEY"  # Replace with your actual SEC API key
        self.query_api = QueryApi(api_key=self.api_key)
        self.llm = ChatOpenAI(model_name="gpt-4", temperature=0.7, api_key="OPENAIAPKIKEY")

    def get_filing_data(self, ticker):
        """Fetch recent SEC filings and provide a summary using JSON metadata instead of full content."""
        query = {
            "query": f"ticker:{ticker}",
            "from": "0",
            "size": "5",
            "sort": [{"filedAt": {"order": "desc"}}]
        }
        try:
            response = self.query_api.get_filings(query)
            if 'filings' not in response:
                return {"error": "No filings found for this ticker symbol."}

            filings_summary = []
            for filing in response['filings']:
                filing_url = filing.get('linkToFilingDetails')
                filing_type = filing.get('formType', 'N/A')
                filed_date = filing.get('filedAt', 'N/A')
                description = filing.get('description', 'No description available.')

                # Combine metadata into a summary prompt
                metadata_summary = f"Form Type: {filing_type}, Filed Date: {filed_date}\nDescription: {description}"
                brief_summary = self.summarize_filing_metadata(metadata_summary)
                
                filings_summary.append({
                    "url": filing_url,
                    "summary": brief_summary
                })
                
            return filings_summary

        except Exception as e:
            return {"error": f"Failed to fetch SEC filings: {str(e)}"}

    def summarize_filing_metadata(self, metadata_summary):
        """Use the LLM to generate a concise summary of filing metadata."""
        summary_prompt = (
            f"Summarize the following SEC filing metadata concisely:\n\n{metadata_summary}\n\n"
            "Provide a brief summary of the main points."
        )
        try:
            summary = self.llm(summary_prompt)
            return summary.content if hasattr(summary, 'content') else str(summary)
        except Exception as e:
            return f"Error summarizing filing metadata: {str(e)}"