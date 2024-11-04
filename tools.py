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
