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