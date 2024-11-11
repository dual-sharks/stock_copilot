import requests
from sec_api import QueryApi
from langchain_openai import ChatOpenAI

class SECApiTool:
    def __init__(self):
        self.api_key = "polygonapi"  # Replace with your actual SEC API key
        self.query_api = QueryApi(api_key=self.api_key)
        self.llm = ChatOpenAI(model_name="gpt-4", temperature=0.7, api_key="openaiapi")

    def get_filing_data(self, ticker):
        """Fetch recent SEC filings for the given ticker symbol and provide summaries for each."""
        query = {
            "query": f"ticker:{ticker}",
            "from": "0",
            "size": "5",
            "sort": [{"filedAt": {"order": "desc"}}]
        }
        try:
            response = self.query_api.get_filings(query)
            if 'filings' in response:
                # For each filing, fetch and summarize its content
                summarized_filings = []
                for filing in response['filings']:
                    filing_url = filing.get('linkToFilingDetails', '#')
                    summary = self.download_and_summarize_filing(filing_url)
                    summarized_filings.append({
                        "url": filing_url,
                        "summary": summary
                    })
                return summarized_filings
            else:
                return {"error": "No filings found."}
        except Exception as e:
            return {"error": f"Failed to fetch SEC filings: {str(e)}"}

    def download_and_summarize_filing(self, filing_url):
        """Download and summarize the content of a specific filing."""
        try:
            # Adding additional headers to mimic a browser request
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Connection': 'keep-alive'
            }
            response = requests.get(filing_url, headers=headers)
            if response.status_code == 200:
                content = response.text
                return self.summarize_filing_content(content)
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