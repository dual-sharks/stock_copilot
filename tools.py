import requests
import os
from pydantic import BaseModel, Field

# Define a schema for the tool's arguments
class PolygonAPIToolArgsSchema(BaseModel):
    symbol: str = Field(..., description="The stock ticker symbol to get information for.")

class PolygonAPITool:
    def __init__(self):
        self.api_key = "BTZo73LLIZlgL0yOWLQbvGlQOoMpW3Un"
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