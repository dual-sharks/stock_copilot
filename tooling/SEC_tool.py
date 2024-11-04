import requests
from sec_api import QueryApi
from langchain_openai import ChatOpenAI

class SECApiTool:
    def __init__(self):
        self.api_key = "50ccec65f402053834331285c5702a5bdd3febeb66c8e25ce34b51259b5b735f"  # Replace with your actual SEC API key
        self.query_api = QueryApi(api_key=self.api_key)
        self.llm = ChatOpenAI(model_name="gpt-4", temperature=0.7)

    def get_filing_data(self, ticker):
        """Fetch recent SEC filings for the given ticker symbol."""
        query = {
            "query": f"ticker:{ticker}",
            "from": "0",
            "size": "5",  # Adjust as needed for more or fewer results
            "sort": [{"filedAt": {"order": "desc"}}]
        }
        try:
            response = self.query_api.get_filings(query)
            return response  # The response should already be parsed JSON
        except Exception as e:
            return {"error": f"Failed to fetch SEC filings: {str(e)}"}

    def download_filing_content(self, filing_url):
        """Download the content of the filing for summarization."""
        try:
            response = requests.get(
                filing_url,
                headers={'User-Agent': 'Mozilla/5.0'}
            )
            if response.status_code == 200:
                return response.text
            else:
                return f"Failed to fetch filing content: {response.status_code} - {response.reason}"
        except Exception as e:
            return f"Error fetching filing content: {str(e)}"

    def summarize_filing_content(self, content):
        """Summarize the content of the filing using LLM."""
        summary_prompt = (
            f"Summarize the following SEC filing content:\n\n{content[:3000]}\n\n"
            "Provide a concise summary highlighting the main points."
        )
        try:
            summary = self.llm(summary_prompt)
            return summary.content if hasattr(summary, 'content') else str(summary)
        except Exception as e:
            return f"Error summarizing filing content: {str(e)}"
