import json
from tooling.polygon_tool import PolygonAPITool
from langchain_openai import ChatOpenAI

# Initialize the PolygonAPITool
polygon_tool = PolygonAPITool()

def generate_detailed_report(stock_symbol):
    """Generate a detailed stock report."""
    
    # Get stock data from Polygon tool
    ticker_data = polygon_tool.get_stock_info(stock_symbol)
    
    if 'error' not in ticker_data:
        # Summarize the stock data using the LLM
        detailed_report = generate_report_using_llm(ticker_data)  # Now we call the generate_report_using_llm function
        return detailed_report  # Return the summary for use in Streamlit
    else:
        return ticker_data.get('error', 'Error fetching stock data.')

def generate_report_using_llm(ticker_data):
    """Generate a detailed stock report using the LLM."""
    # Log or print the ticker data structure to inspect it
    print(ticker_data)  # For debugging purposes (you can remove this later)

    json_string = json.dumps(ticker_data, indent=2)

    # Prepare the prompt
    stock_symbol = ticker_data.get('symbol', 'Unknown')  # Safely get 'symbol' from the data
    prompt = f"Here is the stock data for {stock_symbol}:\n\n{json_string}\n\nPlease provide a deep, detailed, and insightful report including an analysis of the company’s financial health, stock performance, market trends, and any relevant news or events."

    # Use the LLM for generating a detailed report
    llm = polygon_tool.llm  # We use the LLM from the PolygonAPITool instance
    
    if llm:
        # Call the LLM using the correct method for generating text
        summary_response = llm.predict(prompt)  # Use predict instead of call
        # Handle the response
        return summary_response if isinstance(summary_response, str) else "No summary available."
    else:
        return "LLM is not properly initialized."
