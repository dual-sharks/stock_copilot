import requests
import os
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

# Define a schema for the tool's arguments
class PolygonAPIToolArgsSchema(BaseModel):
    symbol: str = Field(..., description="The stock ticker symbol to get information for.")

class PolygonAPITool:
    def __init__(self):
        self.api_key = os.getenv("POLYGON_API_KEY")
        self.llm = ChatOpenAI(model_name="gpt-4o", temperature=0.7, api_key=os.getenv("OPENAI_API_KEY"))
        self.name = "PolygonAPITool"
        self.args_schema = PolygonAPIToolArgsSchema  # Define the args_schema attribute
        self.description = 'Gets data from polygon'

    def get_options_data(self, symbol, expiration_date, option_type, strike_price):
        """Fetch options data based on the provided details."""
        # Format the strike price to match API requirements (multiply by 1000)
        formatted_strike = f"{int(strike_price*1000):08d}"
        
        # Create the options symbol in the format O:TSLA230113C00015000
        option_symbol = f"O:{symbol}{expiration_date}{option_type}{formatted_strike}"
        
        # Calculate date range (let's get last 30 days of data up to expiration)
        end_date = expiration_date
        # Convert expiration_date string to datetime and subtract 30 days
        from datetime import datetime, timedelta
        end_date_obj = datetime.strptime(expiration_date, "%y%m%d")
        start_date_obj = end_date_obj - timedelta(days=30)
        start_date = start_date_obj.strftime("%Y-%m-%d")
        end_date = end_date_obj.strftime("%Y-%m-%d")
        
        url = f"https://api.polygon.io/v2/aggs/ticker/{option_symbol}/range/1/day/{start_date}/{end_date}?apiKey={self.api_key}"
        
        try:
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                data['option_details'] = {
                    'symbol': symbol,
                    'expiration': expiration_date,
                    'type': 'Call' if option_type == 'C' else 'Put',
                    'strike_price': strike_price,
                    'option_symbol': option_symbol
                }
                return data
            else:
                return {"error": f"Failed to fetch options data: {response.status_code}"}
        except Exception as e:
            return {"error": f"Error fetching options data: {str(e)}"}

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