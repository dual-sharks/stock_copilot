import requests
import os
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

# Define a schema for the tool's arguments
class PolygonAPIToolArgsSchema(BaseModel):
    symbol: str = Field(..., description="The stock ticker symbol to get information for.")

class PolygonAPITool:
    def __init__(self):
        self.api_key = "polygonapi"
        self.llm = ChatOpenAI(model_name="gpt-4", temperature=0.7)
        self.name = "PolygonAPITool"
        self.args_schema = PolygonAPIToolArgsSchema  # Define the args_schema attribute
        self.description = 'Gets data from polygon'

    def get_stock_info(self, symbol):
        """Fetch stock data for the given symbol."""
        url = f"https://api.polygon.io/v3/reference/tickers/{symbol}?apiKey={self.api_key}"
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()  # You might need to format this based on API structure
        else:
            return {"error": f"Failed to fetch data: {response.status_code}"}
        
    def get_market_news(self, ticker, limit=5):
        """Fetch market news for the given ticker."""
        url = f"https://api.polygon.io/v2/reference/news?ticker={ticker}&limit={limit}&apiKey={self.api_key}"
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"Failed to fetch news: {response.status_code} - {response.reason}"}
        
    def analyze_market_trends(self, ticker):
        """Fetch top news articles and perform sentiment analysis."""
        news_data = self.get_market_news(ticker)
        if 'error' not in news_data:
            articles = news_data.get("results", [])[:5]  # Get the top 5 articles
            summary = "Here are the top 5 articles:\n\n"
            sources = "\nTo read the documents themselves, go to these links:\n"

            for idx, article in enumerate(articles):
                summary += f"**{idx + 1}. Title**: {article['title']}\n"
                summary += f"**Published**: {article['published_utc']}\n"
                summary += f"**Summary**: {article['description']}\n\n"
                sources += f"{idx + 1}. [Read more]({article['article_url']})\n"

            # Use LLM for sentiment analysis
            sentiment_prompt = (
                f"Perform a sentiment analysis and market trend summary for the following news articles:\n\n{summary}\n"
                "Provide a summary of the overall market sentiment and key trends."
            )
            sentiment_response = self.llm(sentiment_prompt)

            # Extract the plain content if response is complex
            if hasattr(sentiment_response, 'content'):
                sentiment_analysis = sentiment_response.content
            else:
                sentiment_analysis = str(sentiment_response)

            return sentiment_analysis + "\n\n" + sources
        else:
            return news_data['error']
        

    def __call__(self, symbol):
        """Make the tool callable, so it can be used directly by the agent."""
        return self.get_stock_info(symbol)
    

class SECApiTool:
    def __init__(self):
        self.base_url = "https://api.sec-api.io"  # SEC-API endpoint
        self.api_key = "50ccec65f402053834331285c5702a5bdd3febeb66c8e25ce34b51259b5b735f"

    def get_filing_data(self, ticker):
        """Fetch recent SEC filings for the given ticker symbol."""
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'User-Agent': 'StockPilot kerim.tricic@cloudelligent.com',
        }

        # Define the payload for the SEC-API endpoint
        params = {
            "query": {
                "query_string": {
                    "query": f"ticker:{ticker}",
                    "size": 10,  # Adjust as needed for more or fewer results
                    "sort": [{"filedAt": "desc"}]  # Sort by filing date
                }
            }
        }

        response = requests.post(f"{self.base_url}/filings", json=params, headers=headers)

        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"Failed to fetch data: {response.status_code} - {response.reason}"}